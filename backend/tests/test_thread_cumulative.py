"""
Itens 1/2 do cliente (jul/2026): o parecer de follow-up (irmão) numa thread deve
ler TODOS os documentos e corpos da conversa, não só os da última mensagem.
Testa parecer_engine._thread_cumulative_context.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import parecer_engine


def _att(name: str, text: str) -> SimpleNamespace:
    return SimpleNamespace(filename=name, extracted_text=text)


def _req(thread, atts, body, created) -> SimpleNamespace:
    return SimpleNamespace(
        gmail_thread_id=thread, attachments=atts, extracted_text=body, created_at=created,
    )


def _db_returning(reqs) -> MagicMock:
    db = MagicMock()
    res = MagicMock()
    res.scalars.return_value.all.return_value = reqs
    db.execute = AsyncMock(return_value=res)
    return db


@pytest.mark.asyncio
async def test_request_unico_na_thread_retorna_proprio():
    pr = _req("t1", [_att("a.pdf", "AAA")], "corpo", 1)
    db = _db_returning([pr])
    docs, body = await parecer_engine._thread_cumulative_context(pr, db)
    assert docs == [("a.pdf", "AAA")]
    assert body == "corpo"


@pytest.mark.asyncio
async def test_sem_thread_id_nao_consulta_o_banco():
    pr = _req(None, [_att("a.pdf", "AAA")], "corpo", 1)
    db = MagicMock()
    db.execute = AsyncMock(side_effect=AssertionError("não deve consultar o banco"))
    docs, body = await parecer_engine._thread_cumulative_context(pr, db)
    assert docs == [("a.pdf", "AAA")]
    assert body == "corpo"


@pytest.mark.asyncio
async def test_followup_reune_todos_docs_da_thread_com_dedup():
    # Rodada 1: consulta + edital; Rodada 2: laudo (novo) + edital REENVIADO.
    r1 = _req("t1", [_att("consulta.pdf", "C"), _att("edital.pdf", "E1")], "corpo 1", 1)
    r2 = _req("t1", [_att("laudo.pdf", "L"), _att("edital.pdf", "E2")], "corpo 2", 2)
    db = _db_returning([r1, r2])  # ordenados asc por created_at

    docs, body = await parecer_engine._thread_cumulative_context(r2, db)
    d = dict(docs)

    # Todos os documentos da conversa entram — não só os da última mensagem.
    assert set(d.keys()) == {"consulta.pdf", "edital.pdf", "laudo.pdf"}
    # Documento reenviado: rodada mais recente vence.
    assert d["edital.pdf"] == "E2"
    # Corpo combinado das duas mensagens, rotulado por rodada.
    assert "MENSAGEM 1 DA CONVERSA" in body
    assert "MENSAGEM 2 DA CONVERSA" in body
    assert "corpo 1" in body and "corpo 2" in body


# ─── Guard de conteúdo mínimo (item 3.4) ────────────────────────────────────────


class TestCorpoVazioGuard:
    def test_secoes_vazias_e_vazio(self):
        assert parecer_engine._corpo_vazio(
            {"relatorio": "", "fundamentos": "", "conclusao": ""}
        ) is True

    def test_dict_sem_chaves_e_vazio(self):
        assert parecer_engine._corpo_vazio({}) is True

    def test_whitespace_e_vazio(self):
        assert parecer_engine._corpo_vazio(
            {"relatorio": "   ", "fundamentos": "\n\n", "conclusao": None}
        ) is True

    def test_esqueleto_com_ementa_mas_corpo_vazio_e_vazio(self):
        # O caso PAR-56: títulos/ementa presentes, mas as 3 seções do corpo vazias.
        assert parecer_engine._corpo_vazio(
            {"ementa": "EMENTA. CONTRATO. PRORROGAÇÃO.",
             "relatorio": "", "fundamentos": "", "conclusao": ""}
        ) is True

    def test_conteudo_real_nao_e_vazio(self):
        fund = "Trata-se de consulta sobre prorrogação contratual do serviço contínuo. " * 20
        assert parecer_engine._corpo_vazio(
            {"relatorio": "É o breve relatório.", "fundamentos": fund, "conclusao": "Opina-se favoravelmente."}
        ) is False
