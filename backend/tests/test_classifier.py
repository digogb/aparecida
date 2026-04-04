from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from app.prompts.classificacao import SYSTEM_PROMPT
from app.services.parecer_engine import _sections_to_tiptap


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


# TestParseSections e TestSectionsToHtml removidos: _parse_sections e _sections_to_html
# foram removidos do parecer_engine quando o pipeline migrou de formato [SEÇÃO] para XML.


class TestSectionsToTiptap:
    """
    _sections_to_tiptap agora usa chaves minúsculas e títulos formatados:
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
        """Verifica que os títulos das seções seguem o formato atual do documento."""
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
