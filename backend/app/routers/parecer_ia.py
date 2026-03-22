import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.services import classifier, parecer_engine

PREFIX = "/api"
TAGS = ["parecer-ia"]

router = APIRouter()


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

    return ClassifyOut(
        tema=pr.tema,
        subtema=data.get("areas_conexas", [None])[0] if data.get("areas_conexas") else None,
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

    result = await db.execute(
        select(ParecerVersion)
        .where(ParecerVersion.request_id == id)
        .order_by(ParecerVersion.version_number)
    )
    versions = result.scalars().all()

    return [ParecerVersionListItem.model_validate(v) for v in versions]


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
    if pr and pr.status not in (ParecerStatus.aprovado, ParecerStatus.enviado, ParecerStatus.em_correcao):
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
