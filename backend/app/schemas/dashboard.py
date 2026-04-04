import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DashboardStats(BaseModel):
    aguardando_revisao: int
    em_revisao: int
    movimentacoes_nao_lidas: int
    tarefas_urgentes: int
    concluidas_semana: int
    enviados_total: int


class DashboardAlert(BaseModel):
    id: str
    type: str  # "parecer_atrasado" | "intimacao_nao_lida" | "prazo_proximo"
    urgency: str  # "high" | "medium"
    title: str
    description: str
    ref_id: Optional[str] = None
    ref_path: Optional[str] = None


class DashboardAlertsResponse(BaseModel):
    alerts: list[DashboardAlert]


class RecentParecer(BaseModel):
    id: uuid.UUID
    subject: Optional[str] = None
    status: str
    municipio_nome: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecentMovement(BaseModel):
    id: uuid.UUID
    process_number: str
    type: str
    tipo_documento: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}


class DashboardRecent(BaseModel):
    pareceres: list[RecentParecer]
    movimentacoes: list[RecentMovement]


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
