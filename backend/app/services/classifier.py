from __future__ import annotations

import json
import logging

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.parecer import ParecerModelo, ParecerRequest, ParecerStatus, ParecerTema
from app.prompts.classificacao import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

CLAUDE_MODEL = "claude-sonnet-4-20250514"


async def classify(parecer_request_id: str, db: AsyncSession) -> ParecerRequest:
    result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == parecer_request_id)
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        raise ValueError(f"ParecerRequest {parecer_request_id} nao encontrado")

    if not pr.extracted_text:
        raise ValueError("ParecerRequest sem texto extraido para classificar")

    user_content = f"Assunto: {pr.subject or 'N/A'}\n\n{pr.extracted_text}"

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw_text = response.content[0].text.strip()
    logger.info("Classificacao raw response: %s", raw_text)

    data = json.loads(raw_text)

    tema_str = data.get("tema", "administrativo")
    try:
        pr.tema = ParecerTema(tema_str)
    except ValueError:
        pr.tema = ParecerTema.administrativo

    modelo_str = data.get("modelo_parecer", "generico")
    try:
        pr.modelo = ParecerModelo(modelo_str)
    except ValueError:
        pr.modelo = ParecerModelo.generico

    old_status = pr.status
    pr.status = ParecerStatus.classificado

    from app.models.parecer import ParecerStatusHistory

    db.add(
        ParecerStatusHistory(
            request_id=pr.id,
            from_status=old_status,
            to_status=ParecerStatus.classificado,
            notes=json.dumps(data, ensure_ascii=False),
        )
    )

    await db.commit()
    await db.refresh(pr)

    return pr, data
