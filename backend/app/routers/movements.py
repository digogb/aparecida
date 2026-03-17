import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.movement import Movement, MovementType, Process
from app.schemas.movement import DJEWebhookPayload, MovementOut, MovementStats
from app.services.dje_sync import ingest_movement
from app.services.notification import ws_manager

PREFIX = "/api"
TAGS = ["movements"]

router = APIRouter()
ws_router = APIRouter()

bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"


def _require_user(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")


# ---------------------------------------------------------------------------
# DJE search (manual trigger)
# ---------------------------------------------------------------------------

class DJESearchRequest(BaseModel):
    nome_advogado: str | None = None
    numero_oab: str | None = None
    numero_processo: str | None = None
    sigla_tribunal: str | None = None
    data_inicio: str | None = None  # ISO date YYYY-MM-DD
    data_fim: str | None = None


async def _run_dje_search(body: DJESearchRequest) -> None:
    """Background worker: search DJE and ingest results."""
    import asyncio
    from datetime import date

    from app.database import async_session as AsyncSessionLocal
    from app.services.dje_sync import ingest_movement as _ingest

    try:
        from dje_search import DJESearchClient, DJESearchParams

        data_inicio = date.fromisoformat(body.data_inicio) if body.data_inicio else None
        data_fim = date.fromisoformat(body.data_fim) if body.data_fim else None

        params = DJESearchParams(
            nome_advogado=body.nome_advogado,
            numero_oab=body.numero_oab,
            numero_processo=body.numero_processo,
            sigla_tribunal=body.sigla_tribunal,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

        loop = asyncio.get_event_loop()
        client = DJESearchClient()
        comunicacoes = await loop.run_in_executor(None, client.buscar, params)

        count = 0
        async with AsyncSessionLocal() as db:
            for com in comunicacoes:
                movement = await _ingest(
                    db=db,
                    dje_id=com.id,
                    process_number=com.numero_processo,
                    raw_type=com.tipo_comunicacao or "publicacao",
                    content=com.texto,
                    published_at=None,
                    court=com.tribunal or com.orgao or None,
                    metadata={
                        "link": com.link,
                        "tribunal": com.tribunal,
                        "orgao": com.orgao,
                        "polos": com.polos.to_dict(),
                        "destinatarios": com.destinatarios,
                        "data_disponibilizacao": com.data_disponibilizacao,
                        "termo_buscado": com.termo_buscado,
                    },
                )
                if movement is not None:
                    count += 1

        logger.info("DJE background search finished: found=%d ingested=%d", len(comunicacoes), count)

    except Exception as e:
        logger.error("DJE background search failed: %s", e)


@router.post("/dje/search", status_code=202, tags=["dje"])
async def dje_search(
    body: DJESearchRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> dict:
    """
    Enqueue a DJE search in the background and return immediately.
    Results arrive via WebSocket as movements are ingested.
    """
    _require_user(credentials)

    try:
        from dje_search import DJESearchParams
        # Validate params before queuing
        data_inicio = None
        data_fim = None
        if body.data_inicio:
            from datetime import date
            data_inicio = date.fromisoformat(body.data_inicio)
        if body.data_fim:
            from datetime import date
            data_fim = date.fromisoformat(body.data_fim)
        DJESearchParams(
            nome_advogado=body.nome_advogado,
            numero_oab=body.numero_oab,
            numero_processo=body.numero_processo,
            sigla_tribunal=body.sigla_tribunal,
            data_inicio=data_inicio,
            data_fim=data_fim,
        ).validar()
    except ImportError:
        raise HTTPException(status_code=503, detail="dje-search-client not installed")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    background_tasks.add_task(_run_dje_search, body)
    return {"status": "started"}


# ---------------------------------------------------------------------------
# DJE webhook (no auth — called by external DJE system)
# ---------------------------------------------------------------------------

@router.post("/dje/webhook", status_code=201, tags=["dje"])
async def dje_webhook(
    payload: DJEWebhookPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Receive a DJE push event and ingest the movement."""
    movement = await ingest_movement(
        db=db,
        dje_id=payload.dje_id,
        process_number=payload.process_number,
        raw_type=payload.type,
        content=payload.content,
        published_at=payload.published_at,
        court=payload.court,
        metadata=payload.metadata,
    )
    if movement is None:
        return {"status": "duplicate"}
    return {"status": "created", "id": str(movement.id)}


# ---------------------------------------------------------------------------
# Stats (before /{id} to avoid route shadowing)
# ---------------------------------------------------------------------------

@router.get("/movements/stats", response_model=MovementStats)
async def movement_stats(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> MovementStats:
    _require_user(credentials)

    total = (await db.execute(select(func.count(Movement.id)))).scalar_one() or 0
    unread = (
        await db.execute(select(func.count(Movement.id)).where(Movement.is_read == False))
    ).scalar_one() or 0

    by_type_rows = (
        await db.execute(select(Movement.type, func.count(Movement.id)).group_by(Movement.type))
    ).all()
    by_type = {row[0].value: row[1] for row in by_type_rows}

    last_sync = (await db.execute(select(func.max(Movement.created_at)))).scalar_one()

    return MovementStats(total=total, unread=unread, by_type=by_type, last_sync=last_sync)


# ---------------------------------------------------------------------------
# Batch read (before /{id})
# ---------------------------------------------------------------------------

@router.patch("/movements/batch-read")
async def batch_mark_read(
    ids: list[uuid.UUID],
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_user(credentials)
    await db.execute(update(Movement).where(Movement.id.in_(ids)).values(is_read=True))
    await db.commit()
    return {"status": "ok", "updated": len(ids)}


# ---------------------------------------------------------------------------
# List movements
# ---------------------------------------------------------------------------

@router.get("/movements", response_model=list[MovementOut])
async def list_movements(
    process_id: Optional[uuid.UUID] = Query(None),
    type: Optional[MovementType] = Query(None),
    is_read: Optional[bool] = Query(None),
    q: Optional[str] = Query(None, description="Full-text search in content"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[MovementOut]:
    _require_user(credentials)

    stmt = select(Movement).options(selectinload(Movement.process))

    filters = []
    if process_id:
        filters.append(Movement.process_id == process_id)
    if type:
        filters.append(Movement.type == type)
    if is_read is not None:
        filters.append(Movement.is_read == is_read)
    if q:
        filters.append(Movement.content.ilike(f"%{q}%"))
    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = (
        stmt.order_by(Movement.published_at.desc().nullslast(), Movement.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Single movement
# ---------------------------------------------------------------------------

@router.get("/movements/{movement_id}", response_model=MovementOut)
async def get_movement(
    movement_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> MovementOut:
    _require_user(credentials)
    result = await db.execute(
        select(Movement)
        .options(selectinload(Movement.process))
        .where(Movement.id == movement_id)
    )
    movement = result.scalar_one_or_none()
    if movement is None:
        raise HTTPException(status_code=404, detail="Movement not found")
    return movement


@router.patch("/movements/{movement_id}/read")
async def mark_movement_read(
    movement_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_user(credentials)
    result = await db.execute(select(Movement).where(Movement.id == movement_id))
    movement = result.scalar_one_or_none()
    if movement is None:
        raise HTTPException(status_code=404, detail="Movement not found")
    movement.is_read = True
    await db.commit()
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Process timeline
# ---------------------------------------------------------------------------

@router.get("/processes/{process_id}/timeline", response_model=list[MovementOut])
async def process_timeline(
    process_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[MovementOut]:
    _require_user(credentials)
    result = await db.execute(
        select(Movement)
        .options(selectinload(Movement.process))
        .where(Movement.process_id == process_id)
        .order_by(Movement.published_at.asc().nullslast(), Movement.created_at.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@ws_router.websocket("/ws/movements")
async def ws_movements(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive: accept ping frames from clients
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
