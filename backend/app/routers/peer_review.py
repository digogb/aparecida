"""
Router para revisão por pares (peer review) de pareceres.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.parecer import (
    ParecerRequest,
    ParecerStatus,
    ParecerStatusHistory,
    ParecerVersion,
    PeerReview,
    PeerReviewStatus,
    VersionSource,
)
from app.models.user import User, UserRole
from app.schemas.peer_review import (
    PeerReviewCreateIn,
    PeerReviewListItem,
    PeerReviewOut,
    PeerReviewRespondIn,
)
from app.schemas.user import UserOut
from app.services.notification import (
    notify_peer_review_completed,
    notify_peer_review_requested,
)

PREFIX = "/api"
TAGS = ["peer-review"]

router = APIRouter()

bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"


def _require_user_id(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")


def _peer_review_to_out(pr: PeerReview) -> PeerReviewOut:
    return PeerReviewOut(
        id=pr.id,
        request_id=pr.request_id,
        version_id=pr.version_id,
        requested_by=pr.requested_by,
        requested_by_name=pr.requester.name if pr.requester else "",
        reviewer_id=pr.reviewer_id,
        reviewer_name=pr.reviewer.name if pr.reviewer else "",
        status=pr.status,
        trechos_marcados=pr.trechos_marcados,
        observacoes=pr.observacoes,
        resposta_geral=pr.resposta_geral,
        resposta_trechos=pr.resposta_trechos,
        result_version_id=pr.result_version_id,
        created_at=pr.created_at,
        completed_at=pr.completed_at,
    )


def _peer_review_to_list_item(pr: PeerReview) -> PeerReviewListItem:
    return PeerReviewListItem(
        id=pr.id,
        request_id=pr.request_id,
        requested_by=pr.requested_by,
        requested_by_name=pr.requester.name if pr.requester else "",
        reviewer_id=pr.reviewer_id,
        reviewer_name=pr.reviewer.name if pr.reviewer else "",
        status=pr.status,
        trechos_marcados=pr.trechos_marcados,
        observacoes=pr.observacoes,
        resposta_geral=pr.resposta_geral,
        resposta_trechos=pr.resposta_trechos,
        created_at=pr.created_at,
        completed_at=pr.completed_at,
    )


async def _load_peer_review(
    review_id: uuid.UUID,
    db: AsyncSession,
) -> PeerReview:
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(PeerReview)
        .options(
            selectinload(PeerReview.requester),
            selectinload(PeerReview.reviewer),
        )
        .where(PeerReview.id == review_id)
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        raise HTTPException(status_code=404, detail="Revisão não encontrada")
    return pr


# ---------------------------------------------------------------------------
# Listar advogados disponíveis para revisão
# ---------------------------------------------------------------------------

@router.get("/users/lawyers", response_model=list[UserOut])
async def list_lawyers(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[UserOut]:
    """Retorna todos os advogados ativos (excluindo o usuário atual)."""
    current_user_id = _require_user_id(credentials)
    result = await db.execute(
        select(User).where(
            User.is_active == True,
            User.role.in_([UserRole.advogado, UserRole.admin]),
            User.id != uuid.UUID(current_user_id),
        ).order_by(User.name)
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Criar solicitação de revisão
# ---------------------------------------------------------------------------

@router.post(
    "/parecer-requests/{id}/peer-review",
    response_model=PeerReviewOut,
)
async def create_peer_review(
    id: uuid.UUID,
    body: PeerReviewCreateIn,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> PeerReviewOut:
    """Cria uma solicitação de revisão por pares."""
    from sqlalchemy.orm import selectinload

    current_user_id = _require_user_id(credentials)

    # Verificar que o parecer existe
    pr_result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == id)
    )
    parecer = pr_result.scalar_one_or_none()
    if parecer is None:
        raise HTTPException(status_code=404, detail="Parecer não encontrado")

    # Verificar que o revisor existe
    reviewer_result = await db.execute(
        select(User).where(User.id == body.reviewer_id, User.is_active == True)
    )
    reviewer = reviewer_result.scalar_one_or_none()
    if reviewer is None:
        raise HTTPException(status_code=404, detail="Revisor não encontrado")

    # Buscar a versão mais recente
    version_result = await db.execute(
        select(ParecerVersion)
        .where(ParecerVersion.request_id == id)
        .order_by(ParecerVersion.version_number.desc())
        .limit(1)
    )
    latest_version = version_result.scalar_one_or_none()
    if latest_version is None:
        raise HTTPException(status_code=400, detail="Nenhuma versão disponível para revisar")

    # Criar peer review
    peer_review = PeerReview(
        request_id=id,
        version_id=latest_version.id,
        requested_by=uuid.UUID(current_user_id),
        reviewer_id=body.reviewer_id,
        status=PeerReviewStatus.pendente,
        trechos_marcados=[t.model_dump() for t in body.trechos_marcados],
        observacoes=body.observacoes,
    )
    db.add(peer_review)

    # Atualizar status do parecer para em_revisao
    old_status = parecer.status
    parecer.status = ParecerStatus.em_revisao
    db.add(ParecerStatusHistory(
        request_id=parecer.id,
        from_status=old_status,
        to_status=ParecerStatus.em_revisao,
        changed_by=uuid.UUID(current_user_id),
        notes=f"Revisão solicitada para {reviewer.name}",
    ))

    await db.flush()

    # Notificar o revisor
    await notify_peer_review_requested(db, peer_review, parecer)

    await db.commit()

    # Recarregar com relacionamentos
    peer_review = await _load_peer_review(peer_review.id, db)
    return _peer_review_to_out(peer_review)


# ---------------------------------------------------------------------------
# Listar revisões de um parecer
# ---------------------------------------------------------------------------

@router.get(
    "/parecer-requests/{id}/peer-reviews",
    response_model=list[PeerReviewListItem],
)
async def list_peer_reviews(
    id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[PeerReviewListItem]:
    """Lista todas as revisões de um parecer."""
    from sqlalchemy.orm import selectinload

    _require_user_id(credentials)

    result = await db.execute(
        select(PeerReview)
        .options(
            selectinload(PeerReview.requester),
            selectinload(PeerReview.reviewer),
        )
        .where(PeerReview.request_id == id)
        .order_by(PeerReview.created_at.desc())
    )
    reviews = result.scalars().all()
    return [_peer_review_to_list_item(r) for r in reviews]


# ---------------------------------------------------------------------------
# Minhas revisões pendentes
# ---------------------------------------------------------------------------

@router.get(
    "/peer-reviews/pending",
    response_model=list[PeerReviewOut],
)
async def list_pending_reviews(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[PeerReviewOut]:
    """Lista revisões pendentes atribuídas ao usuário atual."""
    from sqlalchemy.orm import selectinload

    current_user_id = _require_user_id(credentials)

    result = await db.execute(
        select(PeerReview)
        .options(
            selectinload(PeerReview.requester),
            selectinload(PeerReview.reviewer),
        )
        .where(
            PeerReview.reviewer_id == uuid.UUID(current_user_id),
            PeerReview.status == PeerReviewStatus.pendente,
        )
        .order_by(PeerReview.created_at.desc())
    )
    reviews = result.scalars().all()
    return [_peer_review_to_out(r) for r in reviews]


# ---------------------------------------------------------------------------
# Responder revisão (revisor envia feedback)
# ---------------------------------------------------------------------------

@router.post(
    "/peer-reviews/{review_id}/respond",
    response_model=PeerReviewOut,
)
async def respond_peer_review(
    review_id: uuid.UUID,
    body: PeerReviewRespondIn,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> PeerReviewOut:
    """O revisor envia sua resposta e uma nova versão é criada."""
    current_user_id = _require_user_id(credentials)

    peer_review = await _load_peer_review(review_id, db)

    if str(peer_review.reviewer_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Apenas o revisor pode responder esta revisão")

    if peer_review.status != PeerReviewStatus.pendente:
        raise HTTPException(status_code=400, detail="Esta revisão não está mais pendente")

    # Buscar o parecer
    pr_result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == peer_review.request_id)
    )
    parecer = pr_result.scalar_one_or_none()
    if parecer is None:
        raise HTTPException(status_code=404, detail="Parecer não encontrado")

    # Buscar a versão original que foi revisada
    src_result = await db.execute(
        select(ParecerVersion).where(ParecerVersion.id == peer_review.version_id)
    )
    src_version = src_result.scalar_one_or_none()

    # Calcular próximo número de versão
    next_num_result = await db.execute(
        select(func.coalesce(func.max(ParecerVersion.version_number), 0))
        .where(ParecerVersion.request_id == parecer.id)
    )
    next_num = next_num_result.scalar_one() + 1

    # Montar notas do revisor a partir das respostas
    notas: list[str] = []
    if body.resposta_geral:
        notas.append(f"Revisão de {peer_review.reviewer.name}: {body.resposta_geral}")
    for rt in body.resposta_trechos:
        nota = f'Trecho "{rt.original[:80]}..." → Sugestão: "{rt.sugestao}"'
        if rt.comentario:
            nota += f" ({rt.comentario})"
        notas.append(nota)

    # Criar nova versão com as notas do revisor
    new_version = ParecerVersion(
        request_id=parecer.id,
        version_number=next_num,
        source=VersionSource.peer_review,
        content_tiptap=src_version.content_tiptap if src_version else None,
        content_html=src_version.content_html if src_version else None,
        prompt_version=src_version.prompt_version if src_version else None,
        citacoes_verificar=src_version.citacoes_verificar or [] if src_version else [],
        ressalvas=src_version.ressalvas or [] if src_version else [],
        notas_revisor=notas,
        reprocess_instructions=f"Revisão por pares — {peer_review.reviewer.name}",
        created_by=uuid.UUID(current_user_id),
    )
    db.add(new_version)
    await db.flush()

    # Atualizar peer review
    peer_review.status = PeerReviewStatus.concluida
    peer_review.resposta_geral = body.resposta_geral
    peer_review.resposta_trechos = [rt.model_dump() for rt in body.resposta_trechos]
    peer_review.result_version_id = new_version.id
    peer_review.completed_at = datetime.now(timezone.utc)

    # Voltar status do parecer para em_correcao
    old_status = parecer.status
    parecer.status = ParecerStatus.em_correcao
    db.add(ParecerStatusHistory(
        request_id=parecer.id,
        from_status=old_status,
        to_status=ParecerStatus.em_correcao,
        changed_by=uuid.UUID(current_user_id),
        notes=f"Revisão concluída por {peer_review.reviewer.name}",
    ))

    await db.flush()

    # Notificar o solicitante
    await notify_peer_review_completed(db, peer_review, parecer)

    await db.commit()

    peer_review = await _load_peer_review(review_id, db)
    return _peer_review_to_out(peer_review)


# ---------------------------------------------------------------------------
# Cancelar revisão
# ---------------------------------------------------------------------------

@router.post(
    "/peer-reviews/{review_id}/cancel",
    response_model=PeerReviewOut,
)
async def cancel_peer_review(
    review_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> PeerReviewOut:
    """Cancela uma revisão pendente (apenas o solicitante pode cancelar)."""
    current_user_id = _require_user_id(credentials)

    peer_review = await _load_peer_review(review_id, db)

    if str(peer_review.requested_by) != current_user_id:
        raise HTTPException(status_code=403, detail="Apenas o solicitante pode cancelar esta revisão")

    if peer_review.status != PeerReviewStatus.pendente:
        raise HTTPException(status_code=400, detail="Apenas revisões pendentes podem ser canceladas")

    # Atualizar peer review
    peer_review.status = PeerReviewStatus.cancelada
    peer_review.completed_at = datetime.now(timezone.utc)

    # Buscar o parecer e voltar status para em_correcao
    pr_result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == peer_review.request_id)
    )
    parecer = pr_result.scalar_one_or_none()
    if parecer and parecer.status == ParecerStatus.em_revisao:
        old_status = parecer.status
        parecer.status = ParecerStatus.em_correcao
        db.add(ParecerStatusHistory(
            request_id=parecer.id,
            from_status=old_status,
            to_status=ParecerStatus.em_correcao,
            changed_by=uuid.UUID(current_user_id),
            notes="Revisão por pares cancelada",
        ))

    await db.commit()

    peer_review = await _load_peer_review(review_id, db)
    return _peer_review_to_out(peer_review)
