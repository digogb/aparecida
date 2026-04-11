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
    build_p2_prompt,
    get_prompt_version,
    load_prompt,
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


def _log_api_call(stage: str, model: str, input_tokens: int, output_tokens: int, raw_response: str) -> None:
    """Append one record per API call to ai_calls.jsonl."""
    AI_CALLS_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "raw_response": raw_response,
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


async def _call_api(
    model: str,
    system: str,
    user_message: str,
    max_tokens: int,
    stage: str = "?",
) -> str:
    """
    Chama a API do Claude com retry automático em caso de rate limit.
    Backoff: 60s, 120s, 180s — alinhado com o reset do limite por minuto.
    """
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
                )
            usage = response.usage
            raw_text = response.content[0].text
            logger.warning(
                "TOKENS [%s/%s] input=%d output=%d total=%d",
                stage, model,
                usage.input_tokens,
                usage.output_tokens,
                usage.input_tokens + usage.output_tokens,
            )
            _log_api_call(stage, model, usage.input_tokens, usage.output_tokens, raw_text)
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


# ─── P1: CLASSIFICAÇÃO ───

async def classify_email(
    email_body: str,
    attachments_text: list[str],
) -> dict:
    """
    Chama P1 (Haiku) para classificar o email.
    Haiku tem TPM separado — não precisa do semáforo.
    """
    user_message = email_body
    if attachments_text:
        user_message += "\n\n---\n\n" + "\n\n---\n\n".join(attachments_text)
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
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("P1 JSON inválido, retornando com confiança baixa")
        return {
            "municipio": "",
            "uf": "",
            "orgao_consulente": "",
            "area_principal": "administrativo",
            "areas_conexas": [],
            "tipo_parecer": "preventivo",
            "assunto_resumido": "",
            "fatos": "",
            "duvida_central": email_body[:500],
            "dados_ausentes": [],
            "urgencia": "normal",
            "confianca_classificacao": "baixa",
        }


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

    async with _sonnet_semaphore:
        raw = await _call_api(
            model=MODEL_P2_P3,
            system=build_p2_prompt(include_fewshot=True),
            user_message=user_message,
            max_tokens=8000,
            stage="P2",
        )

    result = parse_parecer_xml(raw)
    result["prompt_version"] = get_prompt_version()
    return result


# ─── P3: REVISÃO COM OBSERVAÇÕES ───

async def revise_parecer(
    parecer_atual: dict,
    observacoes: str,
    secoes_para_revisar: list[str],
) -> dict:
    """
    Chama P3 (Sonnet) para revisar o parecer com as observações do advogado.
    Serializado pelo semáforo — compartilha fila com P2.
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

    async with _sonnet_semaphore:
        raw = await _call_api(
            model=MODEL_P2_P3,
            system=load_prompt("p3_parecer_revision"),
            user_message=user_message,
            max_tokens=6000,
            stage="P3",
        )

    return parse_parecer_xml(raw)
