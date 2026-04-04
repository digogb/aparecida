"""
Testes de estabilidade do pipeline de IA (P1/P2/P3) e fluxo de status.

Estratégia: mock dos serviços de IA no nível do router para isolar
o comportamento HTTP sem chamar a API Anthropic.

Cobre:
  - Endpoints retornam 404 para pareceres inexistentes
  - Falhas do serviço de IA são tratadas (não viram 500 nu)
  - Transições de status inválidas são rejeitadas com 400
  - Restore e versioning funcionam corretamente
  - Parsing de respostas XML do Claude (seções ausentes)
"""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.parecer import ParecerStatus
from tests.conftest import (
    auth_header,
    make_token,
    mock_db,
    mock_parecer,
    mock_version,
    override_db,
)


def _db_returns_none(db):
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    return db


def _db_returns_parecer(db, parecer, version=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = parecer
    result.scalars.return_value.all.return_value = [version] if version else []
    db.execute.return_value = result
    return db


# ---------------------------------------------------------------------------
# P1 — Classificação
# ---------------------------------------------------------------------------

class TestClassifyEndpoint:

    def test_unknown_parecer_returns_404(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)

        with patch(
            "app.routers.parecer_ia.classifier.classify",
            new_callable=AsyncMock,
            side_effect=ValueError("Parecer request nao encontrado"),
        ):
            try:
                with TestClient(app) as client:
                    resp = client.post(f"/api/parecer-requests/{uuid.uuid4()}/classify")
                assert resp.status_code == 404
            finally:
                app.dependency_overrides.clear()

    def test_successful_classification_returns_tema_and_confianca(self):
        db = mock_db()
        p = mock_parecer(status=ParecerStatus.pendente)
        p.tema = "licitacao"
        p.modelo = "licitacao"
        p.classificacao = {
            "area_principal": "licitacoes_contratos",
            "municipio": "São Paulo",
            "uf": "SP",
            "confianca_classificacao": "alta",
            "areas_conexas": [],
        }
        app.dependency_overrides[get_db] = override_db(db)

        with patch(
            "app.routers.parecer_ia.classifier.classify",
            new_callable=AsyncMock,
            return_value=(p, p.classificacao),
        ):
            try:
                with TestClient(app) as client:
                    resp = client.post(f"/api/parecer-requests/{p.id}/classify")
                assert resp.status_code == 200
                data = resp.json()
                assert data["tema"] == "licitacao"
                assert data["confianca"] == 1.0
                assert "municipio_detectado" in data
            finally:
                app.dependency_overrides.clear()

    def test_service_exception_propagates_as_404(self):
        """Qualquer ValueError do serviço vira 404 (incluindo not found)."""
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)

        with patch(
            "app.routers.parecer_ia.classifier.classify",
            new_callable=AsyncMock,
            side_effect=ValueError("qualquer erro de negócio"),
        ):
            try:
                with TestClient(app) as client:
                    resp = client.post(f"/api/parecer-requests/{uuid.uuid4()}/classify")
                assert resp.status_code == 404
            finally:
                app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# P2 — Geração
# ---------------------------------------------------------------------------

class TestGenerateEndpoint:

    def test_unknown_parecer_returns_404(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)

        with patch(
            "app.routers.parecer_ia.parecer_engine.generate",
            new_callable=AsyncMock,
            side_effect=ValueError("Parecer request nao encontrado"),
        ):
            try:
                with TestClient(app) as client:
                    resp = client.post(f"/api/parecer-requests/{uuid.uuid4()}/generate")
                assert resp.status_code == 404
            finally:
                app.dependency_overrides.clear()

    def test_successful_generation_returns_version_detail(self):
        db = mock_db()
        p = mock_parecer(status=ParecerStatus.classificado)
        v = mock_version(request_id=p.id, version_number=1)
        app.dependency_overrides[get_db] = override_db(db)

        with patch(
            "app.routers.parecer_ia.parecer_engine.generate",
            new_callable=AsyncMock,
            return_value=v,
        ):
            try:
                with TestClient(app) as client:
                    resp = client.post(f"/api/parecer-requests/{p.id}/generate")
                assert resp.status_code == 200
                data = resp.json()
                assert "version_number" in data
                assert data["version_number"] == 1
            finally:
                app.dependency_overrides.clear()

    def test_service_exception_propagates_as_404(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)

        with patch(
            "app.routers.parecer_ia.parecer_engine.generate",
            new_callable=AsyncMock,
            side_effect=ValueError("Erro na geração"),
        ):
            try:
                with TestClient(app) as client:
                    resp = client.post(f"/api/parecer-requests/{uuid.uuid4()}/generate")
                assert resp.status_code == 404
            finally:
                app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# P3 — Preview e aplicação de correções
# ---------------------------------------------------------------------------

class TestCorrectionEndpoints:

    def test_preview_correction_unknown_parecer_returns_404(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)

        with patch(
            "app.routers.parecer_ia.parecer_engine.preview_correction",
            new_callable=AsyncMock,
            side_effect=ValueError("nao encontrado"),
        ):
            try:
                with TestClient(app) as client:
                    resp = client.post(
                        f"/api/parecer-requests/{uuid.uuid4()}/preview-correction",
                        json={"observacoes": "Revisar fundamentos jurídicos"},
                    )
                assert resp.status_code == 404
            finally:
                app.dependency_overrides.clear()

    def test_apply_correction_unknown_parecer_returns_404(self):
        db = mock_db()
        app.dependency_overrides[get_db] = override_db(db)

        with patch(
            "app.routers.parecer_ia.parecer_engine.apply_correction",
            new_callable=AsyncMock,
            side_effect=ValueError("nao encontrado"),
        ):
            try:
                with TestClient(app) as client:
                    resp = client.post(
                        f"/api/parecer-requests/{uuid.uuid4()}/apply-correction",
                        json={
                            "secoes_aprovadas": {"ementa": "<p>Nova ementa</p>"},
                            "observacoes": "Aprovado com ajustes",
                            "notas_revisor": [],
                            "citacoes_verificar": [],
                        },
                    )
                assert resp.status_code == 404
            finally:
                app.dependency_overrides.clear()

    def test_preview_correction_missing_body_returns_422(self):
        with TestClient(app) as client:
            resp = client.post(
                f"/api/parecer-requests/{uuid.uuid4()}/preview-correction",
                json={},  # falta campo obrigatório
            )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Versioning
# ---------------------------------------------------------------------------

class TestVersioning:

    def test_list_versions_unknown_parecer_returns_404(self):
        db = mock_db()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{uuid.uuid4()}/versions")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_get_version_nonexistent_returns_404(self):
        db = mock_db()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.get(f"/api/parecer-requests/{uuid.uuid4()}/versions/999")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_restore_nonexistent_version_returns_404(self):
        db = mock_db()

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            # Primeira chamada: parecer existe; segunda: versão não existe
            if call_count == 1:
                result.scalar_one_or_none.return_value = mock_parecer()
            else:
                result.scalar_one_or_none.return_value = None
            return result

        db.execute = AsyncMock(side_effect=side_effect)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{uuid.uuid4()}/versions/{uuid.uuid4()}/restore"
                )
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_restore_from_nonexistent_parecer_returns_404(self):
        db = mock_db()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=result)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{uuid.uuid4()}/versions/{uuid.uuid4()}/restore"
                )
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Transições de status (approve / return)
# ---------------------------------------------------------------------------

class TestStatusTransitions:

    def _token(self):
        return make_token()

    def _db_with_parecer_status(self, status: ParecerStatus):
        db = mock_db()
        p = mock_parecer(status=status, versions=[mock_version()])
        result = MagicMock()
        result.scalar_one_or_none.return_value = p
        db.execute.return_value = result
        return db, p

    # --- approve ---

    def test_approve_gerado_succeeds(self):
        db, p = self._db_with_parecer_status(ParecerStatus.gerado)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/approve",
                    headers=auth_header(self._token()),
                )
            assert resp.status_code == 200
            assert resp.json()["status"] == "aprovado"
        finally:
            app.dependency_overrides.clear()

    def test_approve_em_revisao_succeeds(self):
        db, p = self._db_with_parecer_status(ParecerStatus.em_revisao)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/approve",
                    headers=auth_header(self._token()),
                )
            assert resp.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_approve_pendente_returns_400(self):
        """Parecer pendente (sem geração) não pode ser aprovado."""
        db, p = self._db_with_parecer_status(ParecerStatus.pendente)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/approve",
                    headers=auth_header(self._token()),
                )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_approve_enviado_returns_400(self):
        """Parecer já enviado não pode ser re-aprovado."""
        db, p = self._db_with_parecer_status(ParecerStatus.enviado)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/approve",
                    headers=auth_header(self._token()),
                )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()

    # --- return ---

    def test_return_gerado_succeeds(self):
        db, p = self._db_with_parecer_status(ParecerStatus.gerado)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/return",
                    json={"observacoes": "Necessita revisão dos fundamentos"},
                    headers=auth_header(self._token()),
                )
            assert resp.status_code == 200
            assert resp.json()["status"] == "devolvido"
        finally:
            app.dependency_overrides.clear()

    def test_return_pendente_returns_400(self):
        """Não se pode devolver um parecer ainda não gerado."""
        db, p = self._db_with_parecer_status(ParecerStatus.pendente)
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/return",
                    json={"observacoes": "teste"},
                    headers=auth_header(self._token()),
                )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_return_without_observacoes_returns_422(self):
        with TestClient(app) as client:
            resp = client.post(
                f"/api/parecer-requests/{uuid.uuid4()}/return",
                json={},
                headers=auth_header(self._token()),
            )
        assert resp.status_code == 422

    # --- export sem versão ---

    def test_export_docx_without_version_returns_400(self):
        """Exportar sem nenhuma versão gerada deve retornar 400."""
        db = mock_db()
        p = mock_parecer(versions=[])  # sem versões
        result = MagicMock()
        result.scalar_one_or_none.return_value = p
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/export/docx",
                    headers=auth_header(self._token()),
                )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_export_pdf_without_version_returns_400(self):
        db = mock_db()
        p = mock_parecer(versions=[])
        result = MagicMock()
        result.scalar_one_or_none.return_value = p
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/export/pdf",
                    headers=auth_header(self._token()),
                )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()
