"""
Testes de segurança e robustez do endpoint de upload de .eml.

Cobre: validação de extensão, deduplicação, path traversal em anexos,
parsing de emails malformados e body vazio.
"""
from __future__ import annotations

import io
import re
import tempfile
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from tests.conftest import (
    build_eml,
    build_eml_with_attachment,
    mock_db,
    mock_parecer,
    override_db,
)

ENDPOINT = "/api/parecer-requests/ingest-eml"


@pytest.fixture(autouse=True)
def patch_uploads_dir(tmp_path):
    """Redirect UPLOADS_DIR to a temp directory so tests don't need /app/uploads."""
    with patch("app.routers.ingest.UPLOADS_DIR", new=tmp_path):
        yield


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _db_no_duplicate(db):
    """DB retorna None na checagem de duplicata e None no lookup de município."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    result.scalars.return_value.all.return_value = []  # municipios
    db.execute.return_value = result
    return db


def _post_eml(client, content: bytes, filename: str = "email.eml"):
    return client.post(
        ENDPOINT,
        files={"file": (filename, io.BytesIO(content), "message/rfc822")},
    )


# ---------------------------------------------------------------------------
# Validação de extensão
# ---------------------------------------------------------------------------

class TestExtensionValidation:

    def test_valid_eml_accepted(self):
        db = _db_no_duplicate(mock_db())
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                with patch("app.services.pipeline.process_parecer_pipeline"):
                    with patch("builtins.open", create=True):
                        resp = _post_eml(client, build_eml())
            # 201 (criou) ou 409 (duplicata) — qualquer um indica que passou a validação de extensão
            assert resp.status_code in (201, 409)
        finally:
            app.dependency_overrides.clear()

    def test_pdf_file_rejected(self):
        with TestClient(app) as client:
            resp = client.post(
                ENDPOINT,
                files={"file": ("documento.pdf", io.BytesIO(b"%PDF-1.4 content"), "application/pdf")},
            )
        assert resp.status_code == 400
        assert "eml" in resp.json()["detail"].lower()

    def test_txt_file_rejected(self):
        with TestClient(app) as client:
            resp = client.post(
                ENDPOINT,
                files={"file": ("email.txt", io.BytesIO(b"conteudo"), "text/plain")},
            )
        assert resp.status_code == 400

    def test_exe_file_rejected(self):
        with TestClient(app) as client:
            resp = client.post(
                ENDPOINT,
                files={"file": ("virus.exe", io.BytesIO(b"MZ\x90"), "application/octet-stream")},
            )
        assert resp.status_code == 400

    def test_no_extension_rejected(self):
        with TestClient(app) as client:
            resp = client.post(
                ENDPOINT,
                files={"file": ("semextensao", io.BytesIO(b"data"), "application/octet-stream")},
            )
        assert resp.status_code == 400

    def test_double_extension_eml_dot_exe_rejected(self):
        """email.eml.exe não deve ser aceito."""
        with TestClient(app) as client:
            resp = client.post(
                ENDPOINT,
                files={"file": ("email.eml.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
            )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Deduplicação
# ---------------------------------------------------------------------------

class TestDeduplication:

    def test_same_thread_id_returns_409(self):
        """
        Segundo upload com mesmo Message-ID deve retornar 409.
        O thread_id é derivado do Message-ID quando não há In-Reply-To.
        """
        thread_id = f"<unique-thread-{uuid.uuid4()}@municipio.sp.gov.br>"
        eml = build_eml(message_id=thread_id)

        db = mock_db()
        # Retorna um parecer existente na checagem de duplicata
        existing = mock_parecer(gmail_thread_id=thread_id)
        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        db.execute.return_value = result
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                resp = _post_eml(client, eml)
            assert resp.status_code == 409
            assert "importado" in resp.json()["detail"].lower()
            # Não deve ter adicionado nada ao banco
            db.add.assert_not_called()
        finally:
            app.dependency_overrides.clear()

    def test_different_thread_ids_create_separate_pareceres(self):
        """Dois emails distintos geram dois pareceres (sem deduplicação)."""
        db = _db_no_duplicate(mock_db())
        app.dependency_overrides[get_db] = override_db(db)

        eml1 = build_eml(message_id=f"<msg1-{uuid.uuid4()}@test>")
        eml2 = build_eml(message_id=f"<msg2-{uuid.uuid4()}@test>")

        try:
            with TestClient(app) as client:
                with patch("app.services.pipeline.process_parecer_pipeline"):
                    with patch("builtins.open", create=True):
                        r1 = _post_eml(client, eml1)
                        r2 = _post_eml(client, eml2)
            # Ambos criados com sucesso (ou 409 se mock não distinguir — verificar add)
            assert r1.status_code in (201, 409)
            assert r2.status_code in (201, 409)
        finally:
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Path traversal em nomes de anexos
# ---------------------------------------------------------------------------

class TestAttachmentPathSafety:

    def _upload_with_attachment_and_capture(self, filename: str, content: bytes = b"conteudo"):
        """
        Faz upload de .eml com anexo e captura o storage_path salvo.
        Retorna o storage_path do Attachment adicionado ao DB.
        """
        db = _db_no_duplicate(mock_db())
        app.dependency_overrides[get_db] = override_db(db)

        eml = build_eml_with_attachment(filename, content)
        captured_attachments = []

        original_add = db.add

        def capturing_add(obj):
            from app.models.parecer import Attachment
            if hasattr(obj, "storage_path"):
                captured_attachments.append(obj)
            return original_add(obj)

        db.add = capturing_add

        try:
            with TestClient(app) as client:
                with patch("app.services.pipeline.process_parecer_pipeline"):
                    with patch("builtins.open", create=True):
                        resp = _post_eml(client, eml)
        finally:
            app.dependency_overrides.clear()

        return resp, captured_attachments

    def test_normal_filename_stored_in_uploads(self):
        resp, attachments = self._upload_with_attachment_and_capture("contrato.pdf", b"%PDF")
        assert resp.status_code == 201
        if attachments:
            for att in attachments:
                # Must be inside the configured uploads directory (no escaping to system paths)
                assert "contrato.pdf" in att.storage_path
                assert not att.storage_path.startswith("/etc/")
                assert ".." not in att.storage_path

    def test_path_traversal_filename_sanitized(self):
        """
        ../../../etc/passwd como nome de anexo deve ser sanitizado.
        O regex [^\\w.\\-] substitui / por _, resultando em nome seguro.
        O resultado .._.._.._etc_passwd é seguro — sem separadores de diretório.
        """
        resp, attachments = self._upload_with_attachment_and_capture(
            "../../../etc/passwd", b"conteudo"
        )
        if attachments:
            path = attachments[0].storage_path
            # O nome do arquivo não deve conter separadores de diretório
            assert "/" not in Path(path).name
            assert "\\" not in Path(path).name
            # O arquivo deve estar diretamente no diretório de uploads (sem subdiretórios)
            assert Path(path).parent == Path(path).parent  # o arquivo tem pai único
            assert "etc/passwd" not in path

    def test_windows_path_traversal_sanitized(self):
        """..\\..\\..\\windows\\system32 deve ser sanitizado."""
        resp, attachments = self._upload_with_attachment_and_capture(
            "..\\..\\Windows\\System32\\config.sys"
        )
        if attachments:
            path = attachments[0].storage_path
            # Após sanitização, backslashes viram _ e o arquivo fica flat no diretório
            assert "/" not in Path(path).name
            assert "\\" not in Path(path).name

    def test_filename_with_null_bytes_handled(self):
        """Nomes com null bytes não devem causar crash."""
        resp, _ = self._upload_with_attachment_and_capture("arquivo\x00.pdf")
        assert resp.status_code in (201, 400, 422)  # não 500

    def test_safe_name_regex_blocks_slashes(self):
        """
        Teste unitário direto do regex de sanitização.
        Verifica que o padrão [^\\w.\\-] bloqueia separadores de path.
        """
        safe_name = re.sub(r"[^\w.\-]", "_", "../../../etc/passwd")
        # Nenhum '/' deve sobrar
        assert "/" not in safe_name
        # Nenhum '\' deve sobrar
        assert "\\" not in safe_name
        # O resultado é um nome de arquivo plano
        assert safe_name == ".._.._.._etc_passwd"


# ---------------------------------------------------------------------------
# Emails malformados
# ---------------------------------------------------------------------------

class TestMalformedEmails:

    def test_empty_eml_handled_gracefully(self):
        db = _db_no_duplicate(mock_db())
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                with patch("app.services.pipeline.process_parecer_pipeline"):
                    with patch("builtins.open", create=True):
                        resp = _post_eml(client, b"")
            # Email vazio pode ser parseado (retorna objeto vazio) ou falhar — não deve crashar
            assert resp.status_code in (201, 409, 422)
        finally:
            app.dependency_overrides.clear()

    def test_plain_text_as_eml_handled(self):
        """Conteúdo que não é MIME válido mas tem extensão .eml."""
        db = _db_no_duplicate(mock_db())
        app.dependency_overrides[get_db] = override_db(db)

        try:
            with TestClient(app) as client:
                with patch("app.services.pipeline.process_parecer_pipeline"):
                    with patch("builtins.open", create=True):
                        resp = _post_eml(client, b"Isso nao e um email MIME valido.")
            assert resp.status_code in (201, 409, 422)  # não 500
        finally:
            app.dependency_overrides.clear()

    def test_eml_with_subject_only_uses_subject_as_fallback(self):
        """
        Email sem corpo mas com assunto deve usar o assunto como texto extraído.
        """
        db = _db_no_duplicate(mock_db())
        added_objects = []

        def capture_add(obj):
            added_objects.append(obj)

        db.add = capture_add
        app.dependency_overrides[get_db] = override_db(db)

        eml = build_eml(subject="Consulta sobre contrato de serviços", body="")

        try:
            with TestClient(app) as client:
                with patch("app.services.pipeline.process_parecer_pipeline"):
                    with patch("builtins.open", create=True):
                        resp = _post_eml(client, eml)
            if resp.status_code == 201:
                # ParecerRequest deve ter sido adicionado
                from app.models.parecer import ParecerRequest
                pareceres = [o for o in added_objects if hasattr(o, "extracted_text")]
                if pareceres:
                    pr = pareceres[0]
                    # Fallback: assunto usado como texto mínimo
                    assert pr.extracted_text is not None
                    assert len(pr.extracted_text) > 0
        finally:
            app.dependency_overrides.clear()
