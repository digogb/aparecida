"""
Tests for parecer and gmail_webhook routers.
Run with: pytest backend/tests/test_routers_parecer.py -v
"""
import base64
import json
import os
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.parecer import ExtractionStatus, ParecerRequest, ParecerStatus, ParecerTema


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _mock_parecer(**overrides) -> MagicMock:
    """Return a MagicMock that quacks like a ParecerRequest ORM instance."""
    defaults = dict(
        id=uuid.uuid4(),
        municipio_id=None,
        assigned_to=None,
        gmail_thread_id="thread_abc",
        gmail_message_id="msg_abc",
        subject="Consulta juridica",
        sender_email="prefeitura@example.com",
        status=ParecerStatus.pendente,
        tema=None,
        numero_parecer=None,
        extraction_status=None,
        extracted_text=None,
        raw_payload={},
        created_at=_now(),
        updated_at=_now(),
        attachments=[],
        versions=[],
    )
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _mock_db() -> AsyncMock:
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


def _override_db(db: AsyncMock):
    """Return a FastAPI dependency override for get_db."""
    async def _dep():
        yield db
    return _dep


def _execute_side_effects(*results):
    """
    Build side_effect list where each item is an awaitable returning a result mock.
    Each element of *results is the mock returned from db.execute().
    """
    return results


# ---------------------------------------------------------------------------
# GET /api/parecer-requests
# ---------------------------------------------------------------------------

class TestListParecerRequests:

    def test_returns_200_empty_list(self):
        db = _mock_db()

        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 0

        list_mock = MagicMock()
        list_mock.scalars.return_value.all.return_value = []

        db.execute.side_effect = [count_mock, list_mock]
        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests")
            assert resp.status_code == 200
            data = resp.json()
            assert data["items"] == []
            assert data["total"] == 0
            assert data["limit"] == 20
            assert data["offset"] == 0
        finally:
            app.dependency_overrides.clear()

    def test_returns_200_with_items(self):
        db = _mock_db()
        p = _mock_parecer()

        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 1

        list_mock = MagicMock()
        list_mock.scalars.return_value.all.return_value = [p]

        db.execute.side_effect = [count_mock, list_mock]
        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests")
            assert resp.status_code == 200
            data = resp.json()
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["status"] == "pendente"
        finally:
            app.dependency_overrides.clear()

    def test_filter_by_status(self):
        db = _mock_db()

        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 0
        list_mock = MagicMock()
        list_mock.scalars.return_value.all.return_value = []

        db.execute.side_effect = [count_mock, list_mock]
        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests?status=pendente")
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_filter_by_tema(self):
        db = _mock_db()

        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 0
        list_mock = MagicMock()
        list_mock.scalars.return_value.all.return_value = []

        db.execute.side_effect = [count_mock, list_mock]
        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests?tema=licitacao")
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_filter_by_remetente(self):
        db = _mock_db()

        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 0
        list_mock = MagicMock()
        list_mock.scalars.return_value.all.return_value = []

        db.execute.side_effect = [count_mock, list_mock]
        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests?remetente=prefeitura")
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_filter_by_municipio_id(self):
        db = _mock_db()
        mid = uuid.uuid4()

        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 0
        list_mock = MagicMock()
        list_mock.scalars.return_value.all.return_value = []

        db.execute.side_effect = [count_mock, list_mock]
        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests?municipio_id={mid}")
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_pagination_params_reflected_in_response(self):
        db = _mock_db()

        count_mock = MagicMock()
        count_mock.scalar_one.return_value = 0
        list_mock = MagicMock()
        list_mock.scalars.return_value.all.return_value = []

        db.execute.side_effect = [count_mock, list_mock]
        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests?limit=5&offset=10")
            assert resp.status_code == 200
            data = resp.json()
            assert data["limit"] == 5
            assert data["offset"] == 10
        finally:
            app.dependency_overrides.clear()

    def test_invalid_status_returns_422(self):
        with TestClient(app) as client:
            resp = client.get("/api/parecer-requests?status=invalido")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/parecer-requests/{id}
# ---------------------------------------------------------------------------

class TestGetParecerRequest:

    def test_returns_200_with_detail(self):
        db = _mock_db()
        p = _mock_parecer()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{p.id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == str(p.id)
            assert data["attachments"] == []
            assert data["versions"] == []
        finally:
            app.dependency_overrides.clear()

    def test_returns_404_when_not_found(self):
        db = _mock_db()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{uuid.uuid4()}")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_returns_422_for_invalid_uuid(self):
        with TestClient(app) as client:
            resp = client.get("/api/parecer-requests/not-a-uuid")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/parecer-requests/{id}/retry-extraction
# ---------------------------------------------------------------------------

class TestRetryExtraction:

    def test_resets_extraction_status(self):
        db = _mock_db()
        p = _mock_parecer(extraction_status=ExtractionStatus.failed)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(f"/api/parecer-requests/{p.id}/retry-extraction")
            assert resp.status_code == 200
            db.commit.assert_awaited_once()
            assert p.extraction_status is None
            assert p.extracted_text is None
        finally:
            app.dependency_overrides.clear()

    def test_returns_400_when_not_failed(self):
        db = _mock_db()
        p = _mock_parecer(extraction_status=ExtractionStatus.success)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(f"/api/parecer-requests/{p.id}/retry-extraction")
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_returns_400_when_no_extraction_status(self):
        db = _mock_db()
        p = _mock_parecer(extraction_status=None)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(f"/api/parecer-requests/{p.id}/retry-extraction")
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_returns_404_when_not_found(self):
        db = _mock_db()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(f"/api/parecer-requests/{uuid.uuid4()}/retry-extraction")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/gmail/webhook
# ---------------------------------------------------------------------------

class TestGmailWebhook:

    def _pubsub_payload(self, history_id: str = "99999", email: str = "test@pref.sp.gov.br", message_id: str = "msg_001") -> dict:
        data = base64.b64encode(
            json.dumps({"emailAddress": email, "historyId": history_id}).encode()
        ).decode()
        return {
            "message": {"data": data, "messageId": message_id},
            "subscription": "projects/proj/subscriptions/gmail-push",
        }

    def test_creates_parecer_request(self):
        db = _mock_db()

        # duplicate check returns None (no existing record)
        check_mock = MagicMock()
        check_mock.scalar_one_or_none.return_value = None
        db.execute.return_value = check_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/gmail/webhook", json=self._pubsub_payload())
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert "request_id" in data
            db.add.assert_called_once()
            db.commit.assert_awaited_once()
        finally:
            app.dependency_overrides.clear()

    def test_duplicate_webhook_skips_creation(self):
        db = _mock_db()

        existing = MagicMock()
        check_mock = MagicMock()
        check_mock.scalar_one_or_none.return_value = existing
        db.execute.return_value = check_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/gmail/webhook", json=self._pubsub_payload())
            assert resp.status_code == 200
            data = resp.json()
            assert data["action"] == "duplicate"
            db.add.assert_not_called()
        finally:
            app.dependency_overrides.clear()

    def test_invalid_token_returns_403(self):
        with patch.dict(os.environ, {"PUBSUB_VERIFICATION_TOKEN": "secret"}):
            with TestClient(app) as client:
                resp = client.post(
                    "/api/gmail/webhook?token=wrong",
                    json=self._pubsub_payload(),
                )
        assert resp.status_code == 403

    def test_valid_token_accepted(self):
        db = _mock_db()

        check_mock = MagicMock()
        check_mock.scalar_one_or_none.return_value = None
        db.execute.return_value = check_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with patch.dict(os.environ, {"PUBSUB_VERIFICATION_TOKEN": "secret"}):
                with TestClient(app) as client:
                    resp = client.post(
                        "/api/gmail/webhook?token=secret",
                        json=self._pubsub_payload(),
                    )
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_empty_payload_handled_gracefully(self):
        db = _mock_db()

        check_mock = MagicMock()
        check_mock.scalar_one_or_none.return_value = None
        db.execute.return_value = check_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/gmail/webhook", json={})
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()
