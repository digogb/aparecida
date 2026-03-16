"""
DJE Sync service — normalizes, deduplicates, and classifies DJE movements.

Supports two ingestion modes:
  - Webhook: call ingest_movement() directly from the /dje/webhook endpoint.
  - Polling: schedule poll_dje() via APScheduler (every 15 min) once a real
    DJE API URL is configured in settings.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movement import Movement, MovementType, Process

logger = logging.getLogger(__name__)

# Raw DJE type string → MovementType adapter
_TYPE_MAP: dict[str, MovementType] = {
    "intimacao":    MovementType.intimacao,
    "intimação":    MovementType.intimacao,
    "sentenca":     MovementType.sentenca,
    "sentença":     MovementType.sentenca,
    "despacho":     MovementType.despacho,
    "acordao":      MovementType.acordao,
    "acórdão":      MovementType.acordao,
    "publicacao":   MovementType.publicacao,
    "publicação":   MovementType.publicacao,
    "distribuicao": MovementType.distribuicao,
    "distribuição": MovementType.distribuicao,
}

# Business rules per movement type
MOVEMENT_RULES: dict[MovementType, dict] = {
    MovementType.intimacao:    {"notify": True,  "email_alert": True,  "priority": "high"},
    MovementType.sentenca:     {"notify": True,  "email_alert": False, "priority": "medium"},
    MovementType.despacho:     {"notify": True,  "email_alert": False, "priority": "low"},
    MovementType.acordao:      {"notify": True,  "email_alert": False, "priority": "medium"},
    MovementType.publicacao:   {"notify": True,  "email_alert": False, "priority": "medium"},
    MovementType.distribuicao: {"notify": True,  "email_alert": False, "priority": "low"},
    MovementType.outros:       {"notify": False, "email_alert": False, "priority": "low"},
}


def _normalize_type(raw_type: str) -> MovementType:
    """Adapter: map raw DJE string to MovementType enum."""
    return _TYPE_MAP.get(raw_type.lower().strip(), MovementType.outros)


async def _get_or_create_process(
    db: AsyncSession,
    number: str,
    court: str | None = None,
) -> Process:
    result = await db.execute(select(Process).where(Process.number == number))
    process = result.scalar_one_or_none()
    if process is None:
        process = Process(number=number, court=court)
        db.add(process)
        await db.flush()
    return process


async def ingest_movement(
    db: AsyncSession,
    dje_id: str,
    process_number: str,
    raw_type: str,
    content: str | None = None,
    published_at: datetime | None = None,
    court: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Movement | None:
    """
    Normalize and insert one DJE movement.

    Returns the Movement on success, None if it is a duplicate
    (deduplication via ON CONFLICT DO NOTHING on dje_id).
    """
    movement_type = _normalize_type(raw_type)
    process = await _get_or_create_process(db, process_number, court)

    # Deduplication: ON CONFLICT DO NOTHING ensures idempotency
    stmt = (
        pg_insert(Movement)
        .values(
            process_id=process.id,
            dje_id=dje_id,
            type=movement_type,
            content=content,
            published_at=published_at,
            is_read=False,
            metadata_=metadata,
        )
        .on_conflict_do_nothing(index_elements=["dje_id"])
        .returning(Movement.id)
    )
    result = await db.execute(stmt)
    row = result.fetchone()

    if row is None:
        logger.debug("Movement %s already exists — skipped", dje_id)
        return None

    await db.commit()

    movement_result = await db.execute(select(Movement).where(Movement.id == row[0]))
    movement = movement_result.scalar_one()

    # Apply business rules
    rules = MOVEMENT_RULES.get(movement_type, {})
    if rules.get("notify"):
        from app.services.notification import notify_movement
        await notify_movement(db, movement)

    logger.info(
        "Ingested movement dje_id=%s type=%s process=%s",
        dje_id,
        movement_type.value,
        process_number,
    )
    return movement


async def poll_dje(db: AsyncSession) -> int:
    """
    Polling adapter — called by APScheduler every 15 minutes.

    Replace the stub below with a real DJE API HTTP call when
    the external endpoint is available. Returns number of new movements.
    """
    from app.config import settings

    dje_api_url = getattr(settings, "DJE_API_URL", None)
    if not dje_api_url:
        logger.debug("DJE_API_URL not configured, skipping poll")
        return 0

    try:
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(dje_api_url)
            resp.raise_for_status()
            items: list[dict] = resp.json()

        count = 0
        for item in items:
            movement = await ingest_movement(
                db=db,
                dje_id=item["id"],
                process_number=item["process_number"],
                raw_type=item.get("type", "outros"),
                content=item.get("content"),
                published_at=item.get("published_at"),
                court=item.get("court"),
                metadata=item.get("metadata"),
            )
            if movement is not None:
                count += 1

        logger.info("DJE poll completed: %d new movements", count)
        return count
    except Exception as e:
        logger.warning("DJE poll failed: %s", e)
        return 0
