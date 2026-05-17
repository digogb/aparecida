"""Testes do auditor mecânico (Camada 4 — gate IRR-1 + IRR-2)."""
from __future__ import annotations

import pytest

from app.services.auditor_mecanico import (
    CHARS_PER_LINE,
    AuditorResult,
    affected_sections,
    audit_sections,
    estimar_linhas,
    format_revision_instructions,
)


# ─── estimar_linhas ─────────────────────────────────────────────────────────────


class TestEstimarLinhas:
    def test_empty_returns_zero(self):
        assert estimar_linhas("") == 0
        assert estimar_linhas("   ") == 0

    def test_short_paragraph_is_one_line(self):
        assert estimar_linhas("Texto curto.") == 1

    def test_paragraph_at_chars_per_line_is_one_line(self):
        texto = "x" * CHARS_PER_LINE
        assert estimar_linhas(texto) == 1

    def test_paragraph_just_over_chars_per_line_is_two_lines(self):
        texto = "x" * (CHARS_PER_LINE + 1)
        assert estimar_linhas(texto) == 2

    def test_paragraph_with_newlines(self):
        # 2 linhas físicas, cada uma cabendo em 1 linha renderizada
        texto = "Linha um.\nLinha dois."
        assert estimar_linhas(texto) == 2

    def test_long_paragraph(self):
        # 8 linhas de 78 chars = ≥ 8 linhas estimadas
        texto = "x" * (CHARS_PER_LINE * 8 + 1)
        assert estimar_linhas(texto) >= 9


# ─── IRR-1 (ementa em CAPS) ────────────────────────────────────────────────────


_FUND_OK = "Análise jurídica em parágrafos curtos. Cada um carrega uma ideia."
_REL_OK = "Trata-se de consulta da Prefeitura X.\n\nÉ o breve relatório. Passa-se à fundamentação."
_CONC_OK = "Diante do exposto, o parecer é FAVORÁVEL.\n\na) Recomendação 1.\n\nÉ o parecer, submetido à superior consideração."


class TestIRR1Ementa:
    def test_ementa_full_caps_passes(self):
        sections = {
            "ementa": "EMENTA: DIREITO ADMINISTRATIVO ― DISPENSA ― art. 75 DA Lei nº 14.133/2021 ― PARECER FAVORÁVEL.",
            "relatorio": _REL_OK,
            "fundamentos": _FUND_OK,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert result.passed is True
        assert result.ementa_ok is True

    def test_ementa_with_ordinal_indicators_passes(self):
        # º, °, ª são exceções permitidas
        sections = {
            "ementa": "EMENTA: DIREITO TRIBUTÁRIO ― CF ART. 150, § 6º ― LRF ART. 14 ― PARECER FAVORÁVEL COM RESSALVAS.",
            "relatorio": _REL_OK,
            "fundamentos": _FUND_OK,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert result.ementa_ok is True

    def test_ementa_with_alinea_quotes_passes(self):
        # Letras de alíneas entre aspas são exceção permitida
        sections = {
            "ementa": "EMENTA: ART. 124, INCISO I, ALÍNEA 'b' ― PARECER FAVORÁVEL.",
            "relatorio": _REL_OK,
            "fundamentos": _FUND_OK,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert result.ementa_ok is True

    def test_ementa_with_lowercase_fails(self):
        sections = {
            "ementa": "EMENTA: Direito Administrativo ― Dispensa ― Parecer favorável.",
            "relatorio": _REL_OK,
            "fundamentos": _FUND_OK,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert result.passed is False
        assert result.ementa_ok is False
        assert any("IRR-1" in v for v in result.violacoes)

    def test_empty_ementa_fails(self):
        sections = {
            "ementa": "",
            "relatorio": _REL_OK,
            "fundamentos": _FUND_OK,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert result.ementa_ok is None
        assert result.passed is False


# ─── IRR-2 (parágrafos ≤ 7 linhas) ────────────────────────────────────────────


_EMENTA_OK = "EMENTA: DIREITO ADMINISTRATIVO ― PARECER FAVORÁVEL."


class TestIRR2Paragrafos:
    def test_short_paragraphs_pass(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": _FUND_OK,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert result.passed is True
        assert result.paragrafos_longos == []

    def test_paragraph_8_lines_fails(self):
        # 8 linhas estimadas a 78 chars/linha = 624 chars contínuos
        paragrafo_longo = "Texto longo. " * 60  # ≈ 780 chars, ≈10 linhas
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": paragrafo_longo,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert result.passed is False
        assert len(result.paragrafos_longos) == 1
        p = result.paragrafos_longos[0]
        assert p.secao == "fundamentos"
        assert p.n_linhas >= 8

    def test_long_paragraph_in_relatorio_also_fails(self):
        paragrafo_longo = "x" * (CHARS_PER_LINE * 8 + 50)
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": paragrafo_longo,
            "fundamentos": _FUND_OK,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert result.passed is False
        assert result.paragrafos_longos[0].secao == "relatorio"

    def test_multiple_long_paragraphs_all_reported(self):
        long_para = "x" * (CHARS_PER_LINE * 8 + 1)
        fundamentos = "\n\n".join([long_para, "Parágrafo curto.", long_para])
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": fundamentos,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert len(result.paragrafos_longos) == 2

    def test_short_lines_below_min_chars_ignored(self):
        # Linhas < 100 chars são ignoradas mesmo se quebrarem em múltiplas linhas
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": "Curto.\n" * 20,  # 7 * 20 = 140 chars total, mas cada parágrafo é < 100
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        # Deve passar: nenhum parágrafo individual ultrapassa o limite
        assert result.passed is True

    def test_title_lines_are_skipped(self):
        # Linhas que começam com "I —", "II —", "III —" etc. são ignoradas
        long_title_line = "II — FUNDAMENTOS " + "X" * (CHARS_PER_LINE * 8)
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": long_title_line,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        # Pula a linha de título — passa
        assert result.passed is True


# ─── Logging e helpers ─────────────────────────────────────────────────────────


class TestResultHelpers:
    def test_as_log_dict_is_jsonable(self):
        import json

        sections = {
            "ementa": "EMENTA: minúscula errada.",
            "relatorio": _REL_OK,
            "fundamentos": "x" * (CHARS_PER_LINE * 8 + 1),
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        log = result.as_log_dict()
        # Deve ser serializável
        s = json.dumps(log)
        assert "passed" in log
        assert log["passed"] is False
        assert "violacoes" in log
        assert "paragrafos_longos" in log

    def test_affected_sections_lists_ementa_when_irr1_fails(self):
        sections = {
            "ementa": "EMENTA: minúscula errada.",
            "relatorio": _REL_OK,
            "fundamentos": _FUND_OK,
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert "ementa" in affected_sections(result)

    def test_affected_sections_lists_fundamentos_when_irr2_fails(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": "x" * (CHARS_PER_LINE * 8 + 1),
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        assert "fundamentos" in affected_sections(result)

    def test_format_revision_instructions_mentions_violations(self):
        sections = {
            "ementa": "EMENTA: erro.",
            "relatorio": _REL_OK,
            "fundamentos": "y" * (CHARS_PER_LINE * 9),
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)
        instructions = format_revision_instructions(result)
        assert "IRR-1" in instructions
        assert "IRR-2" in instructions
        assert "TRECHOS MARCADOS PARA CORREÇÃO" in instructions
