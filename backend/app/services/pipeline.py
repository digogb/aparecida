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
from app.services.classifier import NotLegalConsultationError
from app.services.notification import notify_parecer_event

logger = logging.getLogger(__name__)


async def _mark_erro(parecer_request_id: str, etapa: str, exc: Exception) -> None:
    """Salva status=erro e registra histórico. Nunca lança exceção."""
    try:
        async with async_session() as db:
            result = await db.execute(
                select(ParecerRequest).where(ParecerRequest.id == parecer_request_id)
            )
            pr = result.scalar_one_or_none()
            if pr is None:
                return
            old_status = pr.status
            pr.status = ParecerStatus.erro
            db.add(
                ParecerStatusHistory(
                    request_id=pr.id,
                    from_status=old_status,
                    to_status=ParecerStatus.erro,
                    notes=f"Falha na etapa {etapa}: {type(exc).__name__}: {exc}",
                )
            )
            await db.commit()
        await notify_parecer_event("parecer.error", parecer_request_id, "erro", {"etapa": etapa})
    except Exception:
        logger.exception("Pipeline: erro ao salvar status de falha para %s", parecer_request_id)


async def _mark_devolvido(parecer_request_id: str, motivo: str) -> None:
    """Marca o parecer como devolvido (email não é consulta jurídica)."""
    try:
        async with async_session() as db:
            result = await db.execute(
                select(ParecerRequest).where(ParecerRequest.id == parecer_request_id)
            )
            pr = result.scalar_one_or_none()
            if pr is None:
                return
            old_status = pr.status
            pr.status = ParecerStatus.devolvido
            db.add(
                ParecerStatusHistory(
                    request_id=pr.id,
                    from_status=old_status,
                    to_status=ParecerStatus.devolvido,
                    notes=f"Email não é uma consulta jurídica: {motivo}",
                )
            )
            await db.commit()
        await notify_parecer_event("parecer.devolvido", parecer_request_id, "devolvido")
    except Exception:
        logger.exception("Pipeline: erro ao marcar devolvido para %s", parecer_request_id)


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
        await notify_parecer_event("parecer.classified", parecer_request_id, "classificado")
    except NotLegalConsultationError as exc:
        logger.warning("Pipeline P1: email nao juridico, marcando como devolvido — %s", exc)
        await _mark_devolvido(parecer_request_id, str(exc))
        return
    except Exception as exc:
        logger.exception("Pipeline P1: falha ao classificar %s", parecer_request_id)
        await _mark_erro(parecer_request_id, "P1-classificacao", exc)
        return

    # ─── P2: Gerar minuta ───
    try:
        logger.info("Pipeline P2: gerando minuta para %s", parecer_request_id)
        async with async_session() as db:
            await parecer_engine.generate(parecer_request_id, db)
        logger.info("Pipeline P2: minuta gerada para %s", parecer_request_id)
        await notify_parecer_event("parecer.generated", parecer_request_id, "gerado")
    except Exception as exc:
        logger.exception("Pipeline P2: falha ao gerar minuta para %s", parecer_request_id)
        await _mark_erro(parecer_request_id, "P2-geracao", exc)
