from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.movement import Movement, MovementType, Process
from app.models.municipio import Municipio
from app.models.parecer import ParecerRequest, ParecerStatus
from app.models.task import Column, Task, TaskPriority
from app.schemas.dashboard import (
    DashboardAlert,
    DashboardAlertsResponse,
    DashboardRecent,
    DashboardStats,
    RecentMovement,
    RecentParecer,
)

PREFIX = "/api"
TAGS = ["dashboard"]

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"

_PENDING_STATUSES = [
    ParecerStatus.pendente,
    ParecerStatus.classificado,
    ParecerStatus.gerado,
]
_DONE_COLUMN_POSITIONS = [3, 4]  # "Concluída" e "Arquivada"


def _require_user(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    _require_user(credentials)

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # Aguardando revisão (gerado + em_revisao — ainda não tocados pelo advogado)
    aguardando_q = await db.execute(
        select(func.count()).select_from(ParecerRequest).where(
            ParecerRequest.status.in_([
                ParecerStatus.gerado,
                ParecerStatus.em_revisao,
            ])
        )
    )
    aguardando_revisao = aguardando_q.scalar() or 0

    em_revisao = aguardando_revisao

    # Movimentações não lidas
    nao_lidas_q = await db.execute(
        select(func.count()).select_from(Movement).where(Movement.is_read == False)
    )
    movimentacoes_nao_lidas = nao_lidas_q.scalar() or 0

    # Tarefas urgentes (high priority, not in done/archived columns)
    done_cols_q = await db.execute(
        select(Column.id).where(Column.position.in_(_DONE_COLUMN_POSITIONS))
    )
    done_col_ids = [row[0] for row in done_cols_q.fetchall()]

    urgentes_q = await db.execute(
        select(func.count()).select_from(Task).where(
            and_(
                Task.priority == TaskPriority.high,
                Task.column_id.notin_(done_col_ids) if done_col_ids else True,
            )
        )
    )
    tarefas_urgentes = urgentes_q.scalar() or 0

    # Concluídos na semana (enviado, updated_at nos últimos 7 dias)
    concluidas_q = await db.execute(
        select(func.count()).select_from(ParecerRequest).where(
            and_(
                ParecerRequest.status == ParecerStatus.enviado,
                ParecerRequest.updated_at >= week_ago,
            )
        )
    )
    concluidas_semana = concluidas_q.scalar() or 0

    # Enviados total
    enviados_q = await db.execute(
        select(func.count()).select_from(ParecerRequest).where(
            ParecerRequest.status == ParecerStatus.enviado
        )
    )
    enviados_total = enviados_q.scalar() or 0

    return DashboardStats(
        aguardando_revisao=aguardando_revisao,
        em_revisao=em_revisao,
        movimentacoes_nao_lidas=movimentacoes_nao_lidas,
        tarefas_urgentes=tarefas_urgentes,
        concluidas_semana=concluidas_semana,
        enviados_total=enviados_total,
    )


@router.get("/dashboard/alerts", response_model=DashboardAlertsResponse)
async def get_dashboard_alerts(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> DashboardAlertsResponse:
    _require_user(credentials)

    now = datetime.now(timezone.utc)
    cutoff_48h = now - timedelta(hours=48)
    cutoff_3d = now + timedelta(days=3)

    alerts: list[DashboardAlert] = []

    # Pareceres pendentes há mais de 48h
    atrasados_q = await db.execute(
        select(ParecerRequest).where(
            and_(
                ParecerRequest.status.in_(_PENDING_STATUSES),
                ParecerRequest.created_at <= cutoff_48h,
            )
        ).order_by(ParecerRequest.created_at).limit(5)
    )
    for p in atrasados_q.scalars():
        horas = int((now - p.created_at).total_seconds() / 3600)
        alerts.append(DashboardAlert(
            id=f"parecer_atrasado_{p.id}",
            type="parecer_atrasado",
            urgency="high",
            title="Parecer sem resposta",
            description=f"{p.subject or 'Sem assunto'} — {horas}h sem atualização",
            ref_id=str(p.id),
            ref_path=f"/pareceres/{p.id}",
        ))

    # Intimações não lidas
    intimacoes_q = await db.execute(
        select(Movement).where(
            and_(
                Movement.is_read == False,
                Movement.type == MovementType.intimacao,
            )
        ).order_by(Movement.created_at.desc()).limit(5)
    )
    for m in intimacoes_q.scalars():
        alerts.append(DashboardAlert(
            id=f"intimacao_{m.id}",
            type="intimacao_nao_lida",
            urgency="high",
            title="Intimação não lida",
            description=f"Processo — publicada em {m.published_at.strftime('%d/%m/%Y') if m.published_at else 'data desconhecida'}",
            ref_id=str(m.id),
            ref_path="/movimentacoes",
        ))

    # Tarefas com prazo nos próximos 3 dias
    done_cols_q = await db.execute(
        select(Column.id).where(Column.position.in_(_DONE_COLUMN_POSITIONS))
    )
    done_col_ids = [row[0] for row in done_cols_q.fetchall()]

    prazo_q = await db.execute(
        select(Task).where(
            and_(
                Task.due_date != None,
                Task.due_date <= cutoff_3d,
                Task.due_date >= now,
                Task.column_id.notin_(done_col_ids) if done_col_ids else True,
            )
        ).order_by(Task.due_date).limit(5)
    )
    for t in prazo_q.scalars():
        dias = (t.due_date - now).days
        alerts.append(DashboardAlert(
            id=f"prazo_{t.id}",
            type="prazo_proximo",
            urgency="medium" if dias >= 1 else "high",
            title="Prazo próximo",
            description=f"{t.title} — vence em {dias}d",
            ref_id=str(t.id),
            ref_path="/tarefas",
        ))

    return DashboardAlertsResponse(alerts=alerts)


@router.get("/dashboard/recent", response_model=DashboardRecent)
async def get_dashboard_recent(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> DashboardRecent:
    _require_user(credentials)

    # Últimos 5 pareceres (com join para municipio)
    pareceres_q = await db.execute(
        select(ParecerRequest, Municipio.name.label("municipio_nome"))
        .outerjoin(Municipio, ParecerRequest.municipio_id == Municipio.id)
        .order_by(ParecerRequest.created_at.desc())
        .limit(5)
    )
    pareceres_rows = pareceres_q.all()

    pareceres = [
        RecentParecer(
            id=row.ParecerRequest.id,
            subject=row.ParecerRequest.subject,
            status=row.ParecerRequest.status.value,
            municipio_nome=row.municipio_nome,
            created_at=row.ParecerRequest.created_at,
        )
        for row in pareceres_rows
    ]

    # Últimas 5 movimentações
    movs_q = await db.execute(
        select(Movement, Process.number.label("process_number"))
        .join(Process, Movement.process_id == Process.id)
        .order_by(Movement.created_at.desc())
        .limit(5)
    )
    movs_rows = movs_q.all()

    movimentacoes = [
        RecentMovement(
            id=row.Movement.id,
            process_number=row.process_number or "—",
            type=row.Movement.type.value,
            published_at=row.Movement.published_at,
            created_at=row.Movement.created_at,
            is_read=row.Movement.is_read,
        )
        for row in movs_rows
    ]

    return DashboardRecent(pareceres=pareceres, movimentacoes=movimentacoes)
