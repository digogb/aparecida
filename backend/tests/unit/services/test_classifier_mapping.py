"""
Testes unitários para as tabelas de mapeamento do classifier.
Não usa DB — testa apenas a lógica de resolução de área → tema/modelo.
"""
from __future__ import annotations

import pytest

from app.models.parecer import ParecerModelo, ParecerTema
from app.services.classifier import (
    NotLegalConsultationError,
    _AREA_TO_MODELO,
    _AREA_TO_TEMA,
    _LICITACAO_AREAS,
)


class TestAreaToTema:
    def test_licitacao_areas_mapeiam_para_licitacao(self):
        for area in _LICITACAO_AREAS:
            assert _AREA_TO_TEMA[area] == ParecerTema.licitacao, f"falhou para área '{area}'"

    def test_agentes_publicos_eh_administrativo(self):
        assert _AREA_TO_TEMA["agentes_publicos"] == ParecerTema.administrativo

    def test_responsabilidade_fiscal_eh_administrativo(self):
        assert _AREA_TO_TEMA["responsabilidade_fiscal"] == ParecerTema.administrativo

    def test_urbanismo_eh_administrativo(self):
        assert _AREA_TO_TEMA["urbanismo"] == ParecerTema.administrativo

    def test_outro_eh_administrativo(self):
        assert _AREA_TO_TEMA["outro"] == ParecerTema.administrativo

    def test_area_desconhecida_usa_default_administrativo(self):
        area_inventada = "area_que_nao_existe"
        tema = _AREA_TO_TEMA.get(area_inventada, ParecerTema.administrativo)
        assert tema == ParecerTema.administrativo


class TestAreaToModelo:
    def test_licitacao_areas_mapeiam_para_modelo_licitacao(self):
        for area in _LICITACAO_AREAS:
            assert _AREA_TO_MODELO[area] == ParecerModelo.licitacao

    def test_area_administrativa_usa_default_generico(self):
        modelo = _AREA_TO_MODELO.get("agentes_publicos", ParecerModelo.generico)
        assert modelo == ParecerModelo.generico


class TestNotLegalConsultationError:
    def test_e_subclasse_de_value_error(self):
        assert issubclass(NotLegalConsultationError, ValueError)

    def test_mensagem_preservada(self):
        err = NotLegalConsultationError("não é consulta jurídica")
        assert "não é consulta jurídica" in str(err)
