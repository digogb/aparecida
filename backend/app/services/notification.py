"""
Notification service - in-app notifications, email alerts, and WebSocket broadcast.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movement import Movement, MovementType
from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.models.user import User

logger = logging.getLogger(__name__)

MOVEMENT_TITLES: dict[MovementType, str] = {
    MovementType.intimacao:    "Nova Intimação",
    MovementType.sentenca:     "Nova Sentença",
    MovementType.despacho:     "Novo Despacho",
    MovementType.acordao:      "Novo Acórdão",
    MovementType.publicacao:   "Nova Publicação",
    MovementType.distribuicao: "Nova Distribuição",
    MovementType.outros:       "Nova Movimentação",
}


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts messages."""

    def __init__(self) -> None:
        self._connections: list[Any] = []

    async def connect(self, websocket: Any) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: Any) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, data: dict) -> None:
        dead = []
        for ws in list(self._connections):
            try:
                await ws.send_text(json.dumps(data, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


# Global singleton used by routers
ws_manager = ConnectionManager()


async def _get_lawyers(db: AsyncSession) -> list[User]:
    from app.models.user import UserRole
    result = await db.execute(
        select(User).where(
            User.is_active == True,
            User.role.in_([UserRole.advogado, UserRole.admin]),
        )
    )
    return list(result.scalars().all())


async def notify_movement(db: AsyncSession, movement: Movement) -> None:
    """Create in-app notification for all lawyers and broadcast via WebSocket."""
    title = MOVEMENT_TITLES.get(movement.type, "Nova Movimentação")
    lawyers = await _get_lawyers(db)

    for lawyer in lawyers:
        notif = Notification(
            user_id=lawyer.id,
            channel=NotificationChannel.in_app,
            status=NotificationStatus.pending,
            title=title,
            link=f"/movements/{movement.id}",
            metadata_={"movement_id": str(movement.id), "type": movement.type.value},
        )
        db.add(notif)

    await db.flush()

    # Email alert for intimações only
    if movement.type == MovementType.intimacao:
        try:
            await send_email_alert(movement)
        except Exception as e:
            logger.warning("Email alert failed for movement %s: %s", movement.id, e)

    # WebSocket broadcast (fire-and-forget)
    payload = {
        "event": "movement.created",
        "data": {
            "id": str(movement.id),
            "type": movement.type.value,
            "process_id": str(movement.process_id),
            "published_at": movement.published_at.isoformat() if movement.published_at else None,
        },
    }
    asyncio.create_task(ws_manager.broadcast(payload))


async def send_email_alert(movement: Movement) -> None:
    """Send email alert for intimações via Gmail API."""
    import base64
    from email.mime.text import MIMEText

    from app.config import settings

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        logger.warning("Google API client not available, skipping email alert")
        return

    _GMAIL_SCOPES = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]

    creds = service_account.Credentials.from_service_account_file(
        settings.GMAIL_CREDENTIALS_PATH,
        scopes=_GMAIL_SCOPES,
    )
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    body = (
        f"Nova Intimação recebida no DJE.\n\n"
        f"Processo ID: {movement.process_id}\n"
        f"Publicado em: {movement.published_at}\n\n"
        f"Acesse o sistema para verificar os detalhes e o prazo de resposta.\n\n"
        f"Atenciosamente,\n"
        f"Pearson Hardman"
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Alerta DJE: Nova Intimação"
    msg["To"] = "me"

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    logger.info("Email alert sent for intimação movement %s", movement.id)


async def notify_peer_review_requested(
    db: AsyncSession,
    peer_review: Any,
    parecer: Any,
) -> None:
    """Notifica o revisor que uma revisão foi solicitada."""
    numero = getattr(parecer, "numero_parecer", None) or str(parecer.id)[:8]
    notif = Notification(
        user_id=peer_review.reviewer_id,
        channel=NotificationChannel.in_app,
        status=NotificationStatus.pending,
        title=f"Revisão solicitada: {numero}",
        body="Um colega enviou trechos para você revisar.",
        link=f"/pareceres/{parecer.id}",
        metadata_={
            "type": "peer_review",
            "peer_review_id": str(peer_review.id),
            "parecer_request_id": str(parecer.id),
        },
    )
    db.add(notif)
    await db.flush()

    payload = {
        "event": "peer_review.requested",
        "data": {
            "peer_review_id": str(peer_review.id),
            "parecer_id": str(parecer.id),
            "reviewer_id": str(peer_review.reviewer_id),
        },
    }
    asyncio.create_task(ws_manager.broadcast(payload))


async def notify_peer_review_completed(
    db: AsyncSession,
    peer_review: Any,
    parecer: Any,
) -> None:
    """Notifica o solicitante que a revisão foi concluída."""
    numero = getattr(parecer, "numero_parecer", None) or str(parecer.id)[:8]
    notif = Notification(
        user_id=peer_review.requested_by,
        channel=NotificationChannel.in_app,
        status=NotificationStatus.pending,
        title=f"Revisão concluída: {numero}",
        body="Seu colega concluiu a revisão dos trechos.",
        link=f"/pareceres/{parecer.id}",
        metadata_={
            "type": "peer_review",
            "peer_review_id": str(peer_review.id),
            "parecer_request_id": str(parecer.id),
        },
    )
    db.add(notif)
    await db.flush()

    payload = {
        "event": "peer_review.completed",
        "data": {
            "peer_review_id": str(peer_review.id),
            "parecer_id": str(parecer.id),
            "requested_by": str(peer_review.requested_by),
        },
    }
    asyncio.create_task(ws_manager.broadcast(payload))


async def get_unread_count(db: AsyncSession, user_id: str) -> int:
    """Return count of unread in-app notifications for a user."""
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.channel == NotificationChannel.in_app,
            Notification.status != NotificationStatus.read,
        )
    )
    return result.scalar_one() or 0
