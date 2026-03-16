import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.notification import Notification, NotificationStatus
from app.schemas.notification import NotificationOut, UnreadCountOut
from app.services.notification import get_unread_count

PREFIX = "/api"
TAGS = ["notifications"]

router = APIRouter()

bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"


def _require_user_id(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")


# ---------------------------------------------------------------------------
# Unread count (before /{id} to avoid route shadowing)
# ---------------------------------------------------------------------------

@router.get("/notifications/unread-count", response_model=UnreadCountOut)
async def unread_count(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> UnreadCountOut:
    user_id = _require_user_id(credentials)
    count = await get_unread_count(db, user_id)
    return UnreadCountOut(count=count)


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

@router.get("/notifications", response_model=list[NotificationOut])
async def list_notifications(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[NotificationOut]:
    user_id = _require_user_id(credentials)
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Mark read
# ---------------------------------------------------------------------------

@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_id = _require_user_id(credentials)
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.status = NotificationStatus.read
    notif.read_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "ok"}
