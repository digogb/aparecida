"""
DJESearchClient — cliente HTTP reutilizável para a API DJEN.

API base: https://comunicaapi.pje.jus.br/api/v1/comunicacao

Uso básico::

    from dje_search import DJESearchClient, DJESearchParams
    from datetime import date

    client = DJESearchClient()

    # Busca por nome da parte
    resultados = client.buscar(DJESearchParams(nome_parte="MARIA SILVA"))

    # Busca por advogado
    resultados = client.buscar(DJESearchParams(
        nome_advogado="JOSE ANTONIO SOUZA",
        sigla_tribunal="TJCE",
    ))

    # Busca por OAB com filtro de data
    resultados = client.buscar(DJESearchParams(
        numero_oab="12345/CE",
        data_inicio=date(2025, 1, 1),
        data_fim=date(2025, 3, 31),
    ))

    # Busca por CPF/CNPJ
    resultados = client.buscar(DJESearchParams(cpf_cnpj="12345678901"))

    # Busca por número de processo
    resultados = client.buscar(DJESearchParams(
        numero_processo="0001234-56.2024.8.06.0001"
    ))
"""

import logging
import re
import time
from datetime import date
from typing import Optional

import httpx

from .models import DJEAdvogado, DJEComunicacao, DJEPolo, DJESearchParams
from .utils import (
    create_legacy_ssl_context,
    extrair_numero_processo,
    extrair_polos_do_texto,
    limpar_html,
    normalizar_nome,
)

logger = logging.getLogger(__name__)

_API_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class DJESearchClient:
    """
    Cliente para a API pública do DJEN (comunica.pje.jus.br).

    Thread-safe para uso em aplicações multi-tenant: instancie um objeto por
    contexto de execução ou compartilhe apenas se o delay/retry for aceitável.

    :param timeout:     Timeout HTTP em segundos (padrão: 60).
    :param delay:       Intervalo mínimo entre requisições em segundos (padrão: 1.5).
    :param max_retries: Número de tentativas em caso de falha de rede (padrão: 3).
    """

    def __init__(
        self,
        timeout: int = 60,
        delay: float = 1.5,
        max_retries: int = 3,
    ) -> None:
        self.delay = delay
        self.max_retries = max_retries
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            verify=create_legacy_ssl_context(),
            headers=_DEFAULT_HEADERS,
        )

    def __del__(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Interface pública
    # ------------------------------------------------------------------

    def buscar(self, params: DJESearchParams) -> list[DJEComunicacao]:
        """
        Executa busca na API DJEN com os parâmetros fornecidos.

        Realiza paginação automática até ``params.max_paginas`` e deduplica
        resultados por (numero_processo, data_disponibilizacao).

        :param params: Parâmetros de busca. Ver :class:`DJESearchParams`.
        :returns:      Lista de comunicações normalizadas.
        :raises ValueError: Se nenhum critério de busca for informado.
        """
        params.validar()
        query = self._build_query(params)
        raw = self._paginar(query, params.max_paginas, params)
        return self._deduplicar(raw)

    # ------------------------------------------------------------------
    # Construção da query
    # ------------------------------------------------------------------

    def _build_query(self, params: DJESearchParams) -> dict:
        """Converte DJESearchParams nos parâmetros aceitos pela API."""
        q: dict = {"itensPorPagina": params.itens_por_pagina, "pagina": 1}

        if params.nome_parte:
            q["nomeParte"] = params.nome_parte
        if params.numero_processo:
            q["numeroProcesso"] = params.numero_processo
        if params.cpf_cnpj:
            q["cpfCnpj"] = re.sub(r"\D", "", params.cpf_cnpj)
        if params.nome_advogado:
            q["nomeAdvogado"] = params.nome_advogado
        if params.numero_oab:
            oab_parts = params.numero_oab.strip().split("/")
            q["numeroOab"] = oab_parts[0].strip()
            if len(oab_parts) > 1:
                q["ufOab"] = oab_parts[1].strip().upper()
        if params.sigla_tribunal:
            q["siglaTribunal"] = params.sigla_tribunal
        if params.tipo_comunicacao:
            q["tipoComunicacao"] = params.tipo_comunicacao
        if params.data_inicio:
            q["dataDisponibilizacaoInicio"] = params.data_inicio.isoformat()
        if params.data_fim:
            q["dataDisponibilizacaoFim"] = params.data_fim.isoformat()

        return q

    # ------------------------------------------------------------------
    # Paginação
    # ------------------------------------------------------------------

    def _paginar(
        self,
        query: dict,
        max_paginas: int,
        params: DJESearchParams,
    ) -> list[DJEComunicacao]:
        resultados: list[DJEComunicacao] = []
        itens_por_pagina = query.get("itensPorPagina", 100)

        while True:
            logger.info("DJEN busca — página %d", query["pagina"])
            response = self._requisicao("GET", _API_URL, params=query)

            if response is None or response.status_code != 200:
                status = response.status_code if response else "None"
                logger.warning("Interrompendo paginação: status %s", status)
                break

            content_type = response.headers.get("content-type", "")
            if "html" in content_type:
                logger.warning("API retornou HTML em vez de JSON — abortando")
                break

            data = response.json()
            items = data.get("items", data) if isinstance(data, dict) else data

            if not isinstance(items, list) or not items:
                break

            novos = self._parse_items(items, params)
            resultados.extend(novos)

            if len(novos) < itens_por_pagina:
                break

            query["pagina"] += 1
            if query["pagina"] > max_paginas:
                logger.warning("Limite de %d páginas atingido", max_paginas)
                break

        return resultados

    # ------------------------------------------------------------------
    # Parsing de itens
    # ------------------------------------------------------------------

    def _parse_items(
        self,
        items: list,
        params: DJESearchParams,
    ) -> list[DJEComunicacao]:
        resultados = []
        termo_norm = normalizar_nome(params.nome_parte or "")

        for item in items:
            try:
                destinatarios = item.get("destinatarios", [])

                # Filtro por nome de destinatário — só quando a busca é por nomeParte
                if params.filtrar_por_destinatario:
                    if not any(
                        normalizar_nome(d.get("nome", "")) == termo_norm
                        for d in destinatarios
                    ):
                        continue

                comunicacao = self._parse_item(item, params)

                # Filtro de data client-side — garante o intervalo mesmo se a API ignorar
                if params.data_inicio or params.data_fim:
                    raw_data = (
                        comunicacao.data_disponibilizacao
                        or item.get("datadisponibilizacao")
                        or item.get("dataDisponibilizacao")
                        or ""
                    )
                    pub_date = self._parse_date_to_date(raw_data)
                    if pub_date:
                        if params.data_inicio and pub_date < params.data_inicio:
                            continue
                        if params.data_fim and pub_date > params.data_fim:
                            continue

                resultados.append(comunicacao)
            except Exception as exc:
                logger.error("Erro ao parsear item DJEN: %s", exc)

        return resultados

    @staticmethod
    def _parse_date_to_date(raw: str) -> "date | None":
        """Converte string de data do DJE para date (DD/MM/YYYY ou YYYY-MM-DD)."""
        if not raw:
            return None
        raw = raw.strip().split("T")[0]
        parts = raw.split("/")
        try:
            if len(parts) == 3:
                return date(int(parts[2]), int(parts[1]), int(parts[0]))
            return date.fromisoformat(raw)
        except (ValueError, IndexError):
            return None

    def _parse_item(self, item: dict, params: DJESearchParams) -> DJEComunicacao:
        """Converte um item bruto da API em DJEComunicacao."""
        texto = limpar_html(item.get("texto") or item.get("conteudo") or "")

        processo = (
            item.get("numeroprocessocommascara")
            or item.get("numeroProcesso")
            or item.get("numero_processo")
            or extrair_numero_processo(texto)
        )

        data_disp = (
            item.get("datadisponibilizacao")
            or item.get("dataDisponibilizacao")
            or item.get("data_disponibilizacao")
            or ""
        )

        orgao = (
            item.get("nomeOrgao")
            or item.get("siglaTribunal", "")
        )

        polos = self._extrair_polos(item, texto)

        termo_buscado = (
            params.nome_parte
            or params.numero_processo
            or params.cpf_cnpj
            or params.nome_advogado
            or params.numero_oab
            or ""
        )

        advogados = []
        for da in item.get("destinatarioadvogados", []):
            adv = da.get("advogado", {})
            advogados.append(DJEAdvogado(
                id=adv.get("id", 0),
                nome=adv.get("nome", ""),
                numero_oab=adv.get("numero_oab", ""),
                uf_oab=adv.get("uf_oab", ""),
            ))

        return DJEComunicacao(
            id=str(item.get("id", "")),
            tribunal=item.get("siglaTribunal", ""),
            numero_processo=processo or "",
            data_disponibilizacao=data_disp,
            orgao=orgao,
            id_orgao=item.get("idOrgao", 0),
            tipo_comunicacao=item.get("tipoComunicacao", ""),
            texto=texto,
            link=item.get("link", ""),
            meio=item.get("meio", ""),
            meio_completo=item.get("meiocompleto", ""),
            tipo_documento=item.get("tipoDocumento", ""),
            nome_classe=item.get("nomeClasse", ""),
            codigo_classe=str(item.get("codigoClasse", "")),
            numero_comunicacao=item.get("numeroComunicacao", 0),
            ativo=item.get("ativo", True),
            hash=item.get("hash", ""),
            status=item.get("status", ""),
            motivo_cancelamento=item.get("motivo_cancelamento"),
            data_cancelamento=item.get("data_cancelamento"),
            termo_buscado=termo_buscado,
            polos=polos,
            destinatarios=[d.get("nome", "") for d in item.get("destinatarios", [])],
            advogados=advogados,
            raw_data=item,
        )

    def _extrair_polos(self, item: dict, texto: str) -> DJEPolo:
        """
        Extrai polos ativo/passivo dos dados estruturados da API.
        Fallback para extração via regex no texto quando a API não retorna dados.
        """
        polo = DJEPolo()

        for dest in item.get("destinatarios", []):
            nome = dest.get("nome", "").strip()
            if not nome:
                continue
            tipo = str(dest.get("polo", "")).upper()
            if tipo in ("A",) or "ATIVO" in tipo or "AUTOR" in tipo:
                polo.ativo.append(nome)
            elif tipo in ("P",) or "PASSIVO" in tipo or "REU" in tipo or "RÉU" in tipo:
                polo.passivo.append(nome)
            else:
                polo.outros.append(nome)

        if not polo.ativo and not polo.passivo and texto:
            raw = extrair_polos_do_texto(texto)
            polo.ativo = raw.get("ativo", [])
            polo.passivo = raw.get("passivo", [])
            polo.outros = raw.get("outros", [])

        return polo

    # ------------------------------------------------------------------
    # Deduplicação
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicar(comunicacoes: list[DJEComunicacao]) -> list[DJEComunicacao]:
        """
        Remove duplicatas pelo id da comunicação.

        Cada comunicação tem um id único na API — é o mesmo campo usado como
        dje_id no banco. A deduplicação definitiva acontece no banco via
        ON CONFLICT DO NOTHING; aqui apenas evitamos processar o mesmo id
        duas vezes na mesma paginação.
        """
        vistos: set[str] = set()
        resultado: list[DJEComunicacao] = []
        for c in comunicacoes:
            if c.id and c.id not in vistos:
                vistos.add(c.id)
                resultado.append(c)
        return resultado

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _requisicao(
        self, method: str, url: str, **kwargs
    ) -> Optional[httpx.Response]:
        """Executa requisição com retry e backoff exponencial."""
        for tentativa in range(self.max_retries):
            try:
                time.sleep(self.delay)
                response = self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "HTTP %s em %s (tentativa %d/%d)",
                    exc.response.status_code, url,
                    tentativa + 1, self.max_retries,
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "Erro de rede em %s: %s (tentativa %d/%d)",
                    url, exc,
                    tentativa + 1, self.max_retries,
                )

            if tentativa < self.max_retries - 1:
                time.sleep(2 ** (tentativa + 1))

        logger.error("Falha após %d tentativas: %s", self.max_retries, url)
        return None
