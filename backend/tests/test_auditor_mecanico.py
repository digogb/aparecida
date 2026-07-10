"""Testes do auditor mecânico (Camada 4 — gate IRR-1 + IRR-2 + IRR-3)."""
from __future__ import annotations

import pytest

from app.services.auditor_mecanico import (
    CHARS_PER_LINE,
    AuditorResult,
    MarcadorResidual,
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
_CONC_OK = "Diante do exposto, o parecer é FAVORÁVEL.\n\na) Recomendação 1.\n\nÉ o parecer."


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


# ─── IRR-3 — marcadores residuais sobre norma da parte adversa ─────────────────


class TestIRR3MarcadoresResiduais:
    """Em modo quase-processual, [VERIFICAR] e [REVISAR — ... parte adversa ...]
    em texto final reprovam o gate. Em modo consultivo, IRR-3 não se aplica."""

    def test_consultivo_default_ignores_markers(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": "Texto com [VERIFICAR — algo] residual.",
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections)  # modo=None → consultivo default
        assert result.marcadores_residuais == []
        assert result.passed is True

    def test_consultivo_explicit_ignores_markers(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": "Texto com [VERIFICAR — algo] e [REVISAR — NORMA INVOCADA PELA PARTE ADVERSA].",
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections, modo="consultivo_puro")
        assert result.marcadores_residuais == []
        assert result.passed is True

    def test_quase_processual_flags_verificar_marker(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": "A Lei [VERIFICAR — NORMA 9999/2000 INVOCADA PELO RECORRENTE] não procede.",
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections, modo="quase_processual")
        assert result.passed is False
        assert len(result.marcadores_residuais) == 1
        assert result.marcadores_residuais[0].tipo == "verificar"
        assert result.marcadores_residuais[0].secao == "fundamentos"

    def test_quase_processual_flags_revisar_parte_adversa(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": (
                "O recorrente invoca a Lei nº 9.999/2000 "
                "[REVISAR — NORMA 9.999/2000 INVOCADA PELA PARTE ADVERSA — CONFIRMAR VIGÊNCIA]."
            ),
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections, modo="quase_processual")
        assert result.passed is False
        assert len(result.marcadores_residuais) == 1
        assert result.marcadores_residuais[0].tipo == "revisar_adversa"

    def test_quase_processual_accepts_neutral_revisar_marker(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": (
                "Aplica-se o entendimento "
                "[REVISAR — ACÓRDÃO TCU Nº 1234/2025 NÃO CONFIRMADO. VERIFICAR NÚMERO E RELATOR.]."
            ),
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections, modo="quase_processual")
        # Marcador [REVISAR — ...] sobre acórdão a confirmar é admissível em texto final.
        assert result.marcadores_residuais == []
        assert result.passed is True

    def test_affected_sections_includes_marker_section(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": _FUND_OK,
            "conclusao": (
                "Diante do exposto, [VERIFICAR — ALGO PENDENTE] o parecer é PERTINENTE."
            ),
        }
        result = audit_sections(sections, modo="quase_processual")
        assert "conclusao" in affected_sections(result)

    def test_format_revision_instructions_mentions_irr3(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": "Texto com [VERIFICAR — NORMA 9999/2000 INVOCADA PELA PARTE ADVERSA].",
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections, modo="quase_processual")
        instructions = format_revision_instructions(result)
        assert "IRR-3" in instructions
        assert "MARCADORES A RESOLVER" in instructions

    def test_log_dict_serializes_marcadores(self):
        sections = {
            "ementa": _EMENTA_OK,
            "relatorio": _REL_OK,
            "fundamentos": "[VERIFICAR — algo da parte adversa]",
            "conclusao": _CONC_OK,
        }
        result = audit_sections(sections, modo="quase_processual")
        log = result.as_log_dict()
        assert "marcadores_residuais" in log
        assert len(log["marcadores_residuais"]) == 1
        assert log["marcadores_residuais"][0]["tipo"] == "verificar"
        assert log["marcadores_residuais"][0]["secao"] == "fundamentos"


# ─── Citação literal de artigo de lei (item 3.3 — Opção B) ──────────────────────


class TestCitacaoLiteralLei:
    EMENTA_OK = "CONTRATAÇÃO DIRETA. INEXIGIBILIDADE. ART. 74. PARECER FAVORÁVEL."

    def _sections(self, fundamentos: str) -> dict:
        return {
            "ementa": self.EMENTA_OK,
            "relatorio": "Trata-se de consulta objetiva do Município.",
            "fundamentos": fundamentos,
            "conclusao": "Opina-se favoravelmente.",
        }

    def test_transcricao_em_recuo_reprova(self):
        f = (
            "O dispositivo é expresso.\n\n"
            "> Art. 107. Os contratos de serviços e fornecimentos contínuos poderão ser "
            "prorrogados sucessivamente, respeitada a vigência máxima decenal.\n\n"
            "Cabe, portanto, a prorrogação."
        )
        result = audit_sections(self._sections(f))
        assert not result.passed
        assert len(result.citacoes_literais) == 1
        assert result.citacoes_literais[0].secao == "fundamentos"

    def test_transcricao_entre_aspas_reprova(self):
        f = (
            'A norma dispõe: "Art. 65. As alterações contratuais serão formalizadas por termo '
            'aditivo, respeitados os limites legais e a manutenção do equilíbrio econômico do ajuste."'
        )
        result = audit_sections(self._sections(f))
        assert not result.passed
        assert len(result.citacoes_literais) == 1

    def test_referencia_inline_curta_passa(self):
        f = "Nos termos do art. 107 da Lei 14.133/2021, admite-se a prorrogação sucessiva do contrato."
        result = audit_sections(self._sections(f))
        assert result.citacoes_literais == []
        assert result.passed

    def test_parafrase_passa(self):
        f = (
            "O art. 107 estabelece, em síntese, que os contratos contínuos podem ser prorrogados "
            "sucessivamente, respeitada a vigência decenal e a vantajosidade."
        )
        result = audit_sections(self._sections(f))
        assert result.citacoes_literais == []
        assert result.passed

    def test_jurisprudencia_em_recuo_nao_reprova(self):
        f = (
            "O TCU já decidiu a matéria.\n\n"
            "> A prorrogação de contratos de serviços contínuos exige demonstração da "
            "vantajosidade, sob pena de nulidade do ajuste.\n\n"
            "O entendimento aplica-se ao caso."
        )
        result = audit_sections(self._sections(f))
        assert result.citacoes_literais == []
        assert result.passed

    def test_reportado_em_affected_sections_e_instrucoes(self):
        f = (
            "> Art. 57. O prazo de vigência será de até doze meses, prorrogável na forma da lei, "
            "conforme o interesse público devidamente justificado nos autos do processo."
        )
        result = audit_sections(self._sections(f))
        assert "fundamentos" in affected_sections(result)
        instr = format_revision_instructions(result)
        assert "CITAÇÃO LITERAL DE LEI" in instr
