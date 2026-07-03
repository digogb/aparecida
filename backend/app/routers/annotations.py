"""Anotações inline dos pareceres (marca de trecho + questionamento).

Substitui o fluxo de peer review + notificação (decisão do cliente 03/07/2026):
qualquer advogado marca um trecho e escreve uma pergunta; todos veem o realce
(cor por autor) e o questionamento no hint ao abrir o parecer no editor.

Auth: qualquer usuário autenticado cria/lista; apagar só o autor ou um admin.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.parecer import ParecerAnnotation, ParecerRequest
from app.models.user import User
from app.services.annotation_colors import color_for

PREFIX = "/api"
TAGS = ["annotations"]

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"


def _auth(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Nao autenticado")
    try:
        return jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")


class AnnotationCreate(BaseModel):
    trecho_texto: str
    questionamento: str


class AnnotationOut(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str | None = None
    author_color: str
    trecho_texto: str
    questionamento: str
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/parecer-requests/{id}/annotations", response_model=list[AnnotationOut])
async def list_annotations(
    id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[AnnotationOut]:
    _auth(credentials)
    result = await db.execute(
        select(ParecerAnnotation, User.name, User.email)
        .outerjoin(User, User.id == ParecerAnnotation.author_id)
        .where(ParecerAnnotation.request_id == id)
        .order_by(ParecerAnnotation.created_at)
    )
    out: list[AnnotationOut] = []
    for ann, name, email in result.all():
        out.append(
            AnnotationOut(
                id=ann.id,
                request_id=ann.request_id,
                author_id=ann.author_id,
                author_name=name,
                author_color=color_for(email, ann.author_id),
                trecho_texto=ann.trecho_texto,
                questionamento=ann.questionamento,
                created_at=ann.created_at,
            )
        )
    return out


@router.post("/parecer-requests/{id}/annotations", response_model=AnnotationOut, status_code=201)
async def create_annotation(
    id: uuid.UUID,
    body: AnnotationCreate,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> AnnotationOut:
    payload = _auth(credentials)
    author_id = uuid.UUID(payload["sub"])

    trecho = (body.trecho_texto or "").strip()
    questionamento = (body.questionamento or "").strip()
    if not trecho:
        raise HTTPException(status_code=400, detail="Selecione um trecho para anotar")
    if not questionamento:
        raise HTTPException(status_code=400, detail="Escreva o questionamento")

    pr = (await db.execute(select(ParecerRequest).where(ParecerRequest.id == id))).scalar_one_or_none()
    if pr is None:
        raise HTTPException(status_code=404, detail="Parecer nao encontrado")

    ann = ParecerAnnotation(
        request_id=id,
        author_id=author_id,
        trecho_texto=trecho,
        questionamento=questionamento,
    )
    db.add(ann)
    await db.commit()
    await db.refresh(ann)

    author = (await db.execute(select(User).where(User.id == author_id))).scalar_one_or_none()
    return AnnotationOut(
        id=ann.id,
        request_id=ann.request_id,
        author_id=ann.author_id,
        author_name=author.name if author else None,
        author_color=color_for(author.email if author else None, author_id),
        trecho_texto=ann.trecho_texto,
        questionamento=ann.questionamento,
        created_at=ann.created_at,
    )


@router.delete("/annotations/{annotation_id}", status_code=204)
async def delete_annotation(
    annotation_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> None:
    payload = _auth(credentials)
    ann = (
        await db.execute(select(ParecerAnnotation).where(ParecerAnnotation.id == annotation_id))
    ).scalar_one_or_none()
    if ann is None:
        raise HTTPException(status_code=404, detail="Anotacao nao encontrada")

    is_admin = payload.get("role") == "admin"
    is_author = str(ann.author_id) == payload.get("sub")
    if not (is_admin or is_author):
        raise HTTPException(status_code=403, detail="Apenas o autor ou um admin pode apagar")

    await db.delete(ann)
    await db.commit()
