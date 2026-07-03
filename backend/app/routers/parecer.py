import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.parecer import (
    Attachment,
    PeerReview,
    ParecerRequest,
    ParecerStatus,
    ParecerStatusHistory,
    ParecerTema,
    ParecerVersion,
    ExtractionStatus,
    VersionSource,
)
from app.services.notification import parecer_ws_manager
from app.utils.auth_guard import require_admin

PREFIX = "/api"
TAGS = ["parecer"]

router = APIRouter()
ws_router = APIRouter()

bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"


def _require_admin(credentials: HTTPAuthorizationCredentials | None) -> None:
    """Garante que o requisitante é admin (validação server-side, não só no front)."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Nao autenticado")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem excluir pareceres")


@ws_router.websocket("/ws/pareceres")
async def ws_pareceres(websocket: WebSocket) -> None:
    await parecer_ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        parecer_ws_manager.disconnect(websocket)


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
    reprocess_instructions: Optional[str] = None
    created_by: Optional[uuid.UUID] = None
    created_by_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ParecerRequestOut(BaseModel):
    id: uuid.UUID
    municipio_id: Optional[uuid.UUID] = None
    assigned_to: Optional[uuid.UUID] = None
    # Agrupador de rodadas — o frontend usa para o badge "rodada N/M" quando a mesma
    # thread tem vários requests "irmãos".
    gmail_thread_id: Optional[str] = None
    subject: Optional[str] = None
    sender_email: Optional[str] = None
    status: ParecerStatus
    tema: Optional[ParecerTema] = None
    numero_parecer: Optional[str] = None
    extraction_status: Optional[ExtractionStatus] = None
    municipio_nome: Optional[str] = None
    # Última nota do parecer_status_history para os status terminais negativos
    # (`devolvido`, `erro`). Permite ao advogado ver no card por que a IA
    # não conseguiu gerar o parecer, sem precisar abrir a timeline.
    motivo: Optional[str] = None
    # Nome de quem enviou o parecer ao cliente (só quando status=enviado). Derivado do
    # histórico de status (transição para 'enviado'), sem novo campo no banco.
    enviado_por: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_parecer(cls, pr: ParecerRequest) -> "ParecerRequestOut":
        data = cls.model_validate(pr).model_dump()
        classificacao = pr.classificacao or {}
        data["municipio_nome"] = classificacao.get("municipio") or None
        data["motivo"] = _latest_motivo(pr) if pr.status in _STATUS_COM_MOTIVO else None
        data["enviado_por"] = _enviado_por(pr) if pr.status == ParecerStatus.enviado else None
        return cls(**data)


_STATUS_COM_MOTIVO = {ParecerStatus.devolvido, ParecerStatus.erro}


def _latest_motivo(pr: ParecerRequest) -> Optional[str]:
    """Última nota do status_history — explica o motivo de devolvido/erro."""
    history = pr.status_history or []
    if not history:
        return None
    # status_history vem ordenado por created_at asc; o último é o mais recente.
    latest = history[-1]
    return (latest.notes or None) if latest.to_status == pr.status else None


def _enviado_por(pr: ParecerRequest) -> Optional[str]:
    """Nome de quem realizou o envio — última transição para 'enviado' no histórico."""
    for h in reversed(pr.status_history or []):
        if h.to_status == ParecerStatus.enviado:
            return h.changed_by_user.name if h.changed_by_user else None
    return None


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
    municipio: Optional[str] = Query(default=None),
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
    if municipio is not None:
        base_filters.append(
            ParecerRequest.classificacao["municipio"].astext.ilike(f"%{municipio}%")
        )
    if remetente is not None:
        base_filters.append(ParecerRequest.sender_email.ilike(f"%{remetente}%"))

    count_query = select(func.count()).select_from(ParecerRequest).where(*base_filters)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = (
        select(ParecerRequest)
        .where(*base_filters)
        .options(selectinload(ParecerRequest.status_history).selectinload(ParecerStatusHistory.changed_by_user))
        .order_by(ParecerRequest.created_at.desc())
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


# Declarada ANTES de "/parecer-requests/{id}" — senão o converter de UUID de {id}
# tentaria casar "municipios" e devolveria 422.
@router.get("/parecer-requests/municipios", response_model=list[str])
async def list_municipios(db: AsyncSession = Depends(get_db)) -> list[str]:
    """Lista distinta dos municípios detectados pela IA (classificacao->>'municipio'),
    para alimentar o filtro da lista de pareceres. Município real vem da classificação,
    não da tabela `municipios` (que tem placeholders SP)."""
    from sqlalchemy import literal_column

    mun_expr = literal_column("classificacao->>'municipio'")
    result = await db.execute(
        select(mun_expr)
        .select_from(ParecerRequest)
        .where(mun_expr.isnot(None))
        .distinct()
        .order_by(mun_expr)
    )
    return [row[0] for row in result.all() if row[0]]


@router.get("/parecer-requests/{id}", response_model=ParecerRequestDetail)
async def get_parecer_request(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ParecerRequestDetail:
    from app.models.user import User

    result = await db.execute(
        select(ParecerRequest)
        .options(
            selectinload(ParecerRequest.attachments),
            selectinload(ParecerRequest.versions),
            selectinload(ParecerRequest.status_history).selectinload(ParecerStatusHistory.changed_by_user),
        )
        .where(ParecerRequest.id == id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Parecer request nao encontrado")

    user_ids = {v.created_by for v in item.versions if v.created_by}
    user_names: dict[uuid.UUID, str] = {}
    if user_ids:
        users_result = await db.execute(select(User.id, User.name).where(User.id.in_(user_ids)))
        user_names = {row.id: row.name for row in users_result}

    detail = ParecerRequestDetail.model_validate(item)
    detail.versions = [
        v.model_copy(update={"created_by_name": user_names.get(v.created_by)})
        for v in detail.versions
    ]
    detail.motivo = _latest_motivo(item) if item.status in _STATUS_COM_MOTIVO else None
    detail.enviado_por = _enviado_por(item) if item.status == ParecerStatus.enviado else None
    classificacao = item.classificacao or {}
    detail.municipio_nome = classificacao.get("municipio") or None
    return detail


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


@router.post("/parecer-requests/{id}/reprocess", response_model=ParecerRequestOut)
async def reprocess_parecer(
    id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_admin),
) -> ParecerRequestOut:
    """
    Redispara o pipeline P1→P2 para um request que falhou (status=erro).

    Usado quando o erro foi transitório (ex.: limite de API, timeout) e o email
    é, de fato, uma consulta jurídica. O texto extraído já está no banco, então
    não é preciso reimportar o email.
    """
    result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Parecer request nao encontrado")

    if item.status != ParecerStatus.erro:
        raise HTTPException(
            status_code=400,
            detail="Reprocessamento so permitido para pareceres com status 'erro'",
        )

    if not item.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="Sem texto extraido para reprocessar — refaca a extracao primeiro",
        )

    old_status = item.status
    item.status = ParecerStatus.pendente
    db.add(
        ParecerStatusHistory(
            request_id=item.id,
            from_status=old_status,
            to_status=ParecerStatus.pendente,
            notes="Reprocessamento manual solicitado",
        )
    )
    await db.commit()
    await db.refresh(item)

    from app.services.pipeline import process_parecer_pipeline
    background_tasks.add_task(process_parecer_pipeline, str(item.id))

    return ParecerRequestOut.model_validate(item)


@router.delete("/parecer-requests/{id}", status_code=204)
async def delete_parecer(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> None:
    """Exclui um parecer. Restrito a administradores (auditoria — Erro 1) e vedado
    para pareceres já enviados."""
    _require_admin(credentials)

    result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Parecer nao encontrado")

    if item.status == ParecerStatus.enviado:
        raise HTTPException(status_code=400, detail="Nao e possivel excluir um parecer ja enviado")

    # Apaga filhos antes do pai (peer_reviews inclusa — senao viola FK ao excluir
    # pareceres que passaram por revisao entre pares).
    await db.execute(
        PeerReview.__table__.delete().where(PeerReview.request_id == id)
    )
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
