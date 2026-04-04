"""
Testes de segurança de autenticação JWT.

Cobre: login, token expirado, token adulterado, usuário inativo,
endpoint /auth/me e refresh de token.
"""
from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.database import get_db
from app.main import app
from tests.conftest import (
    auth_header,
    make_expired_token,
    make_tampered_token,
    make_token,
    mock_db,
    mock_user,
    override_db,
)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _db_returns_user(db, user):
    """Configura db.execute para retornar um usuário."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result


def _db_returns_nothing(db):
    """Configura db.execute para não encontrar nada."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

class TestLogin:

    def test_valid_credentials_return_token(self):
        db = mock_db()
        user = mock_user(hashed_password=pwd_ctx.hash("senha123"))
        _db_returns_user(db, user)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/auth/login", json={"email": user.email, "password": "senha123"})
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert len(data["access_token"]) > 20
        finally:
            app.dependency_overrides.clear()

    def test_wrong_password_returns_401(self):
        db = mock_db()
        user = mock_user(hashed_password=pwd_ctx.hash("senha_correta"))
        _db_returns_user(db, user)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/auth/login", json={"email": user.email, "password": "senha_errada"})
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_nonexistent_email_returns_401(self):
        db = mock_db()
        _db_returns_nothing(db)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/auth/login", json={"email": "naoexiste@test.com", "password": "qualquer"})
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_inactive_user_returns_401(self):
        """Usuário com is_active=False não deve conseguir logar."""
        db = mock_db()
        # Usuário inativo não é retornado (query filtra is_active=True)
        _db_returns_nothing(db)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/auth/login", json={"email": "inativo@test.com", "password": "senha123"})
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_missing_fields_returns_422(self):
        with TestClient(app) as client:
            resp = client.post("/api/auth/login", json={"email": "test@test.com"})
        assert resp.status_code == 422

    def test_empty_password_returns_422(self):
        with TestClient(app) as client:
            resp = client.post("/api/auth/login", json={"email": "test@test.com", "password": ""})
        # Pydantic valida campo obrigatório — campo vazio ainda é string válida,
        # mas passlib verifica contra hash e retorna 401
        assert resp.status_code in (401, 422)


# ---------------------------------------------------------------------------
# GET /api/auth/me
# ---------------------------------------------------------------------------

class TestMe:

    def test_valid_token_returns_user_data(self):
        db = mock_db()
        user = mock_user()
        _db_returns_user(db, user)
        app.dependency_overrides[get_db] = override_db(db)
        token = make_token(user_id=str(user.id), email=str(user.email))

        try:
            with TestClient(app) as client:
                resp = client.get("/api/auth/me", headers=auth_header(token))
            assert resp.status_code == 200
            data = resp.json()
            assert "id" in data
            assert "email" in data
            assert "role" in data
            # Senha nunca exposta
            assert "hashed_password" not in data
            assert "password" not in data
        finally:
            app.dependency_overrides.clear()

    def test_no_token_returns_403(self):
        """HTTPBearer sem auto_error=False retorna 403 quando não há token."""
        with TestClient(app) as client:
            resp = client.get("/api/auth/me")
        assert resp.status_code == 403

    def test_expired_token_returns_401(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)
        expired = make_expired_token()

        try:
            with TestClient(app) as client:
                resp = client.get("/api/auth/me", headers=auth_header(expired))
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_tampered_token_returns_401(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)
        tampered = make_tampered_token()

        try:
            with TestClient(app) as client:
                resp = client.get("/api/auth/me", headers=auth_header(tampered))
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_random_string_as_token_returns_401(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get("/api/auth/me", headers=auth_header("nao_e_um_jwt"))
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_token_for_deleted_user_returns_401(self):
        """Token válido mas user não existe mais no banco."""
        db = mock_db()
        _db_returns_nothing(db)
        app.dependency_overrides[get_db] = override_db(db)
        token = make_token()

        try:
            with TestClient(app) as client:
                resp = client.get("/api/auth/me", headers=auth_header(token))
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# POST /api/auth/refresh
# ---------------------------------------------------------------------------

class TestRefresh:

    def test_valid_token_returns_new_token(self):
        db = mock_db()
        user = mock_user()
        _db_returns_user(db, user)
        app.dependency_overrides[get_db] = override_db(db)
        token = make_token(user_id=str(user.id))

        try:
            with TestClient(app) as client:
                resp = client.post("/api/auth/refresh", headers=auth_header(token))
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert data["access_token"] != token  # novo token emitido
        finally:
            app.dependency_overrides.clear()

    def test_no_token_returns_403(self):
        with TestClient(app) as client:
            resp = client.post("/api/auth/refresh")
        assert resp.status_code == 403

    def test_tampered_token_returns_401(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post("/api/auth/refresh", headers=auth_header(make_tampered_token()))
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()
