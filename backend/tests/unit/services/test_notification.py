"""
Testes unitários do notification service (peer review + contagem + broadcast).
Sem rede e sem DB real — usa mocks.
"""
from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import notification as notif


def _mock_db() -> AsyncMock:
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


def _peer_review(**overrides):
    base = dict(id=uuid.uuid4(), reviewer_id=uuid.uuid4(), requested_by=uuid.uuid4())
    base.update(overrides)
    return SimpleNamespace(**base)


def _parecer(**overrides):
    base = dict(id=uuid.uuid4(), numero_parecer="PAR-2026-0009")
    base.update(overrides)
    return SimpleNamespace(**base)


class TestGetUnreadCount:
    @pytest.mark.asyncio
    async def test_retorna_contagem(self):
        db = _mock_db()
        result = MagicMock()
        result.scalar_one.return_value = 7
        db.execute = AsyncMock(return_value=result)
        assert await notif.get_unread_count(db, str(uuid.uuid4())) == 7

    @pytest.mark.asyncio
    async def test_none_vira_zero(self):
        db = _mock_db()
        result = MagicMock()
        result.scalar_one.return_value = None
        db.execute = AsyncMock(return_value=result)
        assert await notif.get_unread_count(db, str(uuid.uuid4())) == 0


class TestNotifyPeerReviewRequested:
    @pytest.mark.asyncio
    async def test_cria_notificacao_para_revisor(self):
        db = _mock_db()
        pr = _peer_review()
        parecer = _parecer()

        await notif.notify_peer_review_requested(db, pr, parecer)

        db.add.assert_called_once()
        created = db.add.call_args.args[0]
        assert created.user_id == pr.reviewer_id
        assert created.metadata_["type"] == "peer_review"
        assert created.link == f"/pareceres/{parecer.id}"
        db.flush.assert_awaited_once()


class TestNotifyPeerReviewCompleted:
    @pytest.mark.asyncio
    async def test_notifica_solicitante(self):
        db = _mock_db()
        pr = _peer_review()
        parecer = _parecer()

        await notif.notify_peer_review_completed(db, pr, parecer)

        created = db.add.call_args.args[0]
        assert created.user_id == pr.requested_by
        assert created.metadata_["type"] == "peer_review"


class TestNotifyParecerEvent:
    @pytest.mark.asyncio
    async def test_nao_levanta_sem_conexoes(self):
        # ws_manager sem conexões: broadcast é no-op; deve apenas agendar e não falhar
        await notif.notify_parecer_event("parecer.generated", uuid.uuid4(), status="gerado")
