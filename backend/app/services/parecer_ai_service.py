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
from app.services.prompt_service import (
    assemble_p2_context,
    assemble_p3_context,
    build_p2_prompt,
    get_prompt_version,
    load_prompt,
    resolve_vertente,
)
from app.services.parecer_html_service import parse_parecer_xml

logger = logging.getLogger(__name__)

# Modelos por etapa
MODEL_P1 = "claude-haiku-4-5-20251001"   # classificação: rápido, barato, TPM separado
MODEL_P2_P3 = "claude-sonnet-4-6"  # geração/revisão: qualidade máxima

# Limite de conteúdo do usuário (~15k tokens ≈ 60k chars)
MAX_USER_CONTENT_CHARS = 60_000

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
            async with AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) as client:
                response = await client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=0,
                    system=system,
                    messages=[{"role": "user", "content": user_message}],
                    **tools_kwargs,
                )
            usage = response.usage
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
        labeled_parts = [f"## Anexo: {fn}\n{text}" for fn, text in ordered]
        user_message += "\n\n---\n\n" + "\n\n---\n\n".join(labeled_parts)
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


# ─── P2: GERAÇÃO DO PARECER ───

async def generate_parecer(
    classification: dict,
    documents_text: list[str],
    email_body: str,
) -> dict:
    """
    Chama P2 (Sonnet) para gerar o parecer completo.
    Serializado pelo semáforo — apenas 1 geração por vez.
    """
    docs_joined = "\n\n---\n\n".join(documents_text) if documents_text else "(sem anexos)"

    user_message = (
        "## DADOS DA CONSULTA (classificação automática)\n"
        f"{json.dumps(classification, ensure_ascii=False, indent=2)}\n\n"
        "## EMAIL ORIGINAL\n"
        f"{email_body}\n\n"
        "## DOCUMENTOS ANEXOS\n"
        f"{docs_joined}"
    )
    user_message = _truncate(user_message, MAX_USER_CONTENT_CHARS)

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

    # Camada 6 — orçamento de web_search por modo da consulta.
    web_search_budget = (
        settings.WEB_SEARCH_MAX_USES_QUASE_PROCESSUAL
        if modo == "quase_processual"
        else settings.WEB_SEARCH_MAX_USES_CONSULTIVO
    )

    async with _sonnet_semaphore:
        raw = await _call_api(
            model=MODEL_P2_P3,
            system=system_prompt,
            user_message=user_message,
            max_tokens=8000,
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
        raw = await _call_api(
            model=MODEL_P2_P3,
            system=system_prompt,
            user_message=user_message,
            max_tokens=6000,
            stage=stage,
            web_search_max_uses=web_search_budget,
        )

    return parse_parecer_xml(raw)
