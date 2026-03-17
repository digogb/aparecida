import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DashboardStats(BaseModel):
    pareceres_pendentes: int
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
    published_at: Optional[datetime] = None
    created_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}


class DashboardRecent(BaseModel):
    pareceres: list[RecentParecer]
    movimentacoes: list[RecentMovement]
