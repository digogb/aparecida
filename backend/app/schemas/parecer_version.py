from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.models.parecer import ParecerModelo, ParecerTema, VersionSource


class ClassifyOut(BaseModel):
    tema: ParecerTema
    subtema: Optional[str] = None
    modelo_parecer: ParecerModelo
    municipio_detectado: Optional[str] = None
    confianca: Optional[float] = None
    request_id: uuid.UUID
    status: str
    classificacao: Optional[dict[str, Any]] = None


class ReprocessIn(BaseModel):
    observacoes: str


class TrechoRevisado(BaseModel):
    original: str
    revisado: str
    secao: str


class PreviewCorrectionOut(BaseModel):
    secoes_alteradas: list[str]
    revisado: dict[str, str]
    trechos: list[TrechoRevisado] = []
    notas_revisor: list[Any] = []
    citacoes_verificar: list[Any] = []


class ApplyCorrectionIn(BaseModel):
    secoes_aprovadas: dict[str, str]
    observacoes: str = ""
    notas_revisor: list[str] = []
    citacoes_verificar: list[Any] = []


class ParecerVersionDetail(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    version_number: int
    source: VersionSource
    content_tiptap: Optional[dict[str, Any]] = None
    content_html: Optional[str] = None
    reprocess_instructions: Optional[str] = None
    prompt_version: Optional[str] = None
    citacoes_verificar: Optional[list[Any]] = None
    ressalvas: Optional[list[Any]] = None
    notas_revisor: Optional[list[Any]] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParecerVersionListItem(BaseModel):
    id: uuid.UUID
    version_number: int
    source: VersionSource
    created_by: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}
