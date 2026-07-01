"""
Testes do gate de réplica no ingest de .eml (routers/ingest.py):
- réplica numa thread já importada SEM anexo-documento → 409
- réplica COM anexo-documento → 201, herdando município/responsável do irmão
"""
from __future__ import annotations

import io
import uuid
from unittest.mock import MagicMock, patch

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


def _post_eml(client, content: bytes, filename: str = "email.eml"):
    return client.post(
        ENDPOINT,
        files={"file": (filename, io.BytesIO(content), "message/rfc822")},
    )


def _db_followup(sibling):
    """DB: sem duplicata (dedup .first() None) mas com irmão na thread (scalar_one_or_none)."""
    db = mock_db()
    dedup = MagicMock()
    dedup.first.return_value = None
    sibling_res = MagicMock()
    sibling_res.scalar_one_or_none.return_value = sibling
    # 1ª execute = dedup por message_id; 2ª = lookup do irmão mais recente da thread
    db.execute.side_effect = [dedup, sibling_res]
    return db


class TestReplicaGate:

    def test_replica_sem_documento_retorna_409(self):
        thread = f"<thread-{uuid.uuid4()}@x.gov.br>"
        sibling = mock_parecer(gmail_thread_id=thread, municipio_id=uuid.uuid4())
        db = _db_followup(sibling)
        app.dependency_overrides[get_db] = override_db(db)

        # Réplica só-texto (In-Reply-To aponta para a thread existente), sem anexo.
        eml = build_eml(in_reply_to=thread, message_id=f"<msg2-{uuid.uuid4()}@x.gov.br>")

        try:
            with TestClient(app) as client:
                resp = _post_eml(client, eml)
            assert resp.status_code == 409
            assert "sem documento" in resp.json()["detail"].lower()
            db.add.assert_not_called()
        finally:
            app.dependency_overrides.clear()

    def test_replica_com_documento_cria_irmao_herdando_municipio(self, tmp_path):
        muni_id = uuid.uuid4()
        assigned_id = uuid.uuid4()
        thread = f"<thread-{uuid.uuid4()}@x.gov.br>"
        sibling = mock_parecer(
            gmail_thread_id=thread, municipio_id=muni_id, assigned_to=assigned_id
        )
        db = _db_followup(sibling)
        app.dependency_overrides[get_db] = override_db(db)

        eml = build_eml_with_attachment(
            "laudo.pdf",
            b"%PDF-1.4 conteudo",
            in_reply_to=thread,
            message_id=f"<msg2-{uuid.uuid4()}@x.gov.br>",
        )

        try:
            with TestClient(app) as client:
                with patch("app.routers.ingest.UPLOADS_DIR", new=tmp_path):
                    with patch(
                        "app.routers.ingest.extract_file",
                        return_value=("texto do laudo", "python_docx", "success"),
                    ):
                        with patch("app.services.pipeline.process_parecer_pipeline"):
                            resp = _post_eml(client, eml)
            assert resp.status_code == 201, resp.text
            body = resp.json()
            assert body["municipio_id"] == str(muni_id)
            assert body["attachments_count"] == 1
        finally:
            app.dependency_overrides.clear()
