from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from app.models.task import TaskCategory, TaskPriority


# ---------------------------------------------------------------------------
# Checklist item schema
# ---------------------------------------------------------------------------

class ChecklistItem(BaseModel):
    text: str
    done: bool = False


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    column_id: uuid.UUID
    title: str
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    priority: TaskPriority = TaskPriority.medium
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[list[str]] = None
    checklist: Optional[list[ChecklistItem]] = None
    source_ref: Optional[dict] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[list[str]] = None
    checklist: Optional[list[ChecklistItem]] = None


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
    start_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[list[str]] = None
    checklist: Optional[list[ChecklistItem]] = None
    position: int
    source_ref: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Task history
# ---------------------------------------------------------------------------

class TaskHistoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    task_id: uuid.UUID
    from_column_id: Optional[uuid.UUID] = None
    to_column_id: Optional[uuid.UUID] = None
    changed_by: Optional[uuid.UUID] = None
    notes: Optional[str] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Task comments
# ---------------------------------------------------------------------------

class TaskCommentCreate(BaseModel):
    content: str


class TaskCommentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    task_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Board / Column
# ---------------------------------------------------------------------------

class ColumnOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    board_id: uuid.UUID
    name: str
    position: int
    wip_limit: Optional[int] = None
    tasks: list[TaskOut] = []

    @model_validator(mode="after")
    def _sort_tasks(self) -> "ColumnOut":
        self.tasks.sort(key=lambda t: t.position)
        return self


class BoardOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    columns: list[ColumnOut] = []

    @model_validator(mode="after")
    def _sort_columns(self) -> "BoardOut":
        self.columns.sort(key=lambda c: c.position)
        return self


# ---------------------------------------------------------------------------
# User (lightweight, for listing assignees)
# ---------------------------------------------------------------------------

class UserMinimal(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    email: str
