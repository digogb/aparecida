"""
Export & approval router — auto-discovered by main.py.

Endpoints:
  POST /parecer-requests/{id}/approve
  POST /parecer-requests/{id}/approve-and-send
  POST /parecer-requests/{id}/export/docx
  POST /parecer-requests/{id}/export/pdf
  POST /parecer-requests/{id}/return
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.parecer import (
    ParecerRequest,
    ParecerStatus,
    ParecerStatusHistory,
    ParecerVersion,
)
from app.services.email_sender import send_parecer
from app.services.export_service import to_docx, to_pdf

PREFIX = "/api"
TAGS = ["export"]

router = APIRouter()
bearer = HTTPBearer()
JWT_ALGORITHM = "HS256"


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

async def _get_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    """Extract user id from JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("missing sub")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _load_request_with_versions(
    request_id: uuid.UUID, db: AsyncSession
) -> ParecerRequest:
    result = await db.execute(
        select(ParecerRequest)
        .options(selectinload(ParecerRequest.versions))
        .where(ParecerRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Parecer request nao encontrado")
    return req


def _latest_version(req: ParecerRequest) -> ParecerVersion:
    if not req.versions:
        raise HTTPException(
            status_code=400,
            detail="Parecer request sem versoes — gere uma versao antes de exportar",
        )
    return max(req.versions, key=lambda v: v.version_number)


async def _transition_status(
    req: ParecerRequest,
    to_status: ParecerStatus,
    db: AsyncSession,
    changed_by: str | None = None,
    notes: str | None = None,
) -> None:
    old_status = req.status
    req.status = to_status
    db.add(
        ParecerStatusHistory(
            request_id=req.id,
            from_status=old_status,
            to_status=to_status,
            changed_by=changed_by,
            notes=notes,
        )
    )
    await db.commit()
    await db.refresh(req)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ReturnBody(BaseModel):
    observacoes: str


class StatusOut(BaseModel):
    id: uuid.UUID
    status: ParecerStatus
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/parecer-requests/{id}/approve",
    response_model=StatusOut,
)
async def approve(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(_get_user_id),
) -> StatusOut:
    """Approve a parecer (transition to 'aprovado')."""
    req = await _load_request_with_versions(id, db)

    allowed = {ParecerStatus.em_revisao, ParecerStatus.gerado, ParecerStatus.devolvido}
    if req.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Nao e possivel aprovar um parecer com status '{req.status.value}'",
        )

    await _transition_status(
        req, ParecerStatus.aprovado, db, changed_by=user_id, notes="Parecer aprovado"
    )
    return StatusOut(id=req.id, status=req.status, message="Parecer aprovado com sucesso")


@router.post(
    "/parecer-requests/{id}/approve-and-send",
    response_model=StatusOut,
)
async def approve_and_send(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(_get_user_id),
) -> StatusOut:
    """Approve and immediately send the parecer by email."""
    req = await _load_request_with_versions(id, db)

    allowed = {ParecerStatus.em_revisao, ParecerStatus.gerado, ParecerStatus.devolvido}
    if req.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Nao e possivel aprovar um parecer com status '{req.status.value}'",
        )

    # Approve first
    await _transition_status(
        req, ParecerStatus.aprovado, db, changed_by=user_id, notes="Parecer aprovado"
    )

    # Generate DOCX and send
    version = _latest_version(req)
    docx_bytes = await to_docx(req, version, db)
    await send_parecer(req, docx_bytes, db, changed_by_id=user_id)

    return StatusOut(
        id=req.id, status=req.status, message="Parecer aprovado e enviado com sucesso"
    )


@router.post("/parecer-requests/{id}/export/docx")
async def export_docx(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(_get_user_id),
) -> Response:
    """Export the latest version as DOCX."""
    req = await _load_request_with_versions(id, db)
    version = _latest_version(req)
    docx_bytes = await to_docx(req, version, db)

    filename = f"Parecer_{req.numero_parecer or 'SN'}.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        },
    )


@router.post("/parecer-requests/{id}/export/pdf")
async def export_pdf(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(_get_user_id),
) -> Response:
    """Export the latest version as PDF."""
    req = await _load_request_with_versions(id, db)
    version = _latest_version(req)
    pdf_bytes = await to_pdf(req, version, db)

    filename = f"Parecer_{req.numero_parecer or 'SN'}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        },
    )


@router.post(
    "/parecer-requests/{id}/return",
    response_model=StatusOut,
)
async def return_parecer(
    id: uuid.UUID,
    body: ReturnBody,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(_get_user_id),
) -> StatusOut:
    """Return a parecer for revision (transition to 'devolvido')."""
    req = await _load_request_with_versions(id, db)

    allowed = {ParecerStatus.em_revisao, ParecerStatus.gerado, ParecerStatus.aprovado}
    if req.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Nao e possivel devolver um parecer com status '{req.status.value}'",
        )

    await _transition_status(
        req,
        ParecerStatus.devolvido,
        db,
        changed_by=user_id,
        notes=body.observacoes,
    )
    return StatusOut(
        id=req.id, status=req.status, message="Parecer devolvido para revisao"
    )
