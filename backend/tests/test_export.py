"""
Tests for export router, export_service, and email_sender.
Run with: pytest backend/tests/test_export.py -v
"""
import shutil
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.config import settings
from app.database import get_db
from app.main import app
from app.models.parecer import ParecerStatus, ParecerTema, VersionSource
from app.models.user import UserRole

# Testes de PDF dependem do binário `soffice` (LibreOffice). Em ambientes de
# dev/CI sem LibreOffice instalado, são automaticamente pulados.
requires_soffice = pytest.mark.skipif(
    shutil.which("soffice") is None,
    reason="LibreOffice (soffice) not installed — PDF export tests skipped",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_token(user_id: str | None = None) -> str:
    uid = user_id or str(uuid.uuid4())
    payload = {"sub": uid, "email": "test@ione.adv.br", "role": "advogado"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def _auth_header(token: str | None = None) -> dict:
    return {"Authorization": f"Bearer {token or _make_token()}"}


def _mock_version(**overrides) -> MagicMock:
    defaults = dict(
        id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        version_number=1,
        source=VersionSource.ia_gerado,
        content_tiptap={
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Parecer Juridico"}],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Este e o "},
                        {
                            "type": "text",
                            "marks": [{"type": "bold"}],
                            "text": "parecer",
                        },
                        {"type": "text", "text": " juridico."},
                    ],
                },
            ],
        },
        content_html="<h1>Parecer Juridico</h1><p>Este e o <b>parecer</b> juridico.</p>",
        reprocess_instructions=None,
        created_by=None,
        created_at=_now(),
        updated_at=_now(),
    )
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _mock_parecer(**overrides) -> MagicMock:
    version = _mock_version()
    defaults = dict(
        id=uuid.uuid4(),
        municipio_id=None,
        assigned_to=None,
        gmail_thread_id="thread_abc",
        gmail_message_id="msg_abc",
        subject="Consulta sobre licitacao",
        sender_email="prefeitura@saocarlos.sp.gov.br",
        status=ParecerStatus.em_revisao,
        tema=ParecerTema.licitacao,
        numero_parecer="2026/001",
        extraction_status=None,
        extracted_text=None,
        raw_payload={},
        created_at=_now(),
        updated_at=_now(),
        attachments=[],
        versions=[version],
    )
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _mock_advogado(name: str = "Matheus Nogueira", role=UserRole.advogado) -> MagicMock:
    m = MagicMock()
    m.name = name
    m.role = role
    m.is_active = True
    return m


def _mock_db() -> AsyncMock:
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


def _override_db(db: AsyncMock):
    async def _dep():
        yield db
    return _dep


# ---------------------------------------------------------------------------
# Unit tests — DOCX generation
# ---------------------------------------------------------------------------

class TestToDocx:

    @pytest.mark.asyncio
    async def test_generates_docx_bytes(self):
        req = _mock_parecer()
        version = req.versions[0]

        db = _mock_db()
        advogados_result = MagicMock()
        advogados_result.scalars.return_value.all.return_value = [
            _mock_advogado("Francisco Ione", UserRole.admin),
            _mock_advogado("Matheus Nogueira", UserRole.advogado),
        ]
        db.execute.return_value = advogados_result

        from app.services.export_service import to_docx

        docx_bytes = await to_docx(req, version, db)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0
        # DOCX magic bytes (PK zip header)
        assert docx_bytes[:2] == b"PK"

    @pytest.mark.asyncio
    async def test_generates_docx_from_html_fallback(self):
        req = _mock_parecer()
        version = req.versions[0]
        version.content_tiptap = None  # force HTML fallback

        db = _mock_db()
        advogados_result = MagicMock()
        advogados_result.scalars.return_value.all.return_value = []
        db.execute.return_value = advogados_result

        from app.services.export_service import to_docx

        docx_bytes = await to_docx(req, version, db)
        assert isinstance(docx_bytes, bytes)
        assert docx_bytes[:2] == b"PK"


# ---------------------------------------------------------------------------
# Unit tests — PDF generation
# ---------------------------------------------------------------------------

class TestToPdf:

    @requires_soffice
    @pytest.mark.asyncio
    async def test_generates_pdf_bytes(self):
        req = _mock_parecer()
        version = req.versions[0]

        db = _mock_db()
        advogados_result = MagicMock()
        advogados_result.scalars.return_value.all.return_value = [
            _mock_advogado("Francisco Ione", UserRole.admin),
        ]
        db.execute.return_value = advogados_result

        from app.services.export_service import to_pdf

        pdf_bytes = await to_pdf(req, version, db)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDF magic bytes
        assert pdf_bytes[:4] == b"%PDF"

# ---------------------------------------------------------------------------
# Unit tests — email_sender
# ---------------------------------------------------------------------------

class TestEmailSender:

    @pytest.mark.asyncio
    async def test_send_parecer_calls_gmail(self):
        req = _mock_parecer(status=ParecerStatus.aprovado)
        db = _mock_db()

        mock_service = MagicMock()
        mock_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
            "id": "sent_123"
        }

        with patch(
            "app.services.email_sender._build_gmail_service",
            return_value=mock_service,
        ):
            from app.services.email_sender import send_parecer

            await send_parecer(req, b"fake-docx", b"fake-pdf", db, changed_by_id=str(uuid.uuid4()))

        # Gmail send was called
        mock_service.users.return_value.messages.return_value.send.assert_called_once()
        # Status updated
        assert req.status == ParecerStatus.enviado
        db.add.assert_called_once()
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_raises_without_sender_email(self):
        req = _mock_parecer(sender_email=None)
        db = _mock_db()

        from app.services.email_sender import send_parecer

        with pytest.raises(ValueError, match="sender_email"):
            await send_parecer(req, b"fake-docx", b"fake-pdf", db)

    def test_email_body_template(self):
        from app.services.email_sender import _build_email_body

        req = _mock_parecer()
        body = _build_email_body(req)
        assert "2026/001" in body
        assert "Ione Advogados" in body
        assert "Consulta sobre licitacao" in body


# ---------------------------------------------------------------------------
# Router integration tests — POST /api/parecer-requests/{id}/approve
# ---------------------------------------------------------------------------

class TestApproveEndpoint:

    def test_approve_returns_200(self):
        db = _mock_db()
        p = _mock_parecer(status=ParecerStatus.em_revisao)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/approve",
                    headers=_auth_header(),
                )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "aprovado"
            assert p.status == ParecerStatus.aprovado
            db.add.assert_called_once()
            db.commit.assert_awaited_once()
        finally:
            app.dependency_overrides.clear()

    def test_approve_rejects_pendente(self):
        db = _mock_db()
        p = _mock_parecer(status=ParecerStatus.pendente)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/approve",
                    headers=_auth_header(),
                )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_approve_returns_404(self):
        db = _mock_db()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{uuid.uuid4()}/approve",
                    headers=_auth_header(),
                )
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_approve_requires_auth(self):
        with TestClient(app) as client:
            resp = client.post(f"/api/parecer-requests/{uuid.uuid4()}/approve")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Router integration tests — POST /api/parecer-requests/{id}/return
# ---------------------------------------------------------------------------

class TestReturnEndpoint:

    def test_return_with_observacoes(self):
        db = _mock_db()
        p = _mock_parecer(status=ParecerStatus.em_revisao)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/return",
                    json={"observacoes": "Precisa revisar fundamentacao"},
                    headers=_auth_header(),
                )
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "devolvido"
            assert p.status == ParecerStatus.devolvido
        finally:
            app.dependency_overrides.clear()

    def test_return_rejects_enviado(self):
        db = _mock_db()
        p = _mock_parecer(status=ParecerStatus.enviado)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/return",
                    json={"observacoes": "Nao deveria funcionar"},
                    headers=_auth_header(),
                )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_return_requires_observacoes(self):
        with TestClient(app) as client:
            resp = client.post(
                f"/api/parecer-requests/{uuid.uuid4()}/return",
                json={},
                headers=_auth_header(),
            )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Router integration tests — POST /api/parecer-requests/{id}/export/docx
# ---------------------------------------------------------------------------

class TestExportDocxEndpoint:

    def test_export_docx_returns_file(self):
        db = _mock_db()
        p = _mock_parecer()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p

        advogados_result = MagicMock()
        advogados_result.scalars.return_value.all.return_value = [
            _mock_advogado()
        ]

        # First call: load request; second call: get advogados
        db.execute.side_effect = [result_mock, advogados_result]

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/export/docx",
                    headers=_auth_header(),
                )
            assert resp.status_code == 200
            assert "application/vnd.openxmlformats" in resp.headers["content-type"]
            assert resp.content[:2] == b"PK"
        finally:
            app.dependency_overrides.clear()

    def test_export_docx_no_versions_returns_400(self):
        db = _mock_db()
        p = _mock_parecer(versions=[])

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p
        db.execute.return_value = result_mock

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/export/docx",
                    headers=_auth_header(),
                )
            assert resp.status_code == 400
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Router integration tests — POST /api/parecer-requests/{id}/export/pdf
# ---------------------------------------------------------------------------

class TestExportPdfEndpoint:

    @requires_soffice
    def test_export_pdf_returns_file(self):
        db = _mock_db()
        p = _mock_parecer()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p

        advogados_result = MagicMock()
        advogados_result.scalars.return_value.all.return_value = [
            _mock_advogado()
        ]

        db.execute.side_effect = [result_mock, advogados_result]

        app.dependency_overrides[get_db] = _override_db(db)

        try:
            with TestClient(app) as client:
                resp = client.post(
                    f"/api/parecer-requests/{p.id}/export/pdf",
                    headers=_auth_header(),
                )
            assert resp.status_code == 200
            assert resp.headers["content-type"] == "application/pdf"
            assert resp.content[:4] == b"%PDF"
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Router integration tests — POST /api/parecer-requests/{id}/approve-and-send
# ---------------------------------------------------------------------------

class TestApproveAndSendEndpoint:

    def test_approve_and_send_returns_200(self):
        db = _mock_db()
        p = _mock_parecer(status=ParecerStatus.em_revisao)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = p

        advogados_result = MagicMock()
        advogados_result.scalars.return_value.all.return_value = [
            _mock_advogado()
        ]

        db.execute.side_effect = [result_mock, advogados_result]

        mock_service = MagicMock()
        mock_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
            "id": "sent_123"
        }

        with patch(
            "app.services.email_sender._build_gmail_service",
            return_value=mock_service,
        ):
            app.dependency_overrides[get_db] = _override_db(db)
            try:
                with TestClient(app) as client:
                    resp = client.post(
                        f"/api/parecer-requests/{p.id}/approve-and-send",
                        headers=_auth_header(),
                    )
                assert resp.status_code == 200
                data = resp.json()
                assert data["status"] == "enviado"
            finally:
                app.dependency_overrides.clear()
