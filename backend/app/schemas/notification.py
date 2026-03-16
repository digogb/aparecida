from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.notification import NotificationChannel, NotificationStatus


class NotificationOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    channel: NotificationChannel
    status: NotificationStatus
    title: str
    body: Optional[str] = None
    link: Optional[str] = None
    metadata_: Optional[dict[str, Any]] = None
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountOut(BaseModel):
    count: int
