from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy import and_, func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.parecer import ParecerRequest, ParecerStatus
from app.models.user import User
from app.schemas.dashboard import (
    AdvogadoItem,
    MunicipioItem,
    OldestParecer,
    PareceresOverview,
    PipelineStage,
)

PREFIX = "/api"
TAGS = ["dashboard"]

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"


def _require_user(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")


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

    # Por município (top 6, apenas abertos) — agrupado pelo nome detectado pela IA
    _mun_expr = literal_column("classificacao->>'municipio'")
    mun_q = await db.execute(
        select(
            _mun_expr.label("municipio_nome"),
            func.count().label("cnt"),
        )
        .select_from(ParecerRequest)
        .where(ParecerRequest.status.in_(_ABERTOS_STATUSES))
        .group_by(_mun_expr)
        .order_by(func.count().desc())
        .limit(6)
    )
    por_municipio = [
        MunicipioItem(
            municipio_id=None,
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
        select(ParecerRequest)
        .where(ParecerRequest.status.in_(_ABERTOS_STATUSES))
        .order_by(ParecerRequest.created_at.asc())
        .limit(5)
    )
    mais_antigos = [
        OldestParecer(
            id=pr.id,
            subject=pr.subject,
            status=pr.status.value,
            municipio_nome=(pr.classificacao or {}).get("municipio"),
            created_at=pr.created_at,
            dias_aberto=max(0, (now - pr.created_at).days),
        )
        for pr in antigos_q.scalars().all()
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
