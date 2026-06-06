"""
Notification service - in-app notifications and WebSocket broadcast.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationChannel, NotificationStatus

logger = logging.getLogger(__name__)


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


# Global singletons used by routers
ws_manager = ConnectionManager()
parecer_ws_manager = ConnectionManager()


async def notify_parecer_event(
    event: str,
    parecer_id: Any,
    status: str | None = None,
    extra: dict | None = None,
) -> None:
    """Broadcast parecer lifecycle events (created/classified/generated/error) to WS clients."""
    payload = {
        "event": event,
        "data": {"id": str(parecer_id), "status": status, **(extra or {})},
    }
    asyncio.create_task(parecer_ws_manager.broadcast(payload))


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
