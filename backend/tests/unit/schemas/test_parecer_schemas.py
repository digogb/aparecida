"""
Testes unitários para schemas de parecer — serialização e validação Pydantic.
"""
from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.parecer import ParecerRequestCreate, ParecerRequestUpdate


class TestParecerRequestCreate:
    def test_todos_campos_opcionais(self):
        schema = ParecerRequestCreate()
        assert schema.municipio_id is None
        assert schema.gmail_thread_id is None
        assert schema.subject is None

    def test_aceita_dados_validos(self):
        schema = ParecerRequestCreate(
            subject="Consulta sobre licitação",
            sender_email="prefeitura@municipio.sp.gov.br",
            gmail_thread_id="thread_abc123",
            gmail_message_id="msg_xyz456",
        )
        assert schema.subject == "Consulta sobre licitação"
        assert schema.sender_email == "prefeitura@municipio.sp.gov.br"

    def test_municipio_id_uuid_valido(self):
        uid = uuid.uuid4()
        schema = ParecerRequestCreate(municipio_id=uid)
        assert schema.municipio_id == uid

    def test_municipio_id_string_uuid(self):
        uid = uuid.uuid4()
        schema = ParecerRequestCreate(municipio_id=str(uid))
        assert schema.municipio_id == uid

    def test_raw_payload_aceita_dict(self):
        payload = {"key": "value", "nested": {"a": 1}}
        schema = ParecerRequestCreate(raw_payload=payload)
        assert schema.raw_payload == payload


class TestParecerRequestUpdate:
    def test_status_invalido_levanta_erro(self):
        with pytest.raises(ValidationError):
            ParecerRequestUpdate(status="status_invalido")

    def test_tema_invalido_levanta_erro(self):
        with pytest.raises(ValidationError):
            ParecerRequestUpdate(tema="tema_inexistente")

    def test_update_parcial_status(self):
        schema = ParecerRequestUpdate(status="aprovado")
        assert schema.status.value == "aprovado"
        assert schema.tema is None

    def test_update_parcial_tema(self):
        schema = ParecerRequestUpdate(tema="licitacao")
        assert schema.tema.value == "licitacao"

    def test_todos_nenhum(self):
        schema = ParecerRequestUpdate()
        assert schema.status is None
        assert schema.tema is None
        assert schema.modelo is None
