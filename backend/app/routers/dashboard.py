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
from app.models.parecer import ParecerRequest, ParecerStatus, PeerReview, PeerReviewStatus
from app.models.task import Column, Task, TaskPriority
from app.models.user import User
from app.schemas.dashboard import (
    AdvogadoItem,
    DashboardAlert,
    DashboardAlertsResponse,
    DashboardRecent,
    DashboardStats,
    MunicipioItem,
    OldestParecer,
    PareceresOverview,
    PipelineStage,
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
    payload = _require_user(credentials)
    current_user_id = payload.get("sub")

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

    # Revisões de parecer solicitadas para o usuário logado
    if current_user_id:
        peer_q = await db.execute(
            select(PeerReview, ParecerRequest, User)
            .join(ParecerRequest, PeerReview.request_id == ParecerRequest.id)
            .join(User, PeerReview.requested_by == User.id)
            .where(
                and_(
                    PeerReview.reviewer_id == current_user_id,
                    PeerReview.status == PeerReviewStatus.pendente,
                )
            )
            .order_by(PeerReview.created_at.desc())
            .limit(5)
        )
        for row in peer_q.all():
            pr = row.PeerReview
            parecer = row.ParecerRequest
            requester = row.User
            numero = parecer.numero_parecer if hasattr(parecer, "numero_parecer") and parecer.numero_parecer else (parecer.subject or str(parecer.id)[:8])
            alerts.append(DashboardAlert(
                id=f"revisao_{pr.id}",
                type="revisao_solicitada",
                urgency="high",
                title=f"Revisão solicitada por {requester.name.split(' ')[0]}",
                description=numero,
                ref_id=str(parecer.id),
                ref_path=f"/pareceres/{parecer.id}",
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
            tipo_documento=(row.Movement.metadata_ or {}).get("tipo_documento"),
            published_at=row.Movement.published_at,
            created_at=row.Movement.created_at,
            is_read=row.Movement.is_read,
        )
        for row in movs_rows
    ]

    return DashboardRecent(pareceres=pareceres, movimentacoes=movimentacoes)


_ABERTOS_STATUSES = [
    ParecerStatus.pendente,
    ParecerStatus.classificado,
    ParecerStatus.gerado,
    ParecerStatus.em_correcao,
    ParecerStatus.em_revisao,
    ParecerStatus.devolvido,
]

_PIPELINE_LABELS = {
    "pendente": "Pendente",
    "classificado": "Classificado",
    "gerado": "Gerado",
    "em_correcao": "Em correção",
    "em_revisao": "Em revisão",
    "devolvido": "Devolvido",
    "aprovado": "Aprovado",
    "enviado": "Enviado",
    "erro": "Erro",
}


@router.get("/dashboard/pareceres-overview", response_model=PareceresOverview)
async def get_pareceres_overview(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> PareceresOverview:
    _require_user(credentials)

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # Pipeline: contagem por status
    pipeline_q = await db.execute(
        select(ParecerRequest.status, func.count().label("cnt"))
        .group_by(ParecerRequest.status)
    )
    status_counts = {row.status: row.cnt for row in pipeline_q.all()}

    pipeline = [
        PipelineStage(
            status=s.value,
            label=_PIPELINE_LABELS.get(s.value, s.value),
            count=status_counts.get(s, 0),
        )
        for s in ParecerStatus
    ]

    total_abertos = sum(status_counts.get(s, 0) for s in _ABERTOS_STATUSES)

    # Por município (top 6, apenas abertos)
    mun_q = await db.execute(
        select(
            Municipio.id.label("municipio_id"),
            Municipio.name.label("municipio_nome"),
            func.count().label("cnt"),
        )
        .select_from(ParecerRequest)
        .outerjoin(Municipio, ParecerRequest.municipio_id == Municipio.id)
        .where(ParecerRequest.status.in_(_ABERTOS_STATUSES))
        .group_by(Municipio.id, Municipio.name)
        .order_by(func.count().desc())
        .limit(6)
    )
    por_municipio = [
        MunicipioItem(
            municipio_id=row.municipio_id,
            municipio_nome=row.municipio_nome or "Sem município",
            count=row.cnt,
        )
        for row in mun_q.all()
    ]

    # Por advogado (assigned_to, apenas abertos)
    adv_q = await db.execute(
        select(
            User.id.label("user_id"),
            User.name.label("user_name"),
            func.count().label("cnt"),
        )
        .select_from(ParecerRequest)
        .outerjoin(User, ParecerRequest.assigned_to == User.id)
        .where(ParecerRequest.status.in_(_ABERTOS_STATUSES))
        .group_by(User.id, User.name)
        .order_by(func.count().desc())
    )
    por_advogado = [
        AdvogadoItem(
            user_id=row.user_id,
            user_name=row.user_name or "Não atribuído",
            count=row.cnt,
        )
        for row in adv_q.all()
    ]

    # 5 pareceres mais antigos ainda abertos
    antigos_q = await db.execute(
        select(ParecerRequest, Municipio.name.label("municipio_nome"))
        .outerjoin(Municipio, ParecerRequest.municipio_id == Municipio.id)
        .where(ParecerRequest.status.in_(_ABERTOS_STATUSES))
        .order_by(ParecerRequest.created_at.asc())
        .limit(5)
    )
    mais_antigos = [
        OldestParecer(
            id=row.ParecerRequest.id,
            subject=row.ParecerRequest.subject,
            status=row.ParecerRequest.status.value,
            municipio_nome=row.municipio_nome,
            created_at=row.ParecerRequest.created_at,
            dias_aberto=max(0, (now - row.ParecerRequest.created_at).days),
        )
        for row in antigos_q.all()
    ]

    # Concluídos na semana (enviados ou aprovados nos últimos 7 dias)
    concluidos_q = await db.execute(
        select(func.count()).select_from(ParecerRequest).where(
            and_(
                ParecerRequest.status.in_([ParecerStatus.enviado, ParecerStatus.aprovado]),
                ParecerRequest.updated_at >= week_ago,
            )
        )
    )
    concluidos_semana = concluidos_q.scalar() or 0

    return PareceresOverview(
        pipeline=pipeline,
        por_municipio=por_municipio,
        por_advogado=por_advogado,
        mais_antigos=mais_antigos,
        total_abertos=total_abertos,
        concluidos_semana=concluidos_semana,
    )
