"""
Task service — CRUD operations, atomic column move with WIP limit enforcement.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Board, Column, Task, TaskComment, TaskHistory
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


async def get_board(board_id: uuid.UUID, db: AsyncSession) -> Board:
    """Fetch board with all columns and tasks."""
    result = await db.execute(
        select(Board)
        .options(
            selectinload(Board.columns).selectinload(Column.tasks)
        )
        .where(Board.id == board_id)
    )
    board = result.scalar_one_or_none()
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


async def get_first_board(db: AsyncSession) -> Board:
    """Return the first (and usually only) board in the system."""
    result = await db.execute(
        select(Board)
        .options(selectinload(Board.columns).selectinload(Column.tasks))
        .order_by(Board.created_at)
        .limit(1)
    )
    board = result.scalar_one_or_none()
    if board is None:
        raise HTTPException(status_code=404, detail="No board found")
    return board


async def create_task(
    data: TaskCreate,
    db: AsyncSession,
    changed_by: Optional[uuid.UUID] = None,
    skip_wip_limit: bool = False,
) -> Task:
    """Create a new task in the given column."""
    # Verify column exists
    col_result = await db.execute(select(Column).where(Column.id == data.column_id))
    column = col_result.scalar_one_or_none()
    if column is None:
        raise HTTPException(status_code=404, detail="Column not found")

    # Check WIP limit (skipped for system-generated tasks)
    if not skip_wip_limit and column.wip_limit is not None:
        count_result = await db.execute(
            select(func.count(Task.id)).where(Task.column_id == column.id)
        )
        current_count = count_result.scalar_one() or 0
        if current_count >= column.wip_limit:
            raise HTTPException(
                status_code=409,
                detail=f"WIP limit reached for column '{column.name}' ({column.wip_limit} tasks)",
            )

    # Determine position (append to end)
    pos_result = await db.execute(
        select(func.coalesce(func.max(Task.position), -1)).where(Task.column_id == column.id)
    )
    next_position = (pos_result.scalar_one() or 0) + 1

    task = Task(
        column_id=data.column_id,
        title=data.title,
        description=data.description,
        category=data.category,
        priority=data.priority,
        assigned_to=data.assigned_to,
        due_date=data.due_date,
        start_date=data.start_date,
        estimated_hours=data.estimated_hours,
        tags=data.tags or [],
        checklist=[item.model_dump() for item in data.checklist] if data.checklist else [],
        position=next_position,
        source_ref=data.source_ref,
    )
    db.add(task)
    await db.flush()

    history = TaskHistory(
        task_id=task.id,
        from_column_id=None,
        to_column_id=column.id,
        changed_by=changed_by,
        notes="Tarefa criada",
    )
    db.add(history)

    await db.commit()
    await db.refresh(task)
    return task


async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: AsyncSession,
    changed_by: Optional[uuid.UUID] = None,
) -> Task:
    """Update task fields (not column/position — use move_task for that)."""
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    changes: list[str] = []
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        old_value = getattr(task, field)
        if field == "checklist" and value is not None:
            value = [item.model_dump() if hasattr(item, "model_dump") else item for item in value]
        if old_value != value:
            changes.append(field)
            setattr(task, field, value)

    if changes:
        history = TaskHistory(
            task_id=task.id,
            from_column_id=task.column_id,
            to_column_id=task.column_id,
            changed_by=changed_by,
            notes=f"Campos atualizados: {', '.join(changes)}",
        )
        db.add(history)

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(
    task_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    """Delete a task and its history."""
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Delete history entries
    history_result = await db.execute(
        select(TaskHistory).where(TaskHistory.task_id == task_id)
    )
    for h in history_result.scalars().all():
        await db.delete(h)

    # Delete comments
    comment_result = await db.execute(
        select(TaskComment).where(TaskComment.task_id == task_id)
    )
    for c in comment_result.scalars().all():
        await db.delete(c)

    await db.delete(task)
    await db.commit()


async def move_task(
    task_id: uuid.UUID,
    to_column_id: uuid.UUID,
    position: int,
    db: AsyncSession,
    changed_by: Optional[uuid.UUID] = None,
) -> Task:
    """
    Atomically move a task to a different column at a given position.
    Raises 409 if the target column's WIP limit would be exceeded.
    """
    # Fetch task
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    task = task_result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    from_column_id = task.column_id

    # Fetch target column
    col_result = await db.execute(select(Column).where(Column.id == to_column_id))
    column = col_result.scalar_one_or_none()
    if column is None:
        raise HTTPException(status_code=404, detail="Target column not found")

    # WIP limit check (only if moving to a different column)
    if from_column_id != to_column_id and column.wip_limit is not None:
        count_result = await db.execute(
            select(func.count(Task.id)).where(Task.column_id == to_column_id)
        )
        current_count = count_result.scalar_one() or 0
        if current_count >= column.wip_limit:
            raise HTTPException(
                status_code=409,
                detail=f"WIP limit reached for column '{column.name}' ({column.wip_limit} tasks)",
            )

    # --- reorder positions atomically ---
    old_col_id = from_column_id
    moving_across = from_column_id != to_column_id

    if moving_across:
        # Close gap in source column
        await db.execute(
            sa_update(Task)
            .where(Task.column_id == old_col_id, Task.position > task.position)
            .values(position=Task.position - 1)
        )
        # Open gap in target column
        await db.execute(
            sa_update(Task)
            .where(Task.column_id == to_column_id, Task.position >= position)
            .values(position=Task.position + 1)
        )
    else:
        # Reorder within the same column
        old_pos = task.position
        if old_pos < position:
            await db.execute(
                sa_update(Task)
                .where(
                    Task.column_id == to_column_id,
                    Task.id != task_id,
                    Task.position > old_pos,
                    Task.position <= position,
                )
                .values(position=Task.position - 1)
            )
        elif old_pos > position:
            await db.execute(
                sa_update(Task)
                .where(
                    Task.column_id == to_column_id,
                    Task.id != task_id,
                    Task.position >= position,
                    Task.position < old_pos,
                )
                .values(position=Task.position + 1)
            )

    # Update task
    task.column_id = to_column_id
    task.position = position

    # Record history
    if from_column_id != to_column_id:
        history = TaskHistory(
            task_id=task.id,
            from_column_id=from_column_id,
            to_column_id=to_column_id,
            changed_by=changed_by,
            notes=f"Movida para coluna {column.name}",
        )
        db.add(history)

    await db.commit()
    await db.refresh(task)
    return task


async def get_task_history(task_id: uuid.UUID, db: AsyncSession) -> list[TaskHistory]:
    """Return history entries for a task, oldest first."""
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    if task_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Task not found")

    result = await db.execute(
        select(TaskHistory)
        .where(TaskHistory.task_id == task_id)
        .order_by(TaskHistory.created_at.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

async def create_comment(
    task_id: uuid.UUID,
    content: str,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> TaskComment:
    """Add a comment to a task."""
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    if task_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Task not found")

    comment = TaskComment(task_id=task_id, user_id=user_id, content=content)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments(task_id: uuid.UUID, db: AsyncSession) -> list[TaskComment]:
    """Return comments for a task, oldest first."""
    task_result = await db.execute(select(Task).where(Task.id == task_id))
    if task_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Task not found")

    result = await db.execute(
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Users (for assignee listing)
# ---------------------------------------------------------------------------

async def list_active_users(db: AsyncSession) -> list[User]:
    """Return all active users (for assignee dropdown)."""
    result = await db.execute(
        select(User).where(User.is_active.is_(True)).order_by(User.name)
    )
    return list(result.scalars().all())
