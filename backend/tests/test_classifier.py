from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services.parecer_engine import _sections_to_tiptap
from app.services.prompt_service import (
    PROMPTS_DIR,
    VERTENTE_ADMINISTRATIVO,
    VERTENTE_LICITACAO,
    VERTENTE_TERCEIRO_SETOR,
    VERTENTE_TRIBUTARIO,
    build_p2_prompt,
    load_prompt,
    resolve_vertente,
)


P1_PROMPT = load_prompt("p1_classification")


class TestP1ClassificationPrompt:
    """Valida o prompt P1 v5.0 — roteador de vertente, subtipo e modo."""

    def test_prompt_lists_all_vertentes(self):
        for v in [
            VERTENTE_LICITACAO,
            VERTENTE_ADMINISTRATIVO,
            VERTENTE_TRIBUTARIO,
            VERTENTE_TERCEIRO_SETOR,
        ]:
            assert v in P1_PROMPT

    def test_prompt_lists_lei_14133_subtipos(self):
        for subtipo in [
            "art_53",
            "dispensa",
            "inexigibilidade",
            "credenciamento",
            "adesao_ata",
            "aditivo",
            "sancao",
            "impugnacao_recurso",
        ]:
            assert subtipo in P1_PROMPT, f"subtipo licitacao ausente: {subtipo}"

    def test_prompt_lists_municipal_geral_subtipos(self):
        # Amostra representativa de cada vertente
        for subtipo in [
            "servidores",
            "atos_administrativos",
            "urbanismo",
            "iptu",
            "iss",
            "lrf_limites_fiscais",
            "mrosc",
            "cebas",
            "prestacao_contas",
        ]:
            assert subtipo in P1_PROMPT, f"subtipo municipal-geral ausente: {subtipo}"

    def test_prompt_mentions_modo(self):
        for modo in ["consultivo_puro", "quase_processual"]:
            assert modo in P1_PROMPT

    def test_prompt_mentions_lei_14133(self):
        assert "14.133" in P1_PROMPT

    def test_prompt_requests_json(self):
        assert "JSON" in P1_PROMPT or "json" in P1_PROMPT

    def test_prompt_has_required_v5_fields(self):
        for field in [
            "is_consulta_juridica",
            "vertente",
            "subtipo",
            "modo",
            "municipio",
            "orgao_consulente",
            "lacuna_normativa_local",
            "documentos_faltantes",
            "confianca_classificacao",
        ]:
            assert field in P1_PROMPT, f"campo obrigatório ausente: {field}"

    def test_prompt_no_legacy_area_principal_fields(self):
        # O schema v5.0 substituiu area_principal por vertente. O prompt não deve mais
        # instruir o modelo a devolver area_principal/areas_conexas.
        for legacy in ["area_principal", "areas_conexas"]:
            # ok se aparecer apenas dentro do nome do código (não na documentação),
            # mas como o prompt é estritamente schema-first, a string não deve estar lá.
            assert legacy not in P1_PROMPT, f"campo legacy ainda no prompt: {legacy}"


class TestResolveVertente:
    """Valida o roteador prompt_service.resolve_vertente."""

    def test_explicit_vertente_v5_takes_priority(self):
        # Schema v5.0 — campo `vertente` explícito
        assert resolve_vertente({"vertente": "licitacao_14133"}) == VERTENTE_LICITACAO
        assert resolve_vertente({"vertente": "administrativo"}) == VERTENTE_ADMINISTRATIVO
        assert resolve_vertente({"vertente": "tributario_financeiro"}) == VERTENTE_TRIBUTARIO
        assert resolve_vertente({"vertente": "terceiro_setor"}) == VERTENTE_TERCEIRO_SETOR

    def test_legacy_area_principal_fallback(self):
        # Schema v4.1 — campo `area_principal` (compatibilidade com pareceres antigos)
        assert resolve_vertente({"area_principal": "licitacoes_contratos"}) == VERTENTE_LICITACAO
        assert resolve_vertente({"area_principal": "agentes_publicos"}) == VERTENTE_ADMINISTRATIVO
        assert resolve_vertente({"area_principal": "tributos_municipais"}) == VERTENTE_TRIBUTARIO
        assert resolve_vertente({"area_principal": "terceiro_setor"}) == VERTENTE_TERCEIRO_SETOR

    def test_explicit_vertente_overrides_legacy(self):
        cls = {"vertente": "licitacao_14133", "area_principal": "agentes_publicos"}
        assert resolve_vertente(cls) == VERTENTE_LICITACAO

    def test_fallback_to_administrativo(self):
        assert resolve_vertente({}) == VERTENTE_ADMINISTRATIVO
        assert resolve_vertente(None) == VERTENTE_ADMINISTRATIVO
        assert resolve_vertente({"vertente": "nonexistent"}) == VERTENTE_ADMINISTRATIVO
        assert resolve_vertente({"area_principal": "nonexistent"}) == VERTENTE_ADMINISTRATIVO


class TestBuildP2Prompt:
    """Valida que o P2 carrega o prompt correto + fewshot correto por vertente."""

    def test_licitacao_loads_lei_14133_prompt(self):
        prompt = build_p2_prompt(VERTENTE_LICITACAO, include_fewshot=False)
        assert "parecer-lei-14133" in prompt.lower() or "Lei nº 14.133" in prompt
        assert "art. 53" in prompt
        assert "IRR-1" in prompt

    def test_administrativo_loads_municipal_geral_prompt(self):
        prompt = build_p2_prompt(VERTENTE_ADMINISTRATIVO, include_fewshot=False)
        assert "parecer-municipal-geral" in prompt.lower() or "vertente" in prompt.lower()
        assert "LACUNA_NORMATIVA" in prompt
        assert "IRR-1" in prompt

    def test_tributario_and_terceiro_setor_share_municipal_geral(self):
        # As 3 vertentes não-licitatórias compartilham o prompt mestre
        p_admin = build_p2_prompt(VERTENTE_ADMINISTRATIVO, include_fewshot=False)
        p_trib = build_p2_prompt(VERTENTE_TRIBUTARIO, include_fewshot=False)
        p_ts = build_p2_prompt(VERTENTE_TERCEIRO_SETOR, include_fewshot=False)
        assert p_admin == p_trib == p_ts

    def test_fewshot_attached_when_requested(self):
        bare = build_p2_prompt(VERTENTE_LICITACAO, include_fewshot=False)
        full = build_p2_prompt(VERTENTE_LICITACAO, include_fewshot=True)
        assert len(full) > len(bare)
        assert "EXEMPLOS DE REFERÊNCIA" in full


class TestSectionsToTiptap:
    """_sections_to_tiptap usa chaves minúsculas e títulos formatados:
      ementa, relatorio, fundamentos, conclusao
    Títulos gerados: "EMENTA", "I — RELATÓRIO", "II — FUNDAMENTOS", "III — CONCLUSÃO"
    """

    def test_generates_valid_tiptap_doc(self):
        sections = {
            "ementa": "Resumo.",
            "relatorio": "Fatos.",
            "fundamentos": "Analise.",
            "conclusao": "Resposta.",
        }
        doc = _sections_to_tiptap(sections)
        assert doc["type"] == "doc"
        assert len(doc["content"]) == 8  # 4 headings + 4 paragraphs

        headings = [n for n in doc["content"] if n["type"] == "heading"]
        assert len(headings) == 4
        assert headings[0]["content"][0]["text"] == "EMENTA"

    def test_section_titles_use_current_format(self):
        sections = {
            "ementa": "E.",
            "relatorio": "R.",
            "fundamentos": "F.",
            "conclusao": "C.",
        }
        doc = _sections_to_tiptap(sections)
        headings = [n for n in doc["content"] if n["type"] == "heading"]
        titles = [h["content"][0]["text"] for h in headings]
        assert titles[0] == "EMENTA"
        assert "RELATÓRIO" in titles[1]
        assert "FUNDAMENTOS" in titles[2]
        assert "CONCLUSÃO" in titles[3]

    def test_multiple_paragraphs_per_section(self):
        sections = {
            "ementa": "Paragrafo 1.\n\nParagrafo 2.",
            "relatorio": "",
            "fundamentos": "",
            "conclusao": "",
        }
        doc = _sections_to_tiptap(sections)
        ementa_paragraphs = []
        found_ementa = False
        for node in doc["content"]:
            if node["type"] == "heading" and node["content"][0]["text"] == "EMENTA":
                found_ementa = True
                continue
            if found_ementa and node["type"] == "paragraph":
                ementa_paragraphs.append(node)
            elif found_ementa and node["type"] == "heading":
                break
        assert len(ementa_paragraphs) == 2


class TestClassifyResponseParsing:
    """Valida o saneamento do output do P1 via _normalize_classification."""

    def test_normalize_handles_full_v5_payload(self):
        from app.services.parecer_ai_service import _normalize_classification

        raw = {
            "is_consulta_juridica": True,
            "municipio": "Potengi",
            "uf": "CE",
            "orgao_consulente": "Procuradoria Geral",
            "vertente": "licitacao_14133",
            "subtipo": "dispensa",
            "modo": "consultivo_puro",
            "tipo_parecer": "preventivo",
            "urgencia": "normal",
            "confianca_classificacao": "alta",
        }
        cls = _normalize_classification(raw, email_body="...")
        assert cls["vertente"] == "licitacao_14133"
        assert cls["subtipo"] == "dispensa"
        assert cls["modo"] == "consultivo_puro"
        assert cls["caso_integrado"] == []
        assert cls["lacuna_normativa_local"] == []
        assert cls["documentos_faltantes"] == []

    def test_normalize_falls_back_on_empty(self):
        from app.services.parecer_ai_service import _normalize_classification

        cls = _normalize_classification({}, email_body="texto do email")
        assert cls["vertente"] == "administrativo"
        assert cls["modo"] == "consultivo_puro"
        assert cls["tipo_parecer"] == "preventivo"
        assert cls["urgencia"] == "normal"
        assert cls["confianca_classificacao"] == "baixa"
        assert cls["duvida_central"] == "texto do email"

    def test_normalize_validates_enum_fields(self):
        from app.services.parecer_ai_service import _normalize_classification

        raw = {
            "vertente": "lixo_inválido",
            "modo": "outro_invalido",
            "tipo_parecer": "outro",
            "urgencia": "muito_alta",
        }
        cls = _normalize_classification(raw, email_body="")
        # Valores inválidos viram defaults conservadores
        assert cls["vertente"] == "administrativo"
        assert cls["modo"] == "consultivo_puro"
        assert cls["tipo_parecer"] == "preventivo"
        assert cls["urgencia"] == "normal"

    def test_normalize_coerces_lists(self):
        from app.services.parecer_ai_service import _normalize_classification

        raw = {
            "lacuna_normativa_local": "CTM não disponível",  # string em vez de lista
            "documentos_faltantes": None,
            "caso_integrado": ["tributario_financeiro"],
        }
        cls = _normalize_classification(raw, email_body="")
        assert cls["lacuna_normativa_local"] == []  # string vira lista vazia
        assert cls["documentos_faltantes"] == []
        assert cls["caso_integrado"] == ["tributario_financeiro"]
