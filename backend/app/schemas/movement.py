from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.movement import MovementType


class ProcessOut(BaseModel):
    id: uuid.UUID
    number: str
    subject: Optional[str] = None
    court: Optional[str] = None
    municipio_id: Optional[uuid.UUID] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MovementOut(BaseModel):
    id: uuid.UUID
    process_id: uuid.UUID
    dje_id: Optional[str] = None
    type: MovementType
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    is_read: bool
    metadata_: Optional[dict[str, Any]] = None
    created_at: datetime
    process: Optional[ProcessOut] = None

    model_config = {"from_attributes": True}


class MovementStats(BaseModel):
    total: int
    unread: int
    by_type: dict[str, int]
    last_sync: Optional[datetime] = None


class DJEWebhookPayload(BaseModel):
    dje_id: str
    process_number: str
    type: str
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    court: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
