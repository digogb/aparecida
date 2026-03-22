import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.parecer import (
    Attachment,
    ExtractionStatus,
    ParecerRequest,
    ParecerStatus,
    ParecerStatusHistory,
    ParecerTema,
    ParecerVersion,
    VersionSource,
)

PREFIX = "/api"
TAGS = ["parecer"]

router = APIRouter()


# --- Schemas ---

class AttachmentOut(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    extraction_status: Optional[ExtractionStatus] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ParecerVersionOut(BaseModel):
    id: uuid.UUID
    version_number: int
    source: VersionSource
    content_tiptap: Optional[dict] = None
    content_html: Optional[str] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ParecerRequestOut(BaseModel):
    id: uuid.UUID
    municipio_id: Optional[uuid.UUID] = None
    assigned_to: Optional[uuid.UUID] = None
    subject: Optional[str] = None
    sender_email: Optional[str] = None
    status: ParecerStatus
    tema: Optional[ParecerTema] = None
    numero_parecer: Optional[str] = None
    extraction_status: Optional[ExtractionStatus] = None
    municipio_nome: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_parecer(cls, pr: ParecerRequest) -> "ParecerRequestOut":
        data = cls.model_validate(pr).model_dump()
        classificacao = pr.classificacao or {}
        data["municipio_nome"] = classificacao.get("municipio") or None
        return cls(**data)


class ParecerRequestDetail(ParecerRequestOut):
    extracted_text: Optional[str] = None
    attachments: list[AttachmentOut] = []
    versions: list[ParecerVersionOut] = []


class PaginatedParecerRequests(BaseModel):
    items: list[ParecerRequestOut]
    total: int
    limit: int
    offset: int


# --- Endpoints ---

@router.get("/parecer-requests", response_model=PaginatedParecerRequests)
async def list_parecer_requests(
    status: Optional[ParecerStatus] = Query(default=None),
    tema: Optional[ParecerTema] = Query(default=None),
    municipio_id: Optional[uuid.UUID] = Query(default=None),
    remetente: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> PaginatedParecerRequests:
    base_filters = []

    if status is not None:
        base_filters.append(ParecerRequest.status == status)
    if tema is not None:
        base_filters.append(ParecerRequest.tema == tema)
    if municipio_id is not None:
        base_filters.append(ParecerRequest.municipio_id == municipio_id)
    if remetente is not None:
        base_filters.append(ParecerRequest.sender_email.ilike(f"%{remetente}%"))

    count_query = select(func.count()).select_from(ParecerRequest).where(*base_filters)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = (
        select(ParecerRequest)
        .where(*base_filters)
        .order_by(ParecerRequest.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedParecerRequests(
        items=[ParecerRequestOut.from_parecer(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/parecer-requests/{id}", response_model=ParecerRequestDetail)
async def get_parecer_request(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ParecerRequestDetail:
    result = await db.execute(
        select(ParecerRequest)
        .options(
            selectinload(ParecerRequest.attachments),
            selectinload(ParecerRequest.versions),
        )
        .where(ParecerRequest.id == id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Parecer request nao encontrado")

    return ParecerRequestDetail.model_validate(item)


@router.post("/parecer-requests/{id}/retry-extraction", response_model=ParecerRequestOut)
async def retry_extraction(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ParecerRequestOut:
    result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Parecer request nao encontrado")

    if item.extraction_status != ExtractionStatus.failed:
        raise HTTPException(
            status_code=400,
            detail="Retry so permitido para extractions com status 'failed'",
        )

    item.extraction_status = None
    item.extracted_text = None
    await db.commit()
    await db.refresh(item)

    return ParecerRequestOut.model_validate(item)


@router.delete("/parecer-requests/{id}", status_code=204)
async def delete_parecer(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Parecer nao encontrado")

    await db.execute(
        ParecerVersion.__table__.delete().where(ParecerVersion.request_id == id)
    )
    await db.execute(
        ParecerStatusHistory.__table__.delete().where(ParecerStatusHistory.request_id == id)
    )
    await db.execute(
        Attachment.__table__.delete().where(Attachment.request_id == id)
    )
    await db.delete(item)
    await db.commit()
