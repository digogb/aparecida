from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.parecer import (
    ExtractionMethod,
    ExtractionStatus,
    ParecerModelo,
    ParecerStatus,
    ParecerTema,
    VersionSource,
)


class ParecerRequestCreate(BaseModel):
    municipio_id: Optional[uuid.UUID] = None
    gmail_thread_id: Optional[str] = None
    gmail_message_id: Optional[str] = None
    subject: Optional[str] = None
    sender_email: Optional[str] = None
    raw_payload: Optional[dict[str, Any]] = None


class ParecerRequestUpdate(BaseModel):
    municipio_id: Optional[uuid.UUID] = None
    assigned_to: Optional[uuid.UUID] = None
    status: Optional[ParecerStatus] = None
    tema: Optional[ParecerTema] = None
    modelo: Optional[ParecerModelo] = None
    extracted_text: Optional[str] = None
    extraction_method: Optional[ExtractionMethod] = None
    extraction_status: Optional[ExtractionStatus] = None


class ParecerRequestOut(BaseModel):
    id: uuid.UUID
    municipio_id: Optional[uuid.UUID]
    assigned_to: Optional[uuid.UUID]
    gmail_thread_id: Optional[str]
    gmail_message_id: Optional[str]
    subject: Optional[str]
    sender_email: Optional[str]
    sent_to_email: Optional[str]
    extracted_text: Optional[str]
    extraction_method: Optional[ExtractionMethod]
    extraction_status: Optional[ExtractionStatus]
    status: ParecerStatus
    tema: Optional[ParecerTema]
    modelo: Optional[ParecerModelo]
    numero_parecer: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParecerVersionOut(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    version_number: int
    source: VersionSource
    content_tiptap: Optional[dict[str, Any]]
    content_html: Optional[str]
    reprocess_instructions: Optional[str]
    created_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParecerStatusHistoryOut(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    from_status: Optional[ParecerStatus]
    to_status: ParecerStatus
    changed_by: Optional[uuid.UUID]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
