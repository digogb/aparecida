import base64
import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.parecer import ParecerRequest, ParecerStatus
from app.models.system_config import SystemConfig

PREFIX = "/api"
TAGS = ["gmail"]

router = APIRouter()


async def _process_gmail_message(request_id: str, gmail_info: dict) -> None:
    """Background task: extract attachments, classify (P1) and generate (P2)."""
    from app.services.pipeline import process_parecer_pipeline
    await process_parecer_pipeline(request_id)


@router.get("/gmail/status")
async def gmail_status(db: AsyncSession = Depends(get_db)) -> dict:
    if not (settings.GMAIL_REFRESH_TOKEN or Path(settings.GMAIL_CREDENTIALS_PATH).exists()):
        return {"status": "not_configured"}
    result = await db.execute(
        select(SystemConfig).where(SystemConfig.key == "gmail_auth_status")
    )
    cfg = result.scalar_one_or_none()
    if cfg and cfg.value == "token_revoked":
        return {"status": "token_revoked"}
    return {"status": "connected"}


@router.post("/gmail/webhook", status_code=200)
async def gmail_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    token: str = Query(default=""),
    db: AsyncSession = Depends(get_db),
) -> dict:
    configured_token = os.environ.get("PUBSUB_VERIFICATION_TOKEN", "")
    if configured_token and token != configured_token:
        raise HTTPException(status_code=403, detail="Token invalido")

    body = await request.json()
    message = body.get("message", {})
    raw_data = message.get("data", "")

    gmail_info: dict = {}
    if raw_data:
        try:
            decoded = base64.b64decode(raw_data).decode("utf-8")
            gmail_info = json.loads(decoded)
        except Exception:
            pass

    gmail_message_id: str | None = message.get("messageId") or message.get("message_id")
    # Use historyId as thread key when available, fallback to messageId
    gmail_thread_id: str | None = gmail_info.get("historyId") or gmail_message_id
    sender_email: str | None = gmail_info.get("emailAddress") or None

    # Deduplicate by thread id
    if gmail_thread_id:
        existing = await db.execute(
            select(ParecerRequest).where(ParecerRequest.gmail_thread_id == gmail_thread_id)
        )
        if existing.scalar_one_or_none():
            return {"status": "ok", "action": "duplicate"}

    parecer = ParecerRequest(
        id=uuid.uuid4(),
        gmail_thread_id=gmail_thread_id,
        gmail_message_id=gmail_message_id,
        sender_email=sender_email,
        status=ParecerStatus.pendente,
        raw_payload=body,
    )
    db.add(parecer)
    await db.commit()
    await db.refresh(parecer)

    background_tasks.add_task(_process_gmail_message, str(parecer.id), gmail_info)

    return {"status": "ok", "request_id": str(parecer.id)}
