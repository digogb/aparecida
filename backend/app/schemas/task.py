from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.task import TaskCategory, TaskPriority


class TaskCreate(BaseModel):
    column_id: uuid.UUID
    title: str
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    priority: TaskPriority = TaskPriority.medium
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None
    source_ref: Optional[dict] = None


class TaskMoveRequest(BaseModel):
    column_id: uuid.UUID
    position: int = 0


class TaskOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    column_id: uuid.UUID
    title: str
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    priority: TaskPriority
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None
    position: int
    source_ref: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class TaskHistoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    task_id: uuid.UUID
    from_column_id: Optional[uuid.UUID] = None
    to_column_id: Optional[uuid.UUID] = None
    changed_by: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    created_at: datetime


class ColumnOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    board_id: uuid.UUID
    name: str
    position: int
    wip_limit: Optional[int] = None
    tasks: list[TaskOut] = []


class BoardOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    columns: list[ColumnOut] = []
