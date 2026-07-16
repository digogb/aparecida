"""
Router para revisão por pares (peer review) de pareceres.
"""
from __future__ import annotations

import copy
import re
import unicodedata
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
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


def _normalize_for_match(text: str) -> str:
    """Normaliza texto para busca fuzzy: unifica aspas, traços, espaços e lowercase."""
    s = unicodedata.normalize("NFC", text)
    s = re.sub(r'[“”„‟″]', '"', s)
    s = re.sub(r'[‘’‚‛′]', "'", s)
    s = re.sub(r'[–—−]', '-', s)
    s = re.sub(r'[\xa0 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _apply_replacements_html(html: str, replacements: list[tuple[str, str]]) -> str:
    """Aplica substituições de texto no HTML, ignorando tags."""
    from html.parser import HTMLParser

    class _TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts: list[tuple[str, bool]] = []  # (content, is_tag)

        def handle_starttag(self, tag, attrs):
            self.parts.append((self.get_starttag_text() or "", True))

        def handle_endtag(self, tag):
            self.parts.append((f"</{tag}>", True))

        def handle_data(self, data):
            self.parts.append((data, False))

        def handle_comment(self, data):
            self.parts.append((f"<!--{data}-->", True))

    parser = _TextExtractor()
    parser.feed(html)

    for original, replacement in replacements:
        norm_orig = _normalize_for_match(original).lower()
        if not norm_orig:
            continue

        text_only = "".join(p for p, is_tag in parser.parts if not is_tag)
        norm_text = _normalize_for_match(text_only).lower()
        idx = norm_text.find(norm_orig)
        if idx == -1:
            continue

        char_count = 0
        new_parts: list[tuple[str, bool]] = []
        replaced = False

        for content, is_tag in parser.parts:
            if is_tag or replaced:
                new_parts.append((content, is_tag))
                continue

            norm_content = _normalize_for_match(content).lower()
            piece_start = char_count
            piece_end = char_count + len(norm_content)

            if not replaced and piece_start <= idx < piece_end:
                local_idx = idx - piece_start
                orig_len_in_norm = len(norm_orig)
                src_start = _map_norm_to_src(content, local_idx)
                src_end = _map_norm_to_src(content, local_idx + orig_len_in_norm)
                new_content = content[:src_start] + replacement + content[src_end:]
                new_parts.append((new_content, False))
                replaced = True
            else:
                new_parts.append((content, is_tag))

            char_count = piece_end

        if replaced:
            parser.parts = new_parts

    return "".join(p for p, _ in parser.parts)


def _map_norm_to_src(text: str, norm_idx: int) -> int:
    """Mapeia posição no texto normalizado para posição no texto original."""
    norm_pos = 0
    prev_was_space = True
    for i, ch in enumerate(text):
        if norm_pos >= norm_idx:
            return i
        is_space = ch in (' ', '\t', '\n', '\r', '\xa0', ' ')
        if is_space:
            if not prev_was_space:
                norm_pos += 1
                prev_was_space = True
        else:
            norm_pos += 1
            prev_was_space = False
    return len(text)


def _apply_replacements_tiptap(
    tiptap: dict | None, replacements: list[tuple[str, str]]
) -> dict | None:
    """Aplica substituições de texto no JSON TipTap, percorrendo text nodes."""
    if not tiptap:
        return tiptap

    result = copy.deepcopy(tiptap)

    for original, replacement in replacements:
        norm_orig = _normalize_for_match(original).lower()
        if not norm_orig:
            continue
        _replace_in_node(result, norm_orig, replacement)

    return result


def _replace_in_node(node: dict, norm_orig: str, replacement: str) -> bool:
    """Tenta substituir o texto em text nodes de um nó TipTap. Retorna True se substituiu."""
    children = node.get("content")
    if not isinstance(children, list):
        return False

    if node.get("type") in ("paragraph", "heading"):
        full_text = ""
        for child in children:
            if child.get("type") == "text" and isinstance(child.get("text"), str):
                full_text += child["text"]

        norm_full = _normalize_for_match(full_text).lower()
        idx = norm_full.find(norm_orig)
        if idx != -1:
            src_start = _map_norm_to_src(full_text, idx)
            src_end = _map_norm_to_src(full_text, idx + len(norm_orig))
            new_full = full_text[:src_start] + replacement + full_text[src_end:]

            # Preserva a estrutura de text nodes: localiza quais nodes cobrem
            # o trecho substituído e reescreve apenas eles.
            offset = 0
            new_children: list[dict] = []
            replaced = False
            for child in children:
                if child.get("type") != "text" or not isinstance(child.get("text"), str):
                    new_children.append(child)
                    continue
                t = child["text"]
                child_start = offset
                child_end = offset + len(t)

                if replaced or child_end <= src_start or child_start >= src_end:
                    new_children.append(child)
                elif child_start <= src_start and child_end >= src_end:
                    # Substituição cabe inteira neste node
                    new_text = t[: src_start - child_start] + replacement + t[src_end - child_start :]
                    new_children.append({**child, "text": new_text})
                    replaced = True
                else:
                    # Substituição cruza nodes — colapsa trecho afetado
                    if child_start <= src_start:
                        prefix = t[: src_start - child_start]
                        new_text = prefix + replacement
                        new_children.append({**child, "text": new_text})
                    elif child_start >= src_start and child_end <= src_end:
                        pass  # node inteiro dentro do trecho — remove
                    else:
                        suffix = t[src_end - child_start :]
                        if suffix:
                            new_children.append({**child, "text": suffix})
                        replaced = True
                offset = child_end

            if not replaced and not new_children:
                new_children = [{"type": "text", "text": new_full}]

            node["content"] = new_children
            return True

    for child in children:
        if _replace_in_node(child, norm_orig, replacement):
            return True

    return False


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
    include_self: bool = Query(default=False),
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[UserOut]:
    """Advogados/admins ativos. Por padrão exclui o usuário atual (uso do peer review,
    onde não se pede revisão a si mesmo); `include_self=true` retorna todos, incluindo o
    próprio usuário (usado no filtro "Enviado por" da lista de pareceres)."""
    current_user_id = _require_user_id(credentials)
    filters = [
        User.is_active.is_(True),
        User.role.in_([UserRole.advogado, UserRole.admin]),
    ]
    if not include_self:
        filters.append(User.id != uuid.UUID(current_user_id))
    result = await db.execute(select(User).where(*filters).order_by(User.name))
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
        select(User).where(User.id == body.reviewer_id, User.is_active.is_(True))
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

    # Montar lista de substituições a partir das sugestões do revisor
    replacements: list[tuple[str, str]] = []
    for rt in body.resposta_trechos:
        if rt.original and rt.sugestao:
            replacements.append((rt.original, rt.sugestao))

    # Aplicar substituições ao conteúdo
    src_html = src_version.content_html if src_version else None
    src_tiptap = src_version.content_tiptap if src_version else None
    if replacements:
        if src_html:
            src_html = _apply_replacements_html(src_html, replacements)
        if src_tiptap:
            src_tiptap = _apply_replacements_tiptap(src_tiptap, replacements)

    new_version = ParecerVersion(
        request_id=parecer.id,
        version_number=next_num,
        source=VersionSource.peer_review,
        content_tiptap=src_tiptap,
        content_html=src_html,
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
