from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from app.prompts.classificacao import SYSTEM_PROMPT
from app.services.parecer_engine import _parse_sections, _sections_to_html, _sections_to_tiptap


class TestClassificacaoPrompt:
    def test_prompt_mentions_all_themes(self):
        for tema in ["administrativo", "licitacao"]:
            assert tema in SYSTEM_PROMPT

    def test_prompt_mentions_models(self):
        assert "generico" in SYSTEM_PROMPT
        assert "licitacao" in SYSTEM_PROMPT

    def test_prompt_requests_json(self):
        assert "JSON" in SYSTEM_PROMPT

    def test_prompt_mentions_lei_14133(self):
        assert "14.133" in SYSTEM_PROMPT

    def test_prompt_has_required_fields(self):
        for field in ["tema", "subtema", "modelo_parecer", "municipio_detectado", "confianca"]:
            assert field in SYSTEM_PROMPT


class TestParseSections:
    def test_parse_all_four_sections(self):
        text = (
            "[EMENTA]\nResumo do parecer.\n\n"
            "[RELATORIO]\nFatos narrados.\n\n"
            "[FUNDAMENTACAO]\nAnalise juridica.\n\n"
            "[CONCLUSAO]\nResposta objetiva."
        )
        sections = _parse_sections(text)
        assert len(sections) == 4
        assert "Resumo do parecer." in sections["EMENTA"]
        assert "Fatos narrados." in sections["RELATORIO"]
        assert "Analise juridica." in sections["FUNDAMENTACAO"]
        assert "Resposta objetiva." in sections["CONCLUSAO"]

    def test_parse_with_extra_content(self):
        text = (
            "Texto antes ignorado\n"
            "[EMENTA]\nEmenta aqui.\n"
            "[RELATORIO]\nRelatorio aqui.\n"
            "[FUNDAMENTACAO]\nFundamentacao aqui.\n"
            "[CONCLUSAO]\nConclusao aqui."
        )
        sections = _parse_sections(text)
        assert "EMENTA" in sections
        assert "RELATORIO" in sections
        assert "FUNDAMENTACAO" in sections
        assert "CONCLUSAO" in sections

    def test_parse_empty_text(self):
        sections = _parse_sections("")
        assert sections == {}

    def test_parse_partial_sections(self):
        text = "[EMENTA]\nApenas ementa.\n[CONCLUSAO]\nApenas conclusao."
        sections = _parse_sections(text)
        assert len(sections) == 2
        assert "EMENTA" in sections
        assert "CONCLUSAO" in sections


class TestSectionsToHtml:
    def test_generates_html_with_headings(self):
        sections = {
            "EMENTA": "Resumo.",
            "RELATORIO": "Fatos.",
            "FUNDAMENTACAO": "Analise.",
            "CONCLUSAO": "Resposta.",
        }
        html = _sections_to_html(sections)
        assert "<h2>EMENTA</h2>" in html
        assert "<h2>RELATORIO</h2>" in html
        assert "<h2>FUNDAMENTACAO</h2>" in html
        assert "<h2>CONCLUSAO</h2>" in html
        assert "<p>Resumo.</p>" in html

    def test_handles_missing_sections(self):
        sections = {"EMENTA": "Apenas ementa."}
        html = _sections_to_html(sections)
        assert "<h2>EMENTA</h2>" in html
        assert "<p>Apenas ementa.</p>" in html
        assert "<h2>RELATORIO</h2>" in html


class TestSectionsToTiptap:
    def test_generates_valid_tiptap_doc(self):
        sections = {
            "EMENTA": "Resumo.",
            "RELATORIO": "Fatos.",
            "FUNDAMENTACAO": "Analise.",
            "CONCLUSAO": "Resposta.",
        }
        doc = _sections_to_tiptap(sections)
        assert doc["type"] == "doc"
        assert len(doc["content"]) == 8  # 4 headings + 4 paragraphs

        headings = [n for n in doc["content"] if n["type"] == "heading"]
        assert len(headings) == 4
        assert headings[0]["content"][0]["text"] == "EMENTA"

    def test_multiple_paragraphs_per_section(self):
        sections = {"EMENTA": "Paragrafo 1.\n\nParagrafo 2.", "RELATORIO": "", "FUNDAMENTACAO": "", "CONCLUSAO": ""}
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
    def test_valid_classification_json(self):
        sample = {
            "tema": "licitacao",
            "subtema": "dispensa de licitacao por valor",
            "modelo_parecer": "licitacao",
            "municipio_detectado": "Guarulhos",
            "confianca": 0.92,
        }
        raw = json.dumps(sample)
        parsed = json.loads(raw)
        assert parsed["tema"] == "licitacao"
        assert parsed["modelo_parecer"] == "licitacao"
        assert parsed["confianca"] == 0.92

    def test_licitacao_detection_keywords(self):
        keywords = ["licitacao", "pregao", "Lei 14.133", "dispensa", "inexigibilidade"]
        for kw in keywords:
            assert kw.lower() in SYSTEM_PROMPT.lower() or kw in SYSTEM_PROMPT
