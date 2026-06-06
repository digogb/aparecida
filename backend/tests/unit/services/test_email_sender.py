"""
Testes unitários do email_sender — funções puras e validações (sem rede).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import email_sender as es


def _req(**overrides) -> SimpleNamespace:
    base = dict(
        subject="Consulta sobre licitação",
        numero_parecer="PAR-2026-0007",
        classificacao={},
        sender_email="prefeitura@muni.ce.gov.br",
        gmail_message_id="<msg@x>",
        gmail_thread_id="thread-1",
        id="req-1",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


class TestBuildEmailBody:
    def test_inclui_numero_e_assunto(self):
        body = es._build_email_body(_req())
        assert "PAR-2026-0007" in body
        assert "Consulta sobre licitação" in body
        assert "Ione Advogados & Associados" in body

    def test_saudacao_usa_consulente_quando_presente(self):
        body = es._build_email_body(_req(classificacao={"consulente": "Secretário João"}))
        assert "Prezado(a) Secretário João" in body

    def test_saudacao_usa_municipio_sem_consulente(self):
        body = es._build_email_body(_req(classificacao={"municipio": "Araripe"}))
        assert "Município de Araripe" in body

    def test_saudacao_generica_sem_dados(self):
        body = es._build_email_body(_req(classificacao={}))
        assert "Prezado(a) Senhor(a)" in body

    def test_numero_ausente_usa_sn(self):
        body = es._build_email_body(_req(numero_parecer=None))
        assert "nº S/N" in body


class TestBuildGmailServiceGuard:
    def test_sem_credenciais_levanta_valueerror(self, monkeypatch):
        monkeypatch.setattr(es.settings, "GMAIL_REFRESH_TOKEN", "", raising=False)
        monkeypatch.setattr(es.settings, "GMAIL_CREDENTIALS_PATH", "/caminho/inexistente.json", raising=False)
        with pytest.raises(ValueError, match="Gmail nao configurado"):
            es._build_gmail_service()


class TestSendParecerValidations:
    @pytest.mark.asyncio
    async def test_sem_sender_email_levanta_valueerror(self):
        req = _req(sender_email=None)
        db = AsyncMock()
        db.add = MagicMock()
        with pytest.raises(ValueError, match="sender_email"):
            await es.send_parecer(req, b"%PDF-fake", db)
