"""
Pipeline de processamento automático: classify (P1) → generate (P2).

Roda em background após a importação de um email (.eml ou Gmail webhook).
Usa sua própria sessão de banco — independente do request HTTP que o disparou.
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models.parecer import ParecerRequest, ParecerStatus, ParecerStatusHistory
from app.services import classifier, parecer_engine

logger = logging.getLogger(__name__)


async def process_parecer_pipeline(parecer_request_id: str) -> None:
    """
    Executa P1 (classify) → P2 (generate) para um ParecerRequest.
    Atualiza o status no banco a cada etapa.
    Erros são logados mas não propagados (é background task).
    """
    async with async_session() as db:
        result = await db.execute(
            select(ParecerRequest)
            .where(ParecerRequest.id == parecer_request_id)
            .options(selectinload(ParecerRequest.attachments))
        )
        pr = result.scalar_one_or_none()
        if pr is None:
            logger.error("Pipeline: ParecerRequest %s nao encontrado", parecer_request_id)
            return

        if not pr.extracted_text:
            logger.warning("Pipeline: ParecerRequest %s sem texto extraido, abortando", parecer_request_id)
            return

    # ─── P1: Classificar ───
    try:
        logger.info("Pipeline P1: classificando %s", parecer_request_id)
        async with async_session() as db:
            await classifier.classify(parecer_request_id, db)
        logger.info("Pipeline P1: classificacao concluida para %s", parecer_request_id)
    except Exception:
        logger.exception("Pipeline P1: falha ao classificar %s", parecer_request_id)
        return

    # ─── P2: Gerar minuta ───
    try:
        logger.info("Pipeline P2: gerando minuta para %s", parecer_request_id)
        async with async_session() as db:
            await parecer_engine.generate(parecer_request_id, db)
        logger.info("Pipeline P2: minuta gerada para %s", parecer_request_id)
    except Exception:
        logger.exception("Pipeline P2: falha ao gerar minuta para %s", parecer_request_id)
