"""
Testes unitários para as tabelas de mapeamento do classifier (P1 v5.0).
Não usa DB — testa apenas a resolução de vertente → tema/modelo legacy.
"""
from __future__ import annotations

from app.models.parecer import ParecerModelo, ParecerTema
from app.services.classifier import (
    NotLegalConsultationError,
    _LEGACY_AREA_TO_VERTENTE,
    _VERTENTE_TO_MODELO,
    _VERTENTE_TO_TEMA,
    _resolve_vertente_from_data,
)


class TestVertenteToTema:
    def test_licitacao_mapeia_para_licitacao(self):
        assert _VERTENTE_TO_TEMA["licitacao_14133"] == ParecerTema.licitacao

    def test_demais_vertentes_sao_administrativo(self):
        for v in ("administrativo", "tributario_financeiro", "terceiro_setor"):
            assert _VERTENTE_TO_TEMA[v] == ParecerTema.administrativo

    def test_todas_vertentes_tem_tema_e_modelo(self):
        assert set(_VERTENTE_TO_TEMA) == set(_VERTENTE_TO_MODELO)


class TestVertenteToModelo:
    def test_licitacao_usa_modelo_licitacao(self):
        assert _VERTENTE_TO_MODELO["licitacao_14133"] == ParecerModelo.licitacao

    def test_demais_usam_modelo_generico(self):
        for v in ("administrativo", "tributario_financeiro", "terceiro_setor"):
            assert _VERTENTE_TO_MODELO[v] == ParecerModelo.generico


class TestResolveVertente:
    def test_vertente_valida_e_usada_diretamente(self):
        assert _resolve_vertente_from_data({"vertente": "licitacao_14133"}) == "licitacao_14133"

    def test_vertente_desconhecida_cai_no_fallback_legacy(self):
        # vertente inválida + sem area_principal => default administrativo
        assert _resolve_vertente_from_data({"vertente": "inexistente"}) == "administrativo"

    def test_schema_legacy_area_principal_mapeia(self):
        assert _resolve_vertente_from_data({"area_principal": "licitacoes_contratos"}) == "licitacao_14133"
        assert _resolve_vertente_from_data({"area_principal": "tributos_municipais"}) == "tributario_financeiro"

    def test_area_legacy_desconhecida_default_administrativo(self):
        assert _resolve_vertente_from_data({"area_principal": "algo_que_nao_existe"}) == "administrativo"

    def test_payload_vazio_default_administrativo(self):
        assert _resolve_vertente_from_data({}) == "administrativo"

    def test_todas_areas_legacy_resolvem_para_vertente_valida(self):
        for area, vertente in _LEGACY_AREA_TO_VERTENTE.items():
            assert vertente in _VERTENTE_TO_TEMA, f"área legacy '{area}' aponta p/ vertente inválida"


class TestNotLegalConsultationError:
    def test_e_subclasse_de_value_error(self):
        assert issubclass(NotLegalConsultationError, ValueError)

    def test_mensagem_preservada(self):
        err = NotLegalConsultationError("não é consulta jurídica")
        assert "não é consulta jurídica" in str(err)
