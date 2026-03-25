from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.parecer import PeerReviewStatus


class TrechoMarcado(BaseModel):
    texto: str
    instrucao: str = ""


class RespostaTrecho(BaseModel):
    original: str
    sugestao: str
    comentario: str = ""


class PeerReviewCreateIn(BaseModel):
    reviewer_id: uuid.UUID
    trechos_marcados: list[TrechoMarcado] = []
    observacoes: str = ""


class PeerReviewRespondIn(BaseModel):
    resposta_geral: str
    resposta_trechos: list[RespostaTrecho] = []


class PeerReviewOut(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    version_id: uuid.UUID
    requested_by: uuid.UUID
    requested_by_name: str
    reviewer_id: uuid.UUID
    reviewer_name: str
    status: PeerReviewStatus
    trechos_marcados: Optional[list[Any]] = None
    observacoes: Optional[str] = None
    resposta_geral: Optional[str] = None
    resposta_trechos: Optional[list[Any]] = None
    result_version_id: Optional[uuid.UUID] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PeerReviewListItem(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    requested_by: uuid.UUID
    requested_by_name: str
    reviewer_id: uuid.UUID
    reviewer_name: str
    status: PeerReviewStatus
    observacoes: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
