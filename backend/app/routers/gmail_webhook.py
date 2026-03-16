import base64
import json
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parecer import ParecerRequest, ParecerStatus

PREFIX = "/api"
TAGS = ["gmail"]

router = APIRouter()


async def _process_gmail_message(request_id: str, gmail_info: dict) -> None:
    """Background task placeholder: extract attachments and classify parecer."""
    pass


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
