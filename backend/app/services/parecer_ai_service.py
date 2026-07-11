"""
T2 — Serviço de IA para Pareceres
Orquestra as 3 chamadas ao Claude API (P1, P2, P3) do pipeline v4.1.

Estratégia de tokens:
- P1 usa Haiku (classificação simples, TPM separado, 20x mais barato)
- P2/P3 usam Sonnet (geração complexa que exige qualidade)
- Conteúdo do usuário é truncado a MAX_USER_CONTENT_CHARS antes do envio
- Retry com backoff alinhado ao limite por minuto (60s/120s/180s)
- Semáforo serializa chamadas ao Sonnet (30k TPM = 1 parecer por vez)
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from anthropic import AsyncAnthropic, RateLimitError

from app.config import settings
from app.services.extractor import resumo_financeiro_canonico
from app.services.prompt_safety import wrap_documents
from app.services.prompt_service import (
    assemble_p2_context,
    assemble_p3_context,
    build_p2_prompt,
    get_prompt_version,
    load_prompt,
    resolve_vertente,
)
from app.services.leis_municipios import assemble_municipal_context
from app.services.parecer_html_service import parse_parecer_xml

logger = logging.getLogger(__name__)

# Modelos por etapa
MODEL_P1 = "claude-haiku-4-5-20251001"   # classificação: rápido, barato, TPM separado
MODEL_P2_P3 = "claude-sonnet-5"  # geração/revisão: Sonnet 5 (1M ctx, sucessor do 4.6)

# Fallback de geração/revisão quando o modelo primário RECUSA (stop_reason=refusal).
# O Sonnet 5 às vezes recusa (falso-positivo de segurança) conteúdo legítimo — visto em
# prod no PAR-2026-0056 (habilitação/notas fiscais de uma inexigibilidade). A recusa é
# determinística pelo conteúdo, então retry no mesmo modelo recusaria de novo; o Sonnet 4.6
# (modelo anterior de prod) gera o MESMO conteúdo sem recusar e aceita os mesmos params.
MODEL_P2_FALLBACK = "claude-sonnet-4-6"


class ModelRefusalError(Exception):
    """O modelo recusou a geração (stop_reason=refusal) — resposta vazia."""

# Rede de segurança das chamadas HAIKU (P1 classificação, P1.5 valores).
# LIMITE OBRIGATÓRIO: Haiku 4.5 tem janela de 200k TOKENS — e os anexos são densos
# (~1,9-2,0 chars/token nas planilhas de preço), então 300k chars ≈ ~155k tokens;
# com system (~5k) + output (2k) fica seguro sob 200k. NÃO remover: um único anexo
# real (ex. pesquisa de preços = 566k chars ≈ 294k tokens) já estoura a janela do
# Haiku — sem cap o classify daria 400 e travaria o pipeline no gate. Não custa
# assertividade: o P0 prefilter põe a consulta primeiro (corta a cauda de
# referência) e o resumo_financeiro_canonico sobe o "VALOR TOTAL" antes do corte.
MAX_USER_CONTENT_CHARS = 300_000

# Cap do user_message do P2 (Sonnet = janela de 1M tokens). "Sem limite prático":
# nenhuma consulta real encosta (maior anexo único visto = 566k chars). Serve só
# de trava anti-400 contra estourar 1M. Pior caso denso: 1,5M chars / ~1,9 ≈ 790k
# tokens + system (~77k) + output (8k) ≈ 875k < 1M. Tier da conta = 10M ITPM.
MAX_P2_USER_CONTENT_CHARS = 1_500_000

# Orçamento water-filling da seção "## DOCUMENTOS ANEXOS" do P2 — NENHUM anexo é
# descartado inteiro. Fica abaixo do cap total p/ sobrar espaço p/ classificação +
# email + bloco de valores. Alto o bastante p/ caber conjuntos documentais completos.
MAX_DOCS_CHARS = 1_300_000

# Retry config — alinhado com o limite de 30k tokens/min
MAX_RETRIES = 3
BACKOFF_SECS = [60, 120, 180]

AI_CALLS_LOG = Path("/app/logs/ai_calls.jsonl")


def _log_api_call(
    stage: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    raw_response: str,
    tool_calls: list[dict] | None = None,
) -> None:
    """Append one record per API call to ai_calls.jsonl.

    `tool_calls` (Camada 6): lista de {tool_name, query, result_summary} para cada
    invocação de server tool (web_search). None ou [] quando tools não foi usado.
    """
    AI_CALLS_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "raw_response": raw_response,
        "tool_calls_count": len(tool_calls or []),
        "tool_calls": tool_calls or [],
    }
    with AI_CALLS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# Semáforo: serializa chamadas ao Sonnet.
# Com 30k TPM, um único parecer pode consumir o limite inteiro.
# Sem isso, 2+ requests simultâneos vão ambos receber 429.
_sonnet_semaphore = asyncio.Semaphore(1)


def _truncate(text: str, max_chars: int) -> str:
    """Trunca texto preservando palavras completas, adicionando aviso se cortou."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rsplit(" ", 1)[0]
    return truncated + "\n\n[... conteúdo truncado por limite de tokens ...]"


def _budget_documents(
    documents: list[tuple[str, str]], total_budget: int
) -> list[tuple[str, str]]:
    """Distribui `total_budget` caracteres entre os anexos (water-filling).

    Garante que NENHUM anexo seja descartado inteiro: processa do menor para o
    maior, dando a cada um sua cota (orçamento_restante / docs_restantes); anexos
    menores que a cota usam só o que precisam e devolvem a sobra para os maiores.
    Anexos truncados recebem um aviso explícito no fim do trecho.

    Retorna lista de (filename, texto_possivelmente_truncado) na ordem original.
    """
    n = len(documents)
    if n == 0:
        return []

    takes: dict[int, int] = {}
    remaining = total_budget
    count = n
    # Menores primeiro: liberam sobra para os maiores.
    for idx in sorted(range(n), key=lambda i: len(documents[i][1])):
        share = remaining // count if count else 0
        take = min(len(documents[idx][1]), share)
        takes[idx] = take
        remaining -= take
        count -= 1

    result: list[tuple[str, str]] = []
    for idx, (name, text) in enumerate(documents):
        take = takes[idx]
        if take >= len(text):
            result.append((name, text))
        else:
            cortado = text[:take].rsplit(" ", 1)[0]
            result.append(
                (name, cortado + "\n\n[... trecho deste anexo truncado por limite ...]")
            )
    return result


def _extract_text_and_tool_calls(response) -> tuple[str, list[dict]]:
    """Extrai o texto final + metadata de cada uso de server tool da resposta.

    Quando `tools=` é passado a Anthropic devolve `response.content` como lista
    de blocos de tipos `text`, `server_tool_use`, `web_search_tool_result` etc.
    Esta função:
    - concatena todos os blocos `text`
    - coleta {tool_name, query, result_summary} para cada `server_tool_use`
    """
    text_parts: list[str] = []
    tool_calls: list[dict] = []
    pending_queries: dict[str, dict] = {}

    for block in getattr(response, "content", []) or []:
        btype = getattr(block, "type", None)
        if btype == "text":
            text_parts.append(getattr(block, "text", "") or "")
        elif btype == "server_tool_use":
            tool_id = getattr(block, "id", "") or ""
            tool_name = getattr(block, "name", "") or "unknown"
            tool_input = getattr(block, "input", {}) or {}
            query = tool_input.get("query", "") if isinstance(tool_input, dict) else ""
            pending_queries[tool_id] = {
                "tool_name": tool_name,
                "query": query,
            }
        elif btype == "web_search_tool_result":
            tool_use_id = getattr(block, "tool_use_id", "") or ""
            content = getattr(block, "content", None)
            # Conta resultados (heurística — content é lista de páginas)
            n_results = len(content) if isinstance(content, list) else (0 if content is None else 1)
            meta = pending_queries.pop(tool_use_id, {"tool_name": "web_search", "query": ""})
            tool_calls.append({**meta, "result_summary": f"{n_results} result(s)"})

    # Queries sem result_block (ex: erro) ainda contam.
    for meta in pending_queries.values():
        tool_calls.append({**meta, "result_summary": "no_result_block"})

    return "".join(text_parts), tool_calls


async def _call_api(
    model: str,
    system: str,
    user_message: str,
    max_tokens: int,
    stage: str = "?",
    *,
    web_search_max_uses: int = 0,
) -> str:
    """
    Chama a API do Claude com retry automático em caso de rate limit.
    Backoff: 60s, 120s, 180s — alinhado com o reset do limite por minuto.

    `web_search_max_uses` > 0 (Camada 6) habilita o server tool `web_search_20250305`
    com o orçamento informado. Quando 0, a chamada é puramente texto (comportamento
    histórico). Os usos do tool são logados em ai_calls.jsonl.
    """
    tools_kwargs: dict = {}
    if web_search_max_uses > 0 and settings.WEB_SEARCH_ENABLED:
        tools_kwargs["tools"] = [
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": web_search_max_uses,
            }
        ]

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            # `temperature` só nos modelos que ainda aceitam sampling (Haiku 4.5,
            # usado em P1/P1.5). Sonnet 5 e a família 5 / Opus 4.7+ removeram
            # temperature/top_p/top_k e retornam 400 se enviados.
            #
            # Nos modelos Sonnet 5 (P2/P3) o thinking vem LIGADO por padrão e o
            # web_search induz thinking interleaved; esses blocos consomem o
            # orçamento de max_tokens ANTES de o bloco `text` do parecer sair —
            # produzindo parecer vazio (stop_reason=max_tokens, só `thinking`).
            # Desligamos o thinking para reproduzir o comportamento do Sonnet 4.6:
            # todo o max_tokens vira texto do parecer.
            if "haiku" in model:
                sampling_kwargs: dict = {"temperature": 0}
            else:
                sampling_kwargs = {"thinking": {"type": "disabled"}}
            async with AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) as client:
                response = await client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": user_message}],
                    **sampling_kwargs,
                    **tools_kwargs,
                )
            usage = response.usage
            # Recusa do modelo (stop_reason=refusal): resposta sem blocos de texto —
            # não deixar virar parecer "gerado" em branco. Levanta p/ o chamador
            # decidir (fallback de modelo em P2/P3; erro no pipeline se persistir).
            if response.stop_reason == "refusal":
                logger.warning(
                    "REFUSAL [%s/%s] input=%d output=%d — modelo recusou a geração",
                    stage, model, usage.input_tokens, usage.output_tokens,
                )
                _log_api_call(stage, model, usage.input_tokens, usage.output_tokens, "", tool_calls=[])
                raise ModelRefusalError(
                    f"{model} recusou a geração (stop_reason=refusal) na etapa {stage}"
                )
            if tools_kwargs:
                raw_text, tool_calls = _extract_text_and_tool_calls(response)
            else:
                raw_text = response.content[0].text
                tool_calls = []
            logger.warning(
                "TOKENS [%s/%s] input=%d output=%d total=%d tool_calls=%d",
                stage, model,
                usage.input_tokens,
                usage.output_tokens,
                usage.input_tokens + usage.output_tokens,
                len(tool_calls),
            )
            _log_api_call(
                stage, model,
                usage.input_tokens, usage.output_tokens,
                raw_text,
                tool_calls=tool_calls,
            )
            return raw_text
        except RateLimitError as e:
            last_error = e
            wait = BACKOFF_SECS[attempt]
            logger.warning(
                "Rate limit (tentativa %d/%d), aguardando %ds: %s",
                attempt + 1, MAX_RETRIES, wait, e,
            )
            await asyncio.sleep(wait)

    raise last_error  # type: ignore[misc]


async def _call_generation_with_fallback(
    system: str,
    user_message: str,
    max_tokens: int,
    stage: str,
    *,
    web_search_max_uses: int = 0,
) -> str:
    """Chama o modelo de geração/revisão (Sonnet 5) com fallback em caso de recusa.

    Se o Sonnet 5 recusar (ModelRefusalError), tenta uma vez com MODEL_P2_FALLBACK
    (Sonnet 4.6), que aceita os mesmos parâmetros e não recusa os casos vistos em
    prod. Se o fallback também recusar, propaga o erro — o pipeline marca status=erro
    (e o botão de reprocessar aparece), em vez de salvar um parecer em branco.
    """
    try:
        return await _call_api(
            MODEL_P2_P3, system, user_message, max_tokens, stage,
            web_search_max_uses=web_search_max_uses,
        )
    except ModelRefusalError:
        logger.warning(
            "%s: %s recusou — tentando fallback %s", stage, MODEL_P2_P3, MODEL_P2_FALLBACK,
        )
        return await _call_api(
            MODEL_P2_FALLBACK, system, user_message, max_tokens, f"{stage}-fallback",
            web_search_max_uses=web_search_max_uses,
        )


# ─── P0: PRÉ-FILTRO DE ANEXOS ───

_PREFILTER_SYSTEM = (
    "Você triagem anexos de emails para um escritório jurídico municipal. "
    "Receberá filenames + prévia curta de cada anexo. "
    "Sua tarefa: identificar a ORDEM DE RELEVÂNCIA — qual anexo contém a "
    "CONSULTA JURÍDICA (a pergunta ou pedido que o município está fazendo) "
    "vs. quais são DOCUMENTOS DE REFERÊNCIA (editais antigos, fichas funcionais, "
    "contratos, leis, ofícios já respondidos).\n\n"
    "Retorne EXCLUSIVAMENTE um JSON sem markdown:\n"
    '{"order": [idx_mais_relevante, ..., idx_menos_relevante]}\n\n'
    "A lista DEVE conter todos os índices recebidos, exatamente uma vez."
)


async def prefilter_attachments(
    subject: str,
    email_body: str,
    attachments: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Reordena anexos pondo a consulta primeiro e referências por último.

    Usa Haiku com prévia curta (filename + 400 chars) para decidir.
    Falha silenciosa: qualquer erro mantém a ordem original.

    P0 NÃO envolve os anexos em `<documento_anexo>`: recebe só um snippet curto
    para ordenar (não gera conteúdo do parecer) e devolve apenas uma permutação
    de índices — a fronteira de confiança é aplicada em P1/P1.5/P2, onde o texto
    de fato entra no prompt de geração/classificação.
    """
    if len(attachments) <= 1:
        return attachments

    lines = [
        f"Assunto: {subject or '(sem assunto)'}",
        f"Corpo do email (até 500 chars): {(email_body or '').replace(chr(10), ' ')[:500] or '(vazio)'}",
        "",
        "Anexos:",
    ]
    for i, (fn, text) in enumerate(attachments):
        snippet = (text or "").replace("\n", " ")[:400]
        lines.append(f"[{i}] {fn} ({len(text or '')} chars) — {snippet}")
    user_message = "\n".join(lines)

    try:
        raw = await _call_api(
            model=MODEL_P1,
            system=_PREFILTER_SYSTEM,
            user_message=user_message,
            max_tokens=300,
            stage="P0-prefilter",
        )
    except Exception as exc:
        logger.warning("P0 prefilter API falhou (%s), mantendo ordem original", exc)
        return attachments

    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
        order = data["order"]
    except (json.JSONDecodeError, KeyError, TypeError):
        logger.warning("P0 prefilter JSON inválido: %r — mantendo ordem original", raw[:200])
        return attachments

    n = len(attachments)
    if not isinstance(order, list) or sorted(order) != list(range(n)):
        logger.warning("P0 prefilter ordem inválida %s (n=%d) — mantendo ordem original", order, n)
        return attachments

    logger.info("P0 prefilter reordenou anexos: %s", order)
    return [attachments[i] for i in order]


# ─── P1: CLASSIFICAÇÃO ───

_VALID_VERTENTES = {
    "licitacao_14133",
    "administrativo",
    "tributario_financeiro",
    "terceiro_setor",
}
_VALID_MODOS = {"consultivo_puro", "quase_processual"}
_VALID_TIPOS_PARECER = {"preventivo", "corretivo", "contencioso"}
_VALID_URGENCIAS = {"normal", "alta", "critica"}
_VALID_CONFIANCAS = {"alta", "media", "baixa"}


def _normalize_classification(raw: dict, email_body: str) -> dict:
    """Normaliza o JSON do P1 v5.0 para o schema esperado pelo restante do pipeline.

    Garante a presença de todos os campos obrigatórios com valores válidos. Quando o P1
    retorna JSON parcial ou com valores inesperados, aplica defaults conservadores.
    """
    cls: dict = dict(raw or {})

    # Campos string
    cls.setdefault("is_consulta_juridica", True)
    cls.setdefault("municipio", "")
    cls.setdefault("uf", "")
    cls.setdefault("orgao_consulente", "")
    cls.setdefault("consulente", "")
    cls.setdefault("assunto_resumido", "")
    cls.setdefault("motivo_nao_juridica", None)
    cls.setdefault("fatos_extraidos", "")
    cls.setdefault("duvida_central", email_body[:500] if email_body else "")

    # Campos enumerados — validar e cair para default conservador
    if cls.get("vertente") not in _VALID_VERTENTES:
        cls["vertente"] = "administrativo"
    if cls.get("modo") not in _VALID_MODOS:
        cls["modo"] = "consultivo_puro"
    if cls.get("tipo_parecer") not in _VALID_TIPOS_PARECER:
        cls["tipo_parecer"] = "preventivo"
    if cls.get("urgencia") not in _VALID_URGENCIAS:
        cls["urgencia"] = "normal"
    if cls.get("confianca_classificacao") not in _VALID_CONFIANCAS:
        cls["confianca_classificacao"] = "baixa"

    # Subtipo é livre dentro da vertente (lista evoluiu nas skills). Garantir string.
    cls.setdefault("subtipo", "")
    if not isinstance(cls["subtipo"], str):
        cls["subtipo"] = ""

    # Listas
    for key in ("caso_integrado", "documentos_mencionados", "lacuna_normativa_local", "documentos_faltantes"):
        val = cls.get(key)
        if not isinstance(val, list):
            cls[key] = []
        else:
            cls[key] = [str(x) for x in val if x]

    return cls


async def classify_email(
    email_body: str,
    attachments: list[tuple[str, str]],
    subject: str = "",
) -> dict:
    """Chama P1 (Haiku) para classificar o email.

    `attachments` é uma lista de (filename, texto_extraído). Quando há 2+ anexos,
    chama P0-prefilter antes para reordenar (consulta primeiro, referências depois).
    Cada anexo é rotulado com seu filename no user_message para o P1 distinguir.

    Retorna dicionário no schema P1 v5.0 (com `vertente`, `subtipo`, `modo`,
    `lacuna_normativa_local`, `documentos_faltantes`). Campos faltantes ou inválidos são
    saneados por `_normalize_classification`.
    """
    ordered = await prefilter_attachments(subject, email_body, attachments)

    user_message = email_body
    if ordered:
        # Fronteira de confiança: anexos vão envoltos em `<documento_anexo>`
        # (conteúdo é dado a classificar, não instrução). Ver p1_classification.txt.
        user_message += "\n\n---\n\n" + wrap_documents(ordered)
    user_message = _truncate(user_message, MAX_USER_CONTENT_CHARS)

    raw = await _call_api(
        model=MODEL_P1,
        system=load_prompt("p1_classification"),
        user_message=user_message,
        max_tokens=2000,
        stage="P1",
    )

    raw = raw.strip()

    # Strip markdown fences se presentes
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("P1 JSON inválido, retornando classificação com confiança baixa")
        parsed = {}

    classification = _normalize_classification(parsed, email_body)
    logger.info(
        "P1 classificou: vertente=%s subtipo=%s modo=%s confianca=%s",
        classification["vertente"],
        classification["subtipo"],
        classification["modo"],
        classification["confianca_classificacao"],
    )
    return classification


# ─── P1.5: EXTRAÇÃO E DESAMBIGUAÇÃO FINANCEIRA ───

# Subtipos / vertentes onde o valor é base do parecer — disparam P1.5.
# Mantenha enxuto: subtipos onde a IA já demonstrou alucinar valor inicial.
_SUBTIPOS_COM_VALOR = (
    "aditivo",       # art. 125 — base de cálculo dos 25%
    "dispensa",      # art. 75 — valor decide qual inciso aplica
    "inexigibilidade",  # art. 74 — justificativa do preço
    "pesquisa_precos",
    "carona",        # adesão a ata — comprovação de vantajosidade
)


# Tolerância (pontos percentuais) entre o % de acréscimo declarado na planilha
# e o % implícito por uma base candidata. Acima disso, a base não "fecha".
_PCT_TOL = 0.5


def _num(valor) -> float | None:
    """Converte string monetária/percentual em float. Aceita '939166.94',
    '939.166,94', '22,04%', '22.04%'. Retorna None quando não numérico."""
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    s = str(valor).strip().replace("R$", "").replace("%", "").strip()
    if not s:
        return None
    if "," in s and "." in s:        # pt-BR: ponto = milhar, vírgula = decimal
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _fmt_brl(v: float) -> str:
    """Formata float como moeda pt-BR: 939166.94 -> '939.166,94'."""
    return f"{v:,.2f}".translate(str.maketrans({",": ".", ".": ","}))


def _reconciliar_valores(data: dict) -> dict:
    """Rede de segurança determinística para o P1.5.

    Confere se `acréscimo ÷ valor_inicial` reproduz o percentual declarado na
    planilha. Escolhe, entre os candidatos (campo principal + lista), a base que
    melhor reproduz o percentual. Se alguma fecha dentro de `_PCT_TOL`, corrige
    `valor_inicial_contrato` e recalcula percentual/extrapolação. Se nenhuma
    fecha, rebaixa a confiança para 'ambiguo' e registra alerta — para o P2
    inserir `[REVISAR]` em vez de concluir com base errada.
    """
    acr = _num((data.get("valor_acrescimos") or {}).get("valor"))
    declarado = _num(data.get("percentual_declarado_no_documento"))
    vic = data.get("valor_inicial_contrato") or {}
    base_atual = _num(vic.get("valor"))

    if not acr or acr <= 0 or declarado is None:
        return data  # sem dados suficientes para conferir

    bases: list[float] = []
    for c in (data.get("valores_candidatos_inicial") or []):
        v = _num(c.get("valor"))
        if v and v > 0:
            bases.append(round(v, 2))
    if base_atual and base_atual > 0:
        bases.append(round(base_atual, 2))
    bases = list(dict.fromkeys(bases))  # únicos, preservando ordem
    if not bases:
        return data

    incons = data.get("inconsistencias_detectadas")
    if not isinstance(incons, list):
        incons = data["inconsistencias_detectadas"] = []

    implicado = lambda b: acr / b * 100.0
    melhor = min(bases, key=lambda b: abs(implicado(b) - declarado))
    erro = abs(implicado(melhor) - declarado)

    if erro <= _PCT_TOL:
        pct = implicado(melhor)
        if base_atual is None or abs(round(base_atual, 2) - melhor) > 0.01:
            incons.append(
                f"Reconciliação aritmética: valor inicial ajustado para "
                f"R$ {_fmt_brl(melhor)} — é a única base que reproduz o percentual "
                f"declarado ({declarado:.2f}%). Valor antes indicado "
                f"({vic.get('valor')}) não fechava com o percentual."
            )
        vic["valor"] = f"{melhor:.2f}"
        vic["confianca"] = "alta"
        data["valor_inicial_contrato"] = vic
        data["percentual_acrescimo_calculado_canonico"] = f"{pct:.2f}%"
        data["discrepancia_percentual"] = False
        data["extrapola_limite"] = pct > 25.0 + 1e-9
    else:
        vic["confianca"] = "ambiguo"
        data["valor_inicial_contrato"] = vic
        data["discrepancia_percentual"] = True
        incons.append(
            "ALERTA: nenhum valor candidato a 'valor inicial' reproduz o "
            f"percentual de acréscimo declarado ({declarado:.2f}%). A base do "
            "art. 125 NÃO foi confirmada — conferir o contrato/planilha original "
            "antes de concluir sobre extrapolação do limite."
        )

    return data


async def extract_valores_financeiros(
    classification: dict,
    documents_text: list[str],
) -> dict | None:
    """P1.5 — Haiku desambigua valores financeiros antes do P2.

    Roda APENAS quando a consulta tem dimensão financeira central
    (subtipos em `_SUBTIPOS_COM_VALOR` ou vertente tributário-financeiro).
    Para os demais, retorna None — o P2 gera sem essa âncora.

    Retorna o dict do JSON (com aplicavel/valor_inicial_contrato/...) ou
    None quando não aplicável. Falha silenciosa: erro vira None e o P2
    segue sem o auxílio.
    """
    subtipo = (classification.get("subtipo") or "").lower()
    vertente = (classification.get("vertente") or "").lower()
    aplicavel = (
        any(s in subtipo for s in _SUBTIPOS_COM_VALOR)
        or vertente == "tributario_financeiro"
    )
    if not aplicavel:
        return None

    if not documents_text:
        return None

    docs_raw = "\n\n---\n\n".join(documents_text)

    # Resumo é extração canônica computada pelo pipeline (confiável). Calculado
    # sobre o texto BRUTO; os anexos em si vão envoltos na fronteira de confiança
    # `<documento_anexo>` (conteúdo não-confiável). Sem os anexos aqui não há nome.
    resumo = resumo_financeiro_canonico(docs_raw)
    docs_joined = wrap_documents([("", t) for t in documents_text])
    if resumo:
        docs_joined = resumo + "\n\n---\n\n" + docs_joined

    user_message = (
        "## DADOS DA CLASSIFICAÇÃO\n"
        f"vertente: {vertente}\n"
        f"subtipo: {subtipo}\n\n"
        "## DOCUMENTOS ANEXOS\n"
        f"{docs_joined}"
    )
    user_message = _truncate(user_message, MAX_USER_CONTENT_CHARS)

    try:
        raw = await _call_api(
            model=MODEL_P1,
            system=load_prompt("p1_5_valores_financeiros"),
            user_message=user_message,
            max_tokens=2000,
            stage="P1.5-valores",
        )
    except Exception as exc:
        logger.warning("P1.5 falhou (%s) — P2 prosseguirá sem âncora financeira", exc)
        return None

    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("P1.5 JSON inválido: %r", raw[:300])
        return None

    if not data.get("aplicavel", True):
        logger.info("P1.5 marcou consulta como não-financeira: %s", data.get("motivo"))
        return None

    data = _reconciliar_valores(data)

    logger.info(
        "P1.5 valores: inicial=%s acrescimos=%s extrapola=%s confianca_inicial=%s",
        (data.get("valor_inicial_contrato") or {}).get("valor"),
        (data.get("valor_acrescimos") or {}).get("valor"),
        data.get("extrapola_limite"),
        (data.get("valor_inicial_contrato") or {}).get("confianca"),
    )
    return data


# ─── P2: GERAÇÃO DO PARECER ───

async def generate_parecer(
    classification: dict,
    documents: list[tuple[str, str]],
    email_body: str,
) -> dict:
    """
    Chama P2 (Sonnet) para gerar o parecer completo.
    Serializado pelo semáforo — apenas 1 geração por vez.

    `documents` é uma lista de (filename, texto_extraído). Cada anexo é rotulado
    com seu nome no prompt (para o Sonnet saber exatamente quais documentos foram
    juntados) e recebe uma cota de caracteres via `_budget_documents`, de modo que
    nenhum anexo seja descartado inteiro pelo limite do prompt.

    Quando a consulta envolve cálculo de valor (aditivo, dispensa,
    pesquisa de preços, etc.), executa P1.5 antes — uma chamada Haiku
    dedicada a desambiguar e ancorar os valores. O resultado é injetado
    no user_message do P2 como bloco "VALORES FINANCEIROS IDENTIFICADOS",
    para o Sonnet usar como fato dado em vez de inferir do texto bruto.
    """
    budgeted = _budget_documents(documents, MAX_DOCS_CHARS)
    # Fronteira de confiança: cada anexo (conteúdo NÃO-CONFIÁVEL) vai envolto na
    # tag `<documento_anexo>`, com tags forjadas neutralizadas. Aplicado DEPOIS do
    # water-filling para que a cota por anexo seja calculada sobre o texto real.
    # Ver REGRA de FRONTEIRA DE CONFIANÇA nos prompts p2_*.txt.
    if budgeted:
        docs_joined = wrap_documents(budgeted)
    else:
        docs_joined = "(sem anexos)"

    documents_text = [text for _, text in documents]
    valores = await extract_valores_financeiros(classification, documents_text)
    valores_block = ""
    if valores is not None:
        valores_block = (
            "\n\n## VALORES FINANCEIROS IDENTIFICADOS (P1.5)\n"
            "Estes valores foram extraídos e desambiguados por etapa especializada.\n"
            "USE-OS como fato dado. Se a confiança for 'ambiguo' ou houver\n"
            "`inconsistencias_detectadas`, insira `[REVISAR — ...]` no parecer\n"
            "explicando ao advogado humano o que conferir.\n\n"
            f"{json.dumps(valores, ensure_ascii=False, indent=2)}\n"
        )

    user_message = (
        "## DADOS DA CONSULTA (classificação automática)\n"
        f"{json.dumps(classification, ensure_ascii=False, indent=2)}"
        f"{valores_block}\n\n"
        "## EMAIL ORIGINAL\n"
        f"{email_body}\n\n"
        "## DOCUMENTOS ANEXOS\n"
        f"{docs_joined}"
    )
    # Nota: este cap é "sem limite prático" (nenhuma consulta real encosta); no
    # pior caso corta a tag `</documento_anexo>` de fechamento do ÚLTIMO anexo —
    # risco baixo (é sempre o último bloco e há aviso de truncamento). Ver plano.
    user_message = _truncate(user_message, MAX_P2_USER_CONTENT_CHARS)

    vertente = resolve_vertente(classification)
    subtipo = classification.get("subtipo") or ""
    modo = classification.get("modo") or "consultivo_puro"
    logger.info("P2 vertente=%s subtipo=%s modo=%s", vertente, subtipo, modo)

    system_prompt = assemble_p2_context(
        vertente=vertente,
        subtipo=subtipo,
        modo=modo,
        include_fewshot=True,
    )

    # Camada M — leis municipais do município da consulta (índice sempre + texto
    # integral da lei relevante ao tema). Apendado fora do lru_cache porque depende
    # do município, que não é chave de cache do assemble_p2_context.
    municipal_block = assemble_municipal_context(
        municipio=classification.get("municipio", "") or "",
        subtipo=subtipo,
        assunto=classification.get("assunto_resumido", "") or "",
    )
    if municipal_block:
        system_prompt = f"{system_prompt}\n\n---\n\n{municipal_block}"

    # Camada 6 — orçamento de web_search por modo da consulta.
    web_search_budget = (
        settings.WEB_SEARCH_MAX_USES_QUASE_PROCESSUAL
        if modo == "quase_processual"
        else settings.WEB_SEARCH_MAX_USES_CONSULTIVO
    )

    async with _sonnet_semaphore:
        raw = await _call_generation_with_fallback(
            system=system_prompt,
            user_message=user_message,
            max_tokens=12000,
            stage=f"P2-{vertente}",
            web_search_max_uses=web_search_budget,
        )

    result = parse_parecer_xml(raw)
    result["prompt_version"] = get_prompt_version()
    return result


# ─── P3: REVISÃO COM OBSERVAÇÕES ───

async def revise_parecer(
    parecer_atual: dict,
    observacoes: str,
    secoes_para_revisar: list[str],
    classification: dict | None = None,
) -> dict:
    """
    Chama P3 (Sonnet) para revisar o parecer com as observações do advogado.
    Serializado pelo semáforo — compartilha fila com P2.

    `classification` (opcional): quando fornecido, monta o system prompt modular
    via `assemble_p3_context(vertente, subtipo, modo)` — anexa a reference do
    subtipo e (se sensível) as armadilhas TCE-CE. Quando None, usa o prompt mestre
    bruto. Também habilita `web_search` com o mesmo orçamento do P2.
    """
    parecer_xml = (
        "<parecer>\n"
        f"<ementa>{parecer_atual.get('ementa', '')}</ementa>\n"
        f"<relatorio>{parecer_atual.get('relatorio', '')}</relatorio>\n"
        f"<fundamentos>{parecer_atual.get('fundamentos', '')}</fundamentos>\n"
        f"<conclusao>{parecer_atual.get('conclusao', '')}</conclusao>\n"
        "</parecer>"
    )

    user_message = (
        "## PARECER ATUAL\n"
        f"{parecer_xml}\n\n"
        "## OBSERVAÇÕES DO ADVOGADO REVISOR\n"
        f"{observacoes}\n\n"
        "## SEÇÕES A REVISAR\n"
        f"{json.dumps(secoes_para_revisar, ensure_ascii=False)}"
    )
    user_message = _truncate(user_message, MAX_USER_CONTENT_CHARS)

    if classification:
        vertente = resolve_vertente(classification)
        subtipo = classification.get("subtipo") or ""
        modo = classification.get("modo") or "consultivo_puro"
        system_prompt = assemble_p3_context(vertente=vertente, subtipo=subtipo, modo=modo)
        # Camada M — leis municipais também na revisão, com orçamento menor (o
        # user_message do P3 já carrega o XML do parecer original).
        municipal_block = assemble_municipal_context(
            municipio=classification.get("municipio", "") or "",
            subtipo=subtipo,
            assunto=classification.get("assunto_resumido", "") or "",
            full_text_budget=18_000,
            force_top_match=False,
        )
        if municipal_block:
            system_prompt = f"{system_prompt}\n\n---\n\n{municipal_block}"
        web_search_budget = (
            settings.WEB_SEARCH_MAX_USES_QUASE_PROCESSUAL
            if modo == "quase_processual"
            else settings.WEB_SEARCH_MAX_USES_CONSULTIVO
        )
        stage = f"P3-{vertente}"
    else:
        system_prompt = load_prompt("p3_parecer_revision")
        web_search_budget = 0
        stage = "P3"

    async with _sonnet_semaphore:
        raw = await _call_generation_with_fallback(
            system=system_prompt,
            user_message=user_message,
            max_tokens=6000,
            stage=stage,
            web_search_max_uses=web_search_budget,
        )

    return parse_parecer_xml(raw)


async def correct_selection(trecho: str, instrucao: str) -> str:
    """Correção PONTUAL de um trecho selecionado do parecer (auditoria — Erro 3).

    Reescreve APENAS o trecho conforme a instrução, preservando o estilo autoral,
    e devolve só o texto corrigido (texto puro). Não toca no resto do documento —
    o editor substitui apenas o range selecionado, sem reescrever/recarregar tudo.
    Sem web_search (correção de redação/forma — rápida e barata)."""
    system_prompt = (
        "Você é o parecerista revisor do escritório Advocacia & Assessoria — Dr. Francisco "
        "Ione Pereira Lima. Recebe um TRECHO de um parecer jurídico já redigido e uma "
        "INSTRUÇÃO de correção. Reescreva APENAS o trecho, aplicando a instrução e "
        "preservando o estilo autoral do escritório: prosa contínua, sem subdivisão numerada, "
        "sem bullets, conectivos de abertura variados (não repetir 'Há'), sem juridiquês "
        "arcaico (destarte, outrossim, data venia decorativos).\n"
        "Regras de saída (obrigatórias):\n"
        "- Responda SOMENTE com o texto corrigido do trecho — sem aspas, sem rótulos, sem "
        "comentários, sem explicações, sem preâmbulo.\n"
        "- Mantenha o português e o registro técnico-institucional.\n"
        "- Não acrescente conteúdo novo além do que a instrução pede; não reescreva o que não "
        "foi pedido; preserve a extensão aproximada do trecho.\n"
        "- Preserve marcadores [REVISAR — ...] / [!VERIFICAR: ... !] existentes no trecho, salvo "
        "se a instrução mandar resolvê-los."
    )
    user_message = (
        "## TRECHO A CORRIGIR\n"
        f"{trecho}\n\n"
        "## INSTRUÇÃO\n"
        f"{instrucao}\n\n"
        "Reescreva o trecho conforme a instrução. Responda apenas com o texto corrigido."
    )
    user_message = _truncate(user_message, MAX_USER_CONTENT_CHARS)

    async with _sonnet_semaphore:
        raw = await _call_generation_with_fallback(
            system=system_prompt,
            user_message=user_message,
            max_tokens=2000,
            stage="P3-trecho",
        )
    return raw.strip()
