"""
Testes do parecer_ai_service — foco no P1.5 (extração financeira via Haiku).

A chamada à API é mockada — testamos apenas a lógica de gating, parsing
e construção do payload para o P2.
"""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from app.services import parecer_ai_service


# ---------------------------------------------------------------------------
# Gating do P1.5 — só dispara em subtipos com dimensão financeira
# ---------------------------------------------------------------------------

class TestP15Gating:

    @pytest.mark.asyncio
    async def test_subtipo_aditivo_dispara(self):
        cls = {"subtipo": "aditivo_quantitativo", "vertente": "licitacao_14133"}
        with patch.object(
            parecer_ai_service, "_call_api", return_value='{"aplicavel": true, "valor_inicial_contrato": {"valor": "100.00", "confianca": "alta"}}'
        ) as mock:
            result = await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            mock.assert_called_once()
            assert result is not None
            assert result["valor_inicial_contrato"]["valor"] == "100.00"

    @pytest.mark.asyncio
    async def test_subtipo_dispensa_dispara(self):
        cls = {"subtipo": "dispensa_valor", "vertente": "licitacao_14133"}
        with patch.object(
            parecer_ai_service, "_call_api", return_value='{"aplicavel": true}'
        ) as mock:
            await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_vertente_tributario_dispara(self):
        cls = {"subtipo": "qualquer", "vertente": "tributario_financeiro"}
        with patch.object(
            parecer_ai_service, "_call_api", return_value='{"aplicavel": true}'
        ) as mock:
            await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_subtipo_sem_valor_nao_dispara(self):
        # parecer_administrativo sem dimensão financeira — pula P1.5
        cls = {"subtipo": "nepotismo", "vertente": "administrativo"}
        with patch.object(parecer_ai_service, "_call_api") as mock:
            result = await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            mock.assert_not_called()
            assert result is None

    @pytest.mark.asyncio
    async def test_sem_anexos_nao_dispara(self):
        cls = {"subtipo": "aditivo", "vertente": "licitacao_14133"}
        with patch.object(parecer_ai_service, "_call_api") as mock:
            result = await parecer_ai_service.extract_valores_financeiros(cls, [])
            mock.assert_not_called()
            assert result is None


# ---------------------------------------------------------------------------
# Robustez de parsing — JSON inválido / API falha viram None
# ---------------------------------------------------------------------------

class TestP15Robustez:

    @pytest.mark.asyncio
    async def test_api_falha_retorna_none(self):
        cls = {"subtipo": "aditivo", "vertente": "licitacao_14133"}
        with patch.object(parecer_ai_service, "_call_api", side_effect=RuntimeError("boom")):
            result = await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            assert result is None

    @pytest.mark.asyncio
    async def test_json_invalido_retorna_none(self):
        cls = {"subtipo": "aditivo", "vertente": "licitacao_14133"}
        with patch.object(parecer_ai_service, "_call_api", return_value="isso não é JSON"):
            result = await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            assert result is None

    @pytest.mark.asyncio
    async def test_strip_markdown_fences(self):
        # P1.5 pode envelopar JSON em ```json ... ``` — deve aceitar
        cls = {"subtipo": "aditivo", "vertente": "licitacao_14133"}
        envelopado = '```json\n{"aplicavel": true, "valor_inicial_contrato": {"valor": "50.00", "confianca": "alta"}}\n```'
        with patch.object(parecer_ai_service, "_call_api", return_value=envelopado):
            result = await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            assert result is not None
            assert result["valor_inicial_contrato"]["valor"] == "50.00"

    @pytest.mark.asyncio
    async def test_aplicavel_false_retorna_none(self):
        # Mesmo disparado por subtipo, se o Haiku decidir que não aplica
        # (ex.: anexo não tem valores), retornamos None para não poluir o P2.
        cls = {"subtipo": "aditivo", "vertente": "licitacao_14133"}
        with patch.object(
            parecer_ai_service,
            "_call_api",
            return_value='{"aplicavel": false, "motivo": "anexos não contêm valores"}',
        ):
            result = await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            assert result is None


# ---------------------------------------------------------------------------
# Detecção de ambiguidade — caso real (CONSULTA 3)
# ---------------------------------------------------------------------------

class TestP15Ambiguidade:

    @pytest.mark.asyncio
    async def test_dois_candidatos_marca_ambiguo_com_canonico(self):
        """Cenário real (CONSULTA 3 — CRECHE PRÓ-INFÂNCIA): planilha com
        'CONTRATADA: R$ 234.791,74' no cabeçalho e 'VALOR TOTAL GERAL
        (BDI: 27,35%): R$ 939.166,94' no rodapé. O canônico é o do rodapé
        (rotulado explicitamente como total com BDI); o valor do cabeçalho
        é parcela (1/4 do canônico) ou referência. O P1.5 marca ambiguidade,
        sinaliza R$ 939.166,94 como `provavel_canonico=true`, e o
        percentual canônico resulta em 22,04% — dentro do limite legal."""
        cls = {"subtipo": "aditivo", "vertente": "licitacao_14133"}
        payload = {
            "aplicavel": True,
            "valor_inicial_contrato": {"valor": "939166.94", "confianca": "ambiguo"},
            "valores_candidatos_inicial": [
                {"valor": "939166.94", "rotulo_no_documento": "VALOR TOTAL GERAL (BDI: 27,35%)", "provavel_canonico": True},
                {"valor": "234791.74", "rotulo_no_documento": "CONTRATADA: ... R$ 234.791,74", "provavel_canonico": False},
            ],
            "valor_acrescimos": {"valor": "206997.62", "confianca": "alta"},
            "percentual_acrescimo_calculado_canonico": "22.04%",
            "percentual_declarado_no_documento": "22.04%",
            "discrepancia_percentual": False,
            "extrapola_limite": False,
            "nota_ambiguidade": "Canônico é o do rodapé totalizador; 234.791,74 é 1/4 do canônico, provavelmente parcela.",
        }
        with patch.object(parecer_ai_service, "_call_api", return_value=json.dumps(payload)):
            result = await parecer_ai_service.extract_valores_financeiros(cls, ["doc"])
            assert result is not None
            assert result["valor_inicial_contrato"]["valor"] == "939166.94"
            assert result["valor_inicial_contrato"]["confianca"] == "ambiguo"
            assert len(result["valores_candidatos_inicial"]) == 2
            # Provável canônico é o do rodapé com BDI
            canonico = next(c for c in result["valores_candidatos_inicial"] if c.get("provavel_canonico"))
            assert canonico["valor"] == "939166.94"
            assert result["extrapola_limite"] is False
