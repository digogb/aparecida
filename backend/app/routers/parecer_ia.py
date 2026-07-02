import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.parecer import ParecerRequest, ParecerVersion
from app.schemas.parecer_version import (
    ApplyCorrectionIn,
    ClassifyOut,
    ParecerVersionDetail,
    ParecerVersionListItem,
    PreviewCorrectionOut,
    ReprocessIn,
)


class VersionUpdateIn(BaseModel):
    content_html: str
    content_tiptap: Optional[dict] = None


class CorrectSelectionIn(BaseModel):
    trecho: str
    instrucao: str


class CorrectSelectionOut(BaseModel):
    corrigido: str
from app.services import classifier, parecer_engine

PREFIX = "/api"
TAGS = ["parecer-ia"]

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"


def _get_user_id(credentials: HTTPAuthorizationCredentials | None) -> uuid.UUID | None:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG])
        raw = payload.get("sub")
        return uuid.UUID(raw) if raw else None
    except Exception:
        return None


@router.post(
    "/parecer-requests/{id}/classify",
    response_model=ClassifyOut,
)
async def classify_request(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ClassifyOut:
    try:
        pr, data = await classifier.classify(str(id), db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # subtipo (v5.0) substitui o antigo areas_conexas[0]; fallback para schema legacy
    subtema = data.get("subtipo") or (
        data.get("areas_conexas", [None])[0] if data.get("areas_conexas") else None
    )
    return ClassifyOut(
        tema=pr.tema,
        subtema=subtema,
        modelo_parecer=pr.modelo,
        municipio_detectado=data.get("municipio"),
        confianca=1.0 if data.get("confianca_classificacao") == "alta" else 0.5,
        request_id=pr.id,
        status=pr.status.value,
        classificacao=data,
    )


@router.post(
    "/parecer-requests/{id}/generate",
    response_model=ParecerVersionDetail,
)
async def generate_parecer(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ParecerVersionDetail:
    try:
        version = await parecer_engine.generate(str(id), db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ParecerVersionDetail.model_validate(version)


@router.post(
    "/parecer-requests/{id}/preview-correction",
    response_model=PreviewCorrectionOut,
)
async def preview_correction(
    id: uuid.UUID,
    body: ReprocessIn,
    db: AsyncSession = Depends(get_db),
) -> PreviewCorrectionOut:
    """Chama P3 e retorna preview das correções sem salvar."""
    try:
        preview = await parecer_engine.preview_correction(str(id), body.observacoes, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return PreviewCorrectionOut(**preview)


@router.post(
    "/parecer-requests/{id}/apply-correction",
    response_model=ParecerVersionDetail,
)
async def apply_correction(
    id: uuid.UUID,
    body: ApplyCorrectionIn,
    db: AsyncSession = Depends(get_db),
) -> ParecerVersionDetail:
    """Aplica as seções aprovadas pelo advogado e cria nova versão."""
    try:
        version = await parecer_engine.apply_correction(
            str(id),
            body.secoes_aprovadas,
            body.observacoes,
            body.notas_revisor,
            body.citacoes_verificar,
            db,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ParecerVersionDetail.model_validate(version)


@router.post(
    "/parecer-requests/{id}/correct-selection",
    response_model=CorrectSelectionOut,
)
async def correct_selection(
    id: uuid.UUID,
    body: CorrectSelectionIn,
    db: AsyncSession = Depends(get_db),
) -> CorrectSelectionOut:
    """Correção por trecho selecionado (auditoria — Erro 3): reescreve só o trecho,
    sem tocar no resto do documento. O editor substitui apenas a seleção."""
    try:
        corrigido = await parecer_engine.correct_selection(
            str(id), body.trecho, body.instrucao, db
        )
    except ValueError as e:
        msg = str(e)
        status = 404 if "nao encontrado" in msg else 400
        raise HTTPException(status_code=status, detail=msg)
    return CorrectSelectionOut(corrigido=corrigido)


@router.get(
    "/parecer-requests/{id}/versions",
    response_model=list[ParecerVersionListItem],
)
async def list_versions(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ParecerVersionListItem]:
    pr_result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == id)
    )
    if pr_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Parecer request nao encontrado")

    from app.models.user import User

    result = await db.execute(
        select(ParecerVersion, User.name)
        .outerjoin(User, User.id == ParecerVersion.created_by)
        .where(ParecerVersion.request_id == id)
        .order_by(ParecerVersion.version_number)
    )
    rows = result.all()

    return [
        ParecerVersionListItem.model_validate(version).model_copy(update={"created_by_name": name})
        for version, name in rows
    ]


@router.get(
    "/parecer-requests/{id}/versions/{version_number}",
    response_model=ParecerVersionDetail,
)
async def get_version(
    id: uuid.UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db),
) -> ParecerVersionDetail:
    result = await db.execute(
        select(ParecerVersion).where(
            ParecerVersion.request_id == id,
            ParecerVersion.version_number == version_number,
        )
    )
    version = result.scalar_one_or_none()
    if version is None:
        raise HTTPException(status_code=404, detail="Versao nao encontrada")

    return ParecerVersionDetail.model_validate(version)


@router.post(
    "/parecer-requests/{id}/versions/{version_id}/restore",
    response_model=ParecerVersionDetail,
)
async def restore_version(
    id: uuid.UUID,
    version_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ParecerVersionDetail:
    """Cria uma nova versão copiando o conteúdo de uma versão anterior."""
    from sqlalchemy import func, select
    from app.models.parecer import ParecerStatus, ParecerStatusHistory, VersionSource

    pr_result = await db.execute(select(ParecerRequest).where(ParecerRequest.id == id))
    pr = pr_result.scalar_one_or_none()
    if pr is None:
        raise HTTPException(status_code=404, detail="Parecer request nao encontrado")

    src_result = await db.execute(
        select(ParecerVersion).where(
            ParecerVersion.id == version_id,
            ParecerVersion.request_id == id,
        )
    )
    src = src_result.scalar_one_or_none()
    if src is None:
        raise HTTPException(status_code=404, detail="Versao nao encontrada")

    next_num_result = await db.execute(
        select(func.coalesce(func.max(ParecerVersion.version_number), 0))
        .where(ParecerVersion.request_id == id)
    )
    next_num = next_num_result.scalar_one() + 1

    new_version = ParecerVersion(
        request_id=pr.id,
        version_number=next_num,
        source=VersionSource.restaurado,
        content_tiptap=src.content_tiptap,
        content_html=src.content_html,
        prompt_version=src.prompt_version,
        citacoes_verificar=src.citacoes_verificar or [],
        ressalvas=src.ressalvas or [],
        notas_revisor=[],
        reprocess_instructions=f"Restaurado da v{src.version_number}",
    )
    db.add(new_version)

    old_status = pr.status
    pr.status = ParecerStatus.em_correcao
    db.add(ParecerStatusHistory(
        request_id=pr.id,
        from_status=old_status,
        to_status=ParecerStatus.em_correcao,
        notes=f"Versão restaurada da v{src.version_number}",
    ))

    await db.commit()
    await db.refresh(new_version)
    return ParecerVersionDetail.model_validate(new_version)


@router.put(
    "/parecer-requests/{id}/versions/{version_id}",
    response_model=ParecerVersionDetail,
)
async def update_version(
    id: uuid.UUID,
    version_id: uuid.UUID,
    body: VersionUpdateIn,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> ParecerVersionDetail:
    result = await db.execute(
        select(ParecerVersion).where(
            ParecerVersion.id == version_id,
            ParecerVersion.request_id == id,
        )
    )
    version = result.scalar_one_or_none()
    if version is None:
        raise HTTPException(status_code=404, detail="Versao nao encontrada")

    version.content_html = body.content_html
    if body.content_tiptap is not None:
        version.content_tiptap = body.content_tiptap

    # Atualizar status para em_correcao ao editar manualmente
    from app.models.parecer import ParecerStatus, ParecerStatusHistory
    pr_result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == id)
    )
    pr = pr_result.scalar_one_or_none()
    if pr:
        # Atribuir advogado automaticamente na primeira edição manual
        user_id = _get_user_id(credentials)
        if user_id and not pr.assigned_to:
            pr.assigned_to = user_id

        if pr.status not in (ParecerStatus.aprovado, ParecerStatus.enviado, ParecerStatus.em_correcao):
            old_status = pr.status
            pr.status = ParecerStatus.em_correcao
            db.add(ParecerStatusHistory(
                request_id=pr.id,
                from_status=old_status,
                to_status=ParecerStatus.em_correcao,
                notes="Edição manual pelo advogado",
            ))

    await db.commit()
    await db.refresh(version)
    return ParecerVersionDetail.model_validate(version)


@router.post(
    "/parecer-requests/{id}/snapshot",
    response_model=ParecerVersionDetail,
)
async def snapshot_version(
    id: uuid.UUID,
    body: VersionUpdateIn,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> ParecerVersionDetail:
    """Cria nova versão manual_edit a partir de um salvamento explícito do editor."""
    from sqlalchemy import func
    from app.models.parecer import ParecerStatus, ParecerStatusHistory, VersionSource

    pr_result = await db.execute(select(ParecerRequest).where(ParecerRequest.id == id))
    pr = pr_result.scalar_one_or_none()
    if pr is None:
        raise HTTPException(status_code=404, detail="Parecer request nao encontrado")

    last_result = await db.execute(
        select(ParecerVersion)
        .where(ParecerVersion.request_id == id)
        .order_by(ParecerVersion.version_number.desc())
        .limit(1)
    )
    last = last_result.scalar_one_or_none()

    next_num_result = await db.execute(
        select(func.coalesce(func.max(ParecerVersion.version_number), 0))
        .where(ParecerVersion.request_id == id)
    )
    next_num = next_num_result.scalar_one() + 1

    user_id = _get_user_id(credentials)

    new_version = ParecerVersion(
        request_id=pr.id,
        version_number=next_num,
        source=VersionSource.manual_edit,
        content_tiptap=body.content_tiptap,
        content_html=body.content_html,
        prompt_version=last.prompt_version if last else None,
        citacoes_verificar=last.citacoes_verificar or [] if last else [],
        ressalvas=last.ressalvas or [] if last else [],
        notas_revisor=[],
        created_by=user_id,
    )
    db.add(new_version)

    if user_id and not pr.assigned_to:
        pr.assigned_to = user_id

    if pr.status not in (ParecerStatus.aprovado, ParecerStatus.enviado, ParecerStatus.em_correcao):
        old_status = pr.status
        pr.status = ParecerStatus.em_correcao
        db.add(ParecerStatusHistory(
            request_id=pr.id,
            from_status=old_status,
            to_status=ParecerStatus.em_correcao,
            notes="Edição manual pelo advogado",
        ))

    await db.commit()
    await db.refresh(new_version)
    return ParecerVersionDetail.model_validate(new_version)
