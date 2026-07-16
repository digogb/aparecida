"""
Testes unitários dos helpers puros do gmail_poller + guarda de configuração.
Não fazem chamadas de rede.
"""
from __future__ import annotations

import base64
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.parecer import ParecerRequest
from app.services import gmail_poller as gp


def _b64(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii").rstrip("=")


def _result(first=None, scalar=None):
    """Mock de resultado de db.execute com .first()/.scalar_one_or_none()."""
    res = MagicMock()
    res.first.return_value = first
    res.scalar_one_or_none.return_value = scalar
    return res


def _mock_db(execute_results):
    db = AsyncMock()
    db.execute.side_effect = list(execute_results)
    db.add = MagicMock()
    return db


def _mock_service(payload, attachment_data="conteudo do anexo"):
    svc = MagicMock()
    msgs = svc.users.return_value.messages.return_value
    msgs.get.return_value.execute.return_value = {"payload": payload}
    msgs.attachments.return_value.get.return_value.execute.return_value = {
        "data": _b64(attachment_data)
    }
    return svc


def _payload(parts):
    return {
        "mimeType": "multipart/mixed",
        "headers": [
            {"name": "Subject", "value": "Consulta jurídica"},
            {"name": "From", "value": "prefeitura@x.gov.br"},
        ],
        "parts": parts,
    }


_BODY_PART = {"mimeType": "text/plain", "body": {"data": _b64("corpo da consulta")}}
_PDF_PART = {
    "filename": "laudo.pdf",
    "mimeType": "application/pdf",
    "body": {"attachmentId": "att1", "size": 100},
}
_IMG_PART = {
    "filename": "assinatura.png",
    "mimeType": "image/png",
    "body": {"attachmentId": "img1", "size": 50},
}


class TestDecodeB64:
    def test_roundtrip(self):
        assert gp._decode_b64(_b64("olá mundo")).decode("utf-8") == "olá mundo"

    def test_tolera_padding_ausente(self):
        # urlsafe sem '=' deve decodificar (o helper acrescenta '==')
        assert gp._decode_b64(_b64("abc")).decode("utf-8") == "abc"


class TestStripHtml:
    def test_remove_tags_preserva_texto(self):
        out = gp._strip_html("<p>Olá</p><p>mundo</p>")
        assert "Olá" in out and "mundo" in out
        assert "<p>" not in out


class TestExtractSenderEmail:
    def test_com_display_name(self):
        assert gp._extract_sender_email("Fulano <fulano@x.gov.br>") == "fulano@x.gov.br"

    def test_sem_display_name(self):
        assert gp._extract_sender_email("fulano@x.gov.br") == "fulano@x.gov.br"

    def test_normaliza_case_e_espacos(self):
        assert gp._extract_sender_email("  Fulano@X.GOV.BR  ") == "fulano@x.gov.br"


class TestWalkPayload:
    def test_text_plain_simples(self):
        payload = {"mimeType": "text/plain", "body": {"data": _b64("corpo do email")}}
        assert gp._walk_payload(payload).strip() == "corpo do email"

    def test_text_html_sem_partes_e_convertido(self):
        payload = {"mimeType": "text/html", "body": {"data": _b64("<b>negrito</b>")}}
        assert "negrito" in gp._walk_payload(payload)

    def test_multipart_prefere_plain(self):
        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {"mimeType": "text/plain", "body": {"data": _b64("texto puro")}},
                {"mimeType": "text/html", "body": {"data": _b64("<p>html</p>")}},
            ],
        }
        assert gp._walk_payload(payload).strip() == "texto puro"


class TestIsConfigured:
    def test_sem_credenciais_false(self, monkeypatch):
        monkeypatch.setattr(gp.settings, "GMAIL_REFRESH_TOKEN", "", raising=False)
        monkeypatch.setattr(gp.settings, "GMAIL_CREDENTIALS_PATH", "/caminho/inexistente.json", raising=False)
        assert gp._is_configured() is False

    def test_com_refresh_token_true(self, monkeypatch):
        monkeypatch.setattr(gp.settings, "GMAIL_REFRESH_TOKEN", "rt-123", raising=False)
        assert gp._is_configured() is True


class TestPollInboxGuard:
    @pytest.mark.asyncio
    async def test_nao_configurado_retorna_zero(self, monkeypatch):
        monkeypatch.setattr(gp, "_is_configured", lambda: False)
        assert await gp.poll_inbox() == 0


class TestDedupHelpers:
    @pytest.mark.asyncio
    async def test_already_imported_por_message_id(self):
        db = _mock_db([_result(first=(uuid.uuid4(),))])
        assert await gp._already_imported("msg-1", db) is True

    @pytest.mark.asyncio
    async def test_already_imported_ausente(self):
        db = _mock_db([_result(first=None)])
        assert await gp._already_imported("msg-1", db) is False

    @pytest.mark.asyncio
    async def test_thread_already_imported(self):
        db = _mock_db([_result(first=(uuid.uuid4(),))])
        assert await gp._thread_already_imported("thread-1", db) is True

    @pytest.mark.asyncio
    async def test_thread_nao_importada(self):
        db = _mock_db([_result(first=None)])
        assert await gp._thread_already_imported("thread-1", db) is False


@pytest.fixture()
def _patch_ingest_side_effects(monkeypatch, tmp_path):
    """Isola _ingest_message de disco, extractor, notificação e pipeline."""
    monkeypatch.setattr(gp, "_UPLOADS_DIR", tmp_path)
    monkeypatch.setattr(gp, "extract_file", lambda fn, b: ("texto extraído", "python_docx", "success"))
    import app.services.notification as notif
    import app.services.pipeline as pipe
    monkeypatch.setattr(notif, "notify_parecer_event", AsyncMock())
    monkeypatch.setattr(pipe, "process_parecer_pipeline", AsyncMock())


class TestIngestMessageGate:
    @pytest.mark.asyncio
    async def test_primeira_msg_cria_sem_anexo(self, _patch_ingest_side_effects):
        # thread ainda não importada → cria request mesmo sem anexo (corpo é a consulta)
        db = _mock_db([_result(first=None)])
        svc = _mock_service(_payload([_BODY_PART]))

        created = await gp._ingest_message(svc, "msg-1", "thread-1", db)

        assert created is True
        added = [c.args[0] for c in db.add.call_args_list if isinstance(c.args[0], ParecerRequest)]
        assert len(added) == 1
        assert added[0].gmail_message_id == "msg-1"
        assert added[0].gmail_thread_id == "thread-1"

    @pytest.mark.asyncio
    async def test_replica_sem_documento_descartada(self, _patch_ingest_side_effects):
        # thread já importada + só imagem (assinatura) → descarta, sem criar registro
        db = _mock_db([_result(first=(uuid.uuid4(),))])
        svc = _mock_service(_payload([_BODY_PART, _IMG_PART]))

        created = await gp._ingest_message(svc, "msg-2", "thread-1", db)

        assert created is False
        added = [c.args[0] for c in db.add.call_args_list if isinstance(c.args[0], ParecerRequest)]
        assert added == []
        db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_replica_com_pdf_vira_irmao_herdando(self, _patch_ingest_side_effects):
        muni_id = uuid.uuid4()
        assigned_id = uuid.uuid4()
        sibling = MagicMock()
        sibling.municipio_id = muni_id
        sibling.assigned_to = assigned_id
        # execute 1: _thread_already_imported → truthy; execute 2: _latest_sibling → sibling
        db = _mock_db([_result(first=(uuid.uuid4(),)), _result(scalar=sibling)])
        svc = _mock_service(_payload([_BODY_PART, _PDF_PART]))

        created = await gp._ingest_message(svc, "msg-2", "thread-1", db)

        assert created is True
        added = [c.args[0] for c in db.add.call_args_list if isinstance(c.args[0], ParecerRequest)]
        assert len(added) == 1
        assert added[0].municipio_id == muni_id
        assert added[0].assigned_to == assigned_id
        assert added[0].gmail_thread_id == "thread-1"
