"""
Testes unitários dos helpers puros do gmail_poller + guarda de configuração.
Não fazem chamadas de rede.
"""
from __future__ import annotations

import base64

import pytest

from app.services import gmail_poller as gp


def _b64(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii").rstrip("=")


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


class TestExtractDomain:
    def test_extrai_dominio(self):
        assert gp._extract_domain("fulano@prefeitura.ce.gov.br") == "prefeitura.ce.gov.br"

    def test_lower_case(self):
        assert gp._extract_domain("X@MUNI.GOV.BR") == "muni.gov.br"

    def test_sem_arroba_retorna_vazio(self):
        assert gp._extract_domain("sem-email") == ""


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
