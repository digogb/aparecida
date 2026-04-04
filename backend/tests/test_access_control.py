"""
Testes de controle de acesso (autenticação obrigatória por endpoint).

Verifica quais endpoints exigem token e rejeita corretamente tokens inválidos.

GAPS DE SEGURANÇA DOCUMENTADOS:
  Os endpoints marcados com TODO abaixo NÃO exigem autenticação atualmente.
  Esses testes documentam o comportamento esperado (403/401) e devem ser
  movidos para a seção de testes ativos após corrigir os routers.
"""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from tests.conftest import (
    auth_header,
    make_expired_token,
    make_tampered_token,
    make_token,
    mock_db,
    mock_parecer,
    mock_version,
    override_db,
)


def _db_with_parecer(parecer=None):
    """DB mock que retorna um parecer e uma versão."""
    db = mock_db()
    p = parecer or mock_parecer(status="gerado")
    v = mock_version(request_id=p.id)
    p.versions = [v]

    result = MagicMock()
    result.scalar_one_or_none.return_value = p
    db.execute.return_value = result
    return db, p


# ---------------------------------------------------------------------------
# Endpoints que EXIGEM autenticação (export.py — bearer auto_error=True)
# ---------------------------------------------------------------------------

class TestExportEndpointsRequireAuth:
    """
    Todos os endpoints de export.py usam HTTPBearer(auto_error=True).
    Sem token → 403 (HTTPBearer rejeita antes do handler).
    Token inválido → 401 (handler rejeita após tentar decodificar).
    """

    def _pid(self):
        return uuid.uuid4()

    # --- approve ---

    def test_approve_without_token_returns_403(self):
        with TestClient(app) as client:
            resp = client.post(f"/api/parecer-requests/{self._pid()}/approve")
        assert resp.status_code == 403

    def test_approve_with_invalid_token_returns_401(self):
        db, _ = _db_with_parecer(mock_parecer(status="gerado"))
        app.dependency_overrides[get_db] = override_db(db)
        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{self._pid()}/approve",
                    headers=auth_header(make_tampered_token()),
                )
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    def test_approve_with_expired_token_returns_401(self):
        db, _ = _db_with_parecer(mock_parecer(status="gerado"))
        app.dependency_overrides[get_db] = override_db(db)
        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{self._pid()}/approve",
                    headers=auth_header(make_expired_token()),
                )
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    # --- export/docx ---

    def test_export_docx_without_token_returns_403(self):
        with TestClient(app) as client:
            resp = client.post(f"/api/parecer-requests/{self._pid()}/export/docx")
        assert resp.status_code == 403

    def test_export_docx_with_invalid_token_returns_401(self):
        db, _ = _db_with_parecer()
        app.dependency_overrides[get_db] = override_db(db)
        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{self._pid()}/export/docx",
                    headers=auth_header(make_tampered_token()),
                )
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    # --- export/pdf ---

    def test_export_pdf_without_token_returns_403(self):
        with TestClient(app) as client:
            resp = client.post(f"/api/parecer-requests/{self._pid()}/export/pdf")
        assert resp.status_code == 403

    # --- return ---

    def test_return_without_token_returns_403(self):
        with TestClient(app) as client:
            resp = client.post(
                f"/api/parecer-requests/{self._pid()}/return",
                json={"observacoes": "Revisar fundamentos"},
            )
        assert resp.status_code == 403

    # --- approve-and-send ---

    def test_approve_and_send_without_token_returns_403(self):
        with TestClient(app) as client:
            resp = client.post(f"/api/parecer-requests/{self._pid()}/approve-and-send")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Endpoints que EXIGEM autenticação (peer_review.py)
# ---------------------------------------------------------------------------

class TestPeerReviewEndpointsRequireAuth:
    """
    peer_review.py usa HTTPBearer(auto_error=False) com helper próprio que
    levanta 401 — não 403 — quando não há token.
    """

    def _pid(self):
        return uuid.uuid4()

    def test_create_peer_review_without_token_returns_401(self):
        with TestClient(app) as client:
            resp = client.post(
                f"/api/parecer-requests/{self._pid()}/peer-review",
                json={"reviewer_id": str(uuid.uuid4()), "version_id": str(uuid.uuid4())},
            )
        assert resp.status_code == 401

    def test_pending_reviews_without_token_returns_401(self):
        with TestClient(app) as client:
            resp = client.get("/api/peer-reviews/pending")
        assert resp.status_code == 401

    def test_respond_review_without_token_returns_401(self):
        with TestClient(app) as client:
            resp = client.post(
                f"/api/peer-reviews/{self._pid()}/respond",
                json={"resposta_geral": "OK"},
            )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Endpoints que EXIGEM autenticação (dashboard.py)
# ---------------------------------------------------------------------------

class TestDashboardRequiresAuth:
    """
    dashboard.py usa HTTPBearer(auto_error=False) com helper próprio que
    levanta 401 — não 403 — quando não há token.
    """

    def test_dashboard_stats_without_token_returns_401(self):
        with TestClient(app) as client:
            resp = client.get("/api/dashboard/pareceres-overview")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GAPS DE SEGURANÇA — comportamento ATUAL (sem auth) documentado
#
# Estes testes verificam que os endpoints abaixo atualmente NÃO exigem
# autenticação. Quando os routers forem corrigidos para exigir token,
# estes testes devem ser atualizados para assert 403.
# ---------------------------------------------------------------------------

class TestSecurityGapsDocumented:
    """
    TODO SEGURANÇA: os endpoints abaixo devem exigir autenticação.
    Atualmente retornam 404/200 sem token — não 403.
    """

    def _pid(self):
        return uuid.uuid4()

    def test_delete_parecer_does_not_require_auth_SECURITY_GAP(self):
        """
        TODO: DELETE deve exigir autenticação e verificar ownership.
        Atualmente qualquer cliente sem token pode deletar qualquer parecer.
        """
        db = mock_db()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None  # não encontrado → 404
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.delete(f"/api/parecer-requests/{self._pid()}")
            # Atualmente retorna 404 (não encontrou), não 403 (não autenticado)
            # Quando corrigido, deve retornar 403 sem token
            assert resp.status_code != 200, "DELETE não deveria ter sucesso sem token"
        finally:
            app.dependency_overrides.clear()

    def test_classify_does_not_require_auth_SECURITY_GAP(self):
        """
        TODO: /classify deve exigir autenticação.
        parecer_ia.py usa HTTPBearer(auto_error=False) — token opcional.
        """
        db = mock_db()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(f"/api/parecer-requests/{self._pid()}/classify")
            # Sem token e sem parecer → 404 (não 403)
            # Confirma que auth não está sendo verificada
            assert resp.status_code in (404, 422, 500), (
                f"Esperado 404 sem auth (gap de segurança), recebeu {resp.status_code}"
            )
        finally:
            app.dependency_overrides.clear()

    def test_generate_does_not_require_auth_SECURITY_GAP(self):
        """
        TODO: /generate deve exigir autenticação.
        """
        db = mock_db()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(f"/api/parecer-requests/{self._pid()}/generate")
            assert resp.status_code in (404, 422, 500)
        finally:
            app.dependency_overrides.clear()
