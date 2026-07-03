import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# --- Pareceres Overview (dashboard focado em pareceres) ---

class PipelineStage(BaseModel):
    status: str
    label: str
    count: int


class MunicipioItem(BaseModel):
    municipio_id: Optional[uuid.UUID] = None
    municipio_nome: str
    count: int


class AdvogadoItem(BaseModel):
    user_id: Optional[uuid.UUID] = None
    user_name: str
    count: int


class OldestParecer(BaseModel):
    id: uuid.UUID
    subject: Optional[str] = None
    status: str
    municipio_nome: Optional[str] = None
    created_at: datetime
    dias_aberto: int

    model_config = {"from_attributes": True}


class PareceresOverview(BaseModel):
    pipeline: list[PipelineStage]
    por_municipio: list[MunicipioItem]
    por_advogado: list[AdvogadoItem]
    mais_antigos: list[OldestParecer]
    total_abertos: int
    concluidos_semana: int
    enviados_semana: int
    enviados_mes: int
