from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.parecer import ExtractionMethod, ExtractionStatus


class AttachmentCreate(BaseModel):
    request_id: uuid.UUID
    filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    storage_path: Optional[str] = None


class AttachmentOut(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    filename: str
    content_type: Optional[str]
    size_bytes: Optional[int]
    extracted_text: Optional[str]
    extraction_method: Optional[ExtractionMethod]
    extraction_status: Optional[ExtractionStatus]
    storage_path: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
