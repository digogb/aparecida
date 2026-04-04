"""
Testes de contrato de API.

Garantem que os schemas de resposta dos endpoints não mudam silenciosamente
entre deploys, quebrando o frontend. Se um campo mudar de nome ou desaparecer,
estes testes falham antes de ir para produção.

Campos verificados são os que o frontend consome diretamente (parecerApi.ts,
dashboardApi.ts, editorApi.ts).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.database import get_db
from app.main import app
from app.models.parecer import (
    ExtractionStatus,
    ParecerStatus,
    ParecerTema,
    ParecerVersion,
    VersionSource,
)
from tests.conftest import (
    auth_header,
    make_token,
    mock_db,
    mock_parecer,
    mock_user,
    mock_version,
    override_db,
)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# GET /api/parecer-requests — lista paginada
# ---------------------------------------------------------------------------

class TestParecerListContract:

    def test_response_has_pagination_fields(self):
        db = mock_db()
        count = MagicMock()
        count.scalar_one.return_value = 0
        lst = MagicMock()
        lst.scalars.return_value.all.return_value = []
        db.execute.side_effect = [count, lst]
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests")
            assert resp.status_code == 200
            data = resp.json()
            for field in ("items", "total", "limit", "offset"):
                assert field in data, f"Campo de paginação '{field}' ausente na resposta"
        finally:
            app.dependency_overrides.clear()

    def test_item_has_fields_consumed_by_frontend(self):
        """
        Campos que parecerApi.ts usa diretamente.
        Se qualquer um sumir, o frontend quebra silenciosamente.
        """
        db = mock_db()
        p = mock_parecer()
        count = MagicMock()
        count.scalar_one.return_value = 1
        lst = MagicMock()
        lst.scalars.return_value.all.return_value = [p]
        db.execute.side_effect = [count, lst]
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests")
            assert resp.status_code == 200
            items = resp.json()["items"]
            assert len(items) == 1
            item = items[0]
            required_fields = [
                "id",
                "status",
                "sender_email",
                "subject",
                "created_at",
            ]
            for field in required_fields:
                assert field in item, f"Campo '{field}' ausente no item da lista de pareceres"
        finally:
            app.dependency_overrides.clear()

    def test_status_values_are_valid_enum_strings(self):
        """Status deve ser uma das strings conhecidas — frontend usa para filtros visuais."""
        db = mock_db()
        p = mock_parecer(status=ParecerStatus.gerado)
        count = MagicMock()
        count.scalar_one.return_value = 1
        lst = MagicMock()
        lst.scalars.return_value.all.return_value = [p]
        db.execute.side_effect = [count, lst]
        app.dependency_overrides[get_db] = override_db(db)

        valid_statuses = {
            "pendente", "classificado", "gerado", "em_correcao",
            "em_revisao", "devolvido", "aprovado", "enviado", "erro",
        }

        try:
            with TestClient(app) as client:
                resp = client.get("/api/parecer-requests")
            item = resp.json()["items"][0]
            assert item["status"] in valid_statuses, (
                f"Status '{item['status']}' não é um valor válido conhecido pelo frontend"
            )
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /api/parecer-requests/{id} — detalhe
# ---------------------------------------------------------------------------

class TestParecerDetailContract:

    def test_detail_has_all_required_fields(self):
        db = mock_db()
        p = mock_parecer()
        result = MagicMock()
        result.scalar_one_or_none.return_value = p
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{p.id}")
            assert resp.status_code == 200
            data = resp.json()
            required_fields = [
                "id",
                "status",
                "sender_email",
                "subject",
                "created_at",
                "attachments",
                "versions",
            ]
            for field in required_fields:
                assert field in data, (
                    f"Campo '{field}' ausente no detalhe do parecer — frontend vai quebrar"
                )
        finally:
            app.dependency_overrides.clear()

    def test_detail_attachments_is_list(self):
        db = mock_db()
        p = mock_parecer(attachments=[])
        result = MagicMock()
        result.scalar_one_or_none.return_value = p
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{p.id}")
            assert isinstance(resp.json()["attachments"], list)
        finally:
            app.dependency_overrides.clear()

    def test_detail_versions_is_list(self):
        db = mock_db()
        p = mock_parecer(versions=[])
        result = MagicMock()
        result.scalar_one_or_none.return_value = p
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{p.id}")
            assert isinstance(resp.json()["versions"], list)
        finally:
            app.dependency_overrides.clear()

    def test_detail_returns_404_not_500_for_unknown_id(self):
        """Não deve retornar 500 para UUID válido mas inexistente."""
        db = mock_db()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{uuid.uuid4()}")
            assert resp.status_code == 404
            assert resp.status_code != 500
        finally:
            app.dependency_overrides.clear()

    def test_invalid_uuid_returns_422_not_500(self):
        with TestClient(app) as client:
            resp = client.get("/api/parecer-requests/nao-e-um-uuid-valido")
        assert resp.status_code == 422
        assert resp.status_code != 500


# ---------------------------------------------------------------------------
# POST /api/auth/login — contrato de token
# ---------------------------------------------------------------------------

class TestAuthContract:

    def test_login_response_has_access_token(self):
        db = mock_db()
        user = mock_user(hashed_password=pwd_ctx.hash("senha123"))
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/auth/login", json={"email": user.email, "password": "senha123"})
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data, "Campo 'access_token' ausente — frontend não consegue autenticar"
            # Não deve expor outros campos sensíveis
            assert "hashed_password" not in data
            assert "refresh_token" not in data  # não existe no sistema
        finally:
            app.dependency_overrides.clear()

    def test_me_response_has_user_fields(self):
        db = mock_db()
        user = mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)
        token = make_token(user_id=str(user.id), email=str(user.email))

        try:
            with TestClient(app) as client:
                resp = client.get("/api/auth/me", headers=auth_header(token))
            assert resp.status_code == 200
            data = resp.json()
            for field in ("id", "email", "role", "name"):
                assert field in data, f"Campo '{field}' ausente em /auth/me"
            # Senha NUNCA deve aparecer
            assert "hashed_password" not in data
            assert "password" not in data
        finally:
            app.dependency_overrides.clear()

    def test_me_role_is_valid_enum(self):
        db = mock_db()
        user = mock_user()
        result = MagicMock()
        result.scalar_one_or_none.return_value = user
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)
        token = make_token(user_id=str(user.id))

        try:
            with TestClient(app) as client:
                resp = client.get("/api/auth/me", headers=auth_header(token))
            data = resp.json()
            if "role" in data:
                assert data["role"] in ("advogado", "secretaria", "admin"), (
                    f"Role '{data['role']}' não é um valor válido"
                )
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/parecer-requests/{id}/approve — contrato de resposta
# ---------------------------------------------------------------------------

class TestApproveContract:

    def test_approve_response_has_status_and_message(self):
        db = mock_db()
        p = mock_parecer(status=ParecerStatus.gerado, versions=[mock_version()])
        result = MagicMock()
        result.scalar_one_or_none.return_value = p
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)
        token = make_token()

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/approve",
                    headers=auth_header(token),
                )
            assert resp.status_code == 200
            data = resp.json()
            for field in ("id", "status", "message"):
                assert field in data, f"Campo '{field}' ausente na resposta de /approve"
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /api/parecer-requests/{id}/versions — contrato
# ---------------------------------------------------------------------------

class TestVersionsContract:

    def test_versions_list_returns_array(self):
        db = mock_db()
        p = mock_parecer()
        v = mock_version(request_id=p.id)

        call_count = 0

        async def execute_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            if call_count == 1:
                # Checagem do parecer
                result.scalar_one_or_none.return_value = p
            else:
                # Lista de versões
                result.scalars.return_value.all.return_value = [v]
            return result

        from unittest.mock import AsyncMock
        db.execute = AsyncMock(side_effect=execute_side_effect)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{p.id}/versions")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Saúde da API
# ---------------------------------------------------------------------------

class TestHealthEndpoint:

    def test_health_returns_200(self):
        with TestClient(app) as client:
            resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_health_does_not_require_auth(self):
        """Health check nunca deve exigir autenticação — usado por load balancers."""
        with TestClient(app) as client:
            resp = client.get("/health")
        assert resp.status_code == 200
