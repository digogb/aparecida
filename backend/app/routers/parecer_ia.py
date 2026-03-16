import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parecer import ParecerRequest, ParecerVersion
from app.schemas.parecer_version import (
    ClassifyOut,
    ParecerVersionDetail,
    ParecerVersionListItem,
    ReprocessIn,
)
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
        subtema=data.get("subtema"),
        modelo_parecer=pr.modelo,
        municipio_detectado=data.get("municipio_detectado"),
        confianca=data.get("confianca", 0.0),
        request_id=pr.id,
        status=pr.status.value,
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
    "/parecer-requests/{id}/reprocess",
    response_model=ParecerVersionDetail,
)
async def reprocess_parecer(
    id: uuid.UUID,
    body: ReprocessIn,
    db: AsyncSession = Depends(get_db),
) -> ParecerVersionDetail:
    try:
        version = await parecer_engine.reprocess(str(id), body.observacoes, db)
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
