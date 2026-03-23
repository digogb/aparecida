"""
Event dispatcher — observer pattern.

dispatch_movement_event: called when a DJE movement is ingested →
  creates an automatic task in the "Entrada" column.

dispatch_parecer_event: called after a parecer is generated →
  creates a revision task in the "Entrada" column.
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movement import Movement, MovementType, Process
from app.models.parecer import ParecerRequest
from app.models.task import Board, Column, TaskCategory, TaskPriority
from app.schemas.task import TaskCreate
from app.services.task_service import create_task

logger = logging.getLogger(__name__)

_MOVEMENT_PRIORITY: dict[MovementType, TaskPriority] = {
    MovementType.intimacao:    TaskPriority.high,
    MovementType.sentenca:     TaskPriority.medium,
    MovementType.despacho:     TaskPriority.low,
    MovementType.acordao:      TaskPriority.medium,
    MovementType.publicacao:   TaskPriority.medium,
    MovementType.distribuicao: TaskPriority.low,
    MovementType.outros:       TaskPriority.low,
}

_MOVEMENT_BUSINESS_DAYS: dict[MovementType, int | None] = {
    MovementType.intimacao:    15,   # prazo de resposta padrão
    MovementType.sentenca:     30,
    MovementType.despacho:     None,
    MovementType.acordao:      30,
    MovementType.publicacao:   None,
    MovementType.distribuicao: None,
    MovementType.outros:       None,
}


async def _get_entrada_column(db: AsyncSession) -> Column | None:
    """Find the first column of the first board (Entrada)."""
    result = await db.execute(
        select(Board).order_by(Board.created_at).limit(1)
    )
    board = result.scalar_one_or_none()
    if board is None:
        return None

    col_result = await db.execute(
        select(Column)
        .where(Column.board_id == board.id)
        .order_by(Column.position)
        .limit(1)
    )
    return col_result.scalar_one_or_none()


async def dispatch_movement_event(movement: Movement, db: AsyncSession) -> None:
    """
    Called after a DJE movement is persisted.
    Creates an automatic task in the Entrada column.
    Silently skips if board/column not found or WIP exceeded.
    """
    column = await _get_entrada_column(db)
    if column is None:
        logger.warning("dispatch_movement_event: no Entrada column found, skipping")
        return

    priority = _MOVEMENT_PRIORITY.get(movement.type, TaskPriority.medium)
    business_days = _MOVEMENT_BUSINESS_DAYS.get(movement.type)

    title_prefix: dict[MovementType, str] = {
        MovementType.intimacao:    "Intimação",
        MovementType.sentenca:     "Sentença",
        MovementType.despacho:     "Despacho",
        MovementType.acordao:      "Acórdão",
        MovementType.publicacao:   "Publicação",
        MovementType.distribuicao: "Distribuição",
        MovementType.outros:       "Movimentação",
    }
    prefix = title_prefix.get(movement.type, "Movimentação")

    # Buscar número do processo legível
    process_result = await db.execute(
        select(Process.number).where(Process.id == movement.process_id)
    )
    process_number = process_result.scalar_one_or_none() or str(movement.process_id)
    title = f"{prefix} — {process_number}"

    source_ref: dict = {
        "type": "movement",
        "movement_id": str(movement.id),
        "movement_type": movement.type.value,
        "process_id": str(movement.process_id),
    }
    if business_days is not None:
        source_ref["business_days"] = business_days

    data = TaskCreate(
        column_id=column.id,
        title=title,
        category=TaskCategory.publicacao_dje,
        priority=priority,
        source_ref=source_ref,
    )

    try:
        task = await create_task(data, db, skip_wip_limit=True)
        logger.info(
            "dispatch_movement_event: created task %s for movement %s",
            task.id,
            movement.id,
        )
    except Exception as e:
        logger.warning("dispatch_movement_event: could not create task: %s", e)


async def dispatch_parecer_event(parecer_request_id: str, db: AsyncSession) -> None:
    """
    Called after a parecer version is generated.
    Creates a revision task in the Entrada column for lawyers to review.
    Silently skips if board/column not found or WIP exceeded.
    """
    column = await _get_entrada_column(db)
    if column is None:
        logger.warning("dispatch_parecer_event: no Entrada column found, skipping")
        return

    # Buscar numero_parecer legível
    pr_result = await db.execute(
        select(ParecerRequest.numero_parecer).where(ParecerRequest.id == parecer_request_id)
    )
    numero = pr_result.scalar_one_or_none() or parecer_request_id[:8]
    title = f"Revisar Parecer — {numero}"

    source_ref: dict = {
        "type": "parecer",
        "parecer_request_id": parecer_request_id,
    }

    data = TaskCreate(
        column_id=column.id,
        title=title,
        category=TaskCategory.parecer,
        priority=TaskPriority.medium,
        source_ref=source_ref,
    )

    try:
        task = await create_task(data, db)
        logger.info(
            "dispatch_parecer_event: created review task %s for parecer %s",
            task.id,
            parecer_request_id,
        )
    except Exception as e:
        logger.warning("dispatch_parecer_event: could not create task: %s", e)
