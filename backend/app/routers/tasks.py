"""
Tasks router — Kanban CRUD endpoints + WebSocket for real-time sync.

Auto-discovered by main.py. Exports `router` and `ws_router`.
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas.task import BoardOut, TaskCreate, TaskHistoryOut, TaskMoveRequest, TaskOut
from app.services.task_service import (
    create_task,
    get_board,
    get_first_board,
    get_task_history,
    move_task,
)

logger = logging.getLogger(__name__)

PREFIX = "/api"
TAGS = ["tasks"]

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
# WebSocket connection manager (task-specific)
# ---------------------------------------------------------------------------

class _TaskConnectionManager:
    def __init__(self) -> None:
        self._connections: list[Any] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, data: dict) -> None:
        dead = []
        for ws in list(self._connections):
            try:
                await ws.send_text(json.dumps(data, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


task_ws_manager = _TaskConnectionManager()


# ---------------------------------------------------------------------------
# Board endpoints
# ---------------------------------------------------------------------------

@router.get("/boards/default/tasks", response_model=BoardOut)
async def get_default_board_tasks(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> BoardOut:
    """Return the first (default) board with all tasks."""
    _require_user(credentials)
    board = await get_first_board(db)
    return board


@router.get("/boards/{board_id}/tasks", response_model=BoardOut)
async def get_board_tasks(
    board_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> BoardOut:
    _require_user(credentials)
    board = await get_board(board_id, db)
    return board


# ---------------------------------------------------------------------------
# Task endpoints
# ---------------------------------------------------------------------------

@router.post("/tasks", response_model=TaskOut, status_code=201)
async def post_task(
    data: TaskCreate,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> TaskOut:
    payload = _require_user(credentials)
    user_id = uuid.UUID(payload["sub"]) if "sub" in payload else None
    task = await create_task(data, db, changed_by=user_id)

    # Broadcast via WebSocket
    asyncio.create_task(task_ws_manager.broadcast({
        "event": "task.created",
        "data": {
            "id": str(task.id),
            "column_id": str(task.column_id),
            "title": task.title,
            "priority": task.priority.value,
        },
    }))

    return task


@router.patch("/tasks/{task_id}/move", response_model=TaskOut)
async def patch_task_move(
    task_id: uuid.UUID,
    body: TaskMoveRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> TaskOut:
    payload = _require_user(credentials)
    user_id = uuid.UUID(payload["sub"]) if "sub" in payload else None
    task = await move_task(task_id, body.column_id, body.position, db, changed_by=user_id)

    # Broadcast move event
    asyncio.create_task(task_ws_manager.broadcast({
        "event": "task.moved",
        "data": {
            "id": str(task.id),
            "column_id": str(task.column_id),
            "position": task.position,
        },
    }))

    return task


@router.get("/tasks/{task_id}/history", response_model=list[TaskHistoryOut])
async def get_history(
    task_id: uuid.UUID,
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> list[TaskHistoryOut]:
    _require_user(credentials)
    return await get_task_history(task_id, db)


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@ws_router.websocket("/ws/tasks")
async def ws_tasks(websocket: WebSocket) -> None:
    await task_ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        task_ws_manager.disconnect(websocket)
