"""
Tests for assemble_p2_context (Camada 3 — carregamento modular de references).

Cobre:
- Camada A (mestre) sempre presente
- Camada B (subtipo) anexada quando há mapeamento
- Camada C (armadilhas-tce-ce) só para subtipos sensíveis da vertente licitação
- Few-shot anexado quando include_fewshot=True
- Cache (lru_cache) limpável
- Degradação sob estouro de orçamento (mockando o limite)

Run: pytest backend/tests/test_assemble_p2_context.py -v
"""
from __future__ import annotations

import pytest

from app.services import prompt_service
from app.services.prompt_service import (
    VERTENTE_ADMINISTRATIVO,
    VERTENTE_LICITACAO,
    VERTENTE_TERCEIRO_SETOR,
    VERTENTE_TRIBUTARIO,
    assemble_p2_context,
    assemble_p3_context,
    clear_assemble_cache,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_assemble_cache()
    yield
    clear_assemble_cache()


class TestCamadaA:

    def test_mestre_licitacao_sempre_presente(self):
        ctx = assemble_p2_context(VERTENTE_LICITACAO, subtipo="art_53", include_fewshot=False)
        # Conteúdo característico do prompt mestre de licitação
        assert "14.133" in ctx or "Lei 14.133" in ctx or "licitação" in ctx.lower()

    def test_mestre_municipal_sempre_presente(self):
        ctx = assemble_p2_context(VERTENTE_ADMINISTRATIVO, subtipo="servidores", include_fewshot=False)
        # Conteúdo característico do prompt municipal-geral
        assert "ZT" in ctx or "Zero Trust" in ctx or "municipal" in ctx.lower()


class TestCamadaB:

    def test_subtipo_dispensa_anexa_reference(self):
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "dispensa", include_fewshot=False)
        assert "REFERÊNCIA TEMÁTICA (licitacao_14133/dispensa)" in ctx

    def test_subtipo_iptu_anexa_reference(self):
        ctx = assemble_p2_context(VERTENTE_TRIBUTARIO, "tributario_iptu", include_fewshot=False)
        assert "REFERÊNCIA TEMÁTICA (tributario_financeiro/tributario_iptu)" in ctx

    def test_subtipo_mrosc_anexa_reference(self):
        ctx = assemble_p2_context(VERTENTE_TERCEIRO_SETOR, "terceiro_mrosc", include_fewshot=False)
        assert "REFERÊNCIA TEMÁTICA (terceiro_setor/terceiro_mrosc)" in ctx

    def test_subtipo_desconhecido_nao_quebra(self):
        # Sem mapeamento → não falha, só não anexa a Camada B.
        ctx = assemble_p2_context(VERTENTE_ADMINISTRATIVO, "subtipo_inexistente", include_fewshot=False)
        assert "REFERÊNCIA TEMÁTICA" not in ctx
        # Mas o mestre continua presente
        assert len(ctx) > 1000


class TestCamadaC:

    def test_armadilhas_anexa_para_dispensa(self):
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "dispensa", include_fewshot=False)
        assert "ARMADILHAS TCE-CE" in ctx

    def test_armadilhas_anexa_para_aditivo(self):
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "aditivo", include_fewshot=False)
        assert "ARMADILHAS TCE-CE" in ctx

    def test_armadilhas_anexa_para_sancao(self):
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "sancao", include_fewshot=False)
        assert "ARMADILHAS TCE-CE" in ctx

    def test_armadilhas_anexa_para_adesao_ata(self):
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "adesao_ata", include_fewshot=False)
        assert "ARMADILHAS TCE-CE" in ctx

    def test_armadilhas_nao_anexa_para_art_53(self):
        # art_53 NÃO é subtipo sensível.
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "art_53", include_fewshot=False)
        assert "ARMADILHAS TCE-CE" not in ctx

    def test_armadilhas_nao_anexa_para_outras_vertentes(self):
        ctx_adm = assemble_p2_context(VERTENTE_ADMINISTRATIVO, "servidores", include_fewshot=False)
        ctx_trib = assemble_p2_context(VERTENTE_TRIBUTARIO, "tributario_iptu", include_fewshot=False)
        assert "ARMADILHAS TCE-CE" not in ctx_adm
        assert "ARMADILHAS TCE-CE" not in ctx_trib


class TestFewshot:

    def test_fewshot_incluido_por_padrao(self):
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "art_53")  # default include_fewshot=True
        assert "EXEMPLOS DE REFERÊNCIA" in ctx

    def test_fewshot_pode_ser_desativado(self):
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "art_53", include_fewshot=False)
        assert "EXEMPLOS DE REFERÊNCIA" not in ctx


class TestOrcamento:

    def test_dispensa_completa_dentro_do_limite(self):
        """dispensa = mestre + few-shot + dispensa.md + armadilhas-tce-ce.md = caso mais pesado."""
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "dispensa", include_fewshot=True)
        # Cabe nos 100k chars (~25k tokens) — verifica que o orçamento não foi degradado.
        # Se foi degradado, "ARMADILHAS TCE-CE" sumiria.
        assert "ARMADILHAS TCE-CE" in ctx
        assert len(ctx) < 100_000  # respeita limite

    def test_degradacao_quando_limite_apertado(self, monkeypatch):
        """Mocka o limite para forçar degradação e verifica que a Camada C cai."""
        monkeypatch.setattr(prompt_service, "_MAX_P2_CONTEXT_CHARS", 50_000)
        clear_assemble_cache()  # invalida cache para a nova policy entrar
        ctx = assemble_p2_context(VERTENTE_LICITACAO, "dispensa", include_fewshot=True)
        # Subtipo (B) preservado; armadilhas (C) caem.
        assert "REFERÊNCIA TEMÁTICA" in ctx
        assert "ARMADILHAS TCE-CE" not in ctx


class TestCache:

    def test_segunda_chamada_usa_cache(self):
        ctx1 = assemble_p2_context(VERTENTE_LICITACAO, "art_53", include_fewshot=False)
        ctx2 = assemble_p2_context(VERTENTE_LICITACAO, "art_53", include_fewshot=False)
        assert ctx1 is ctx2  # mesma string em memória

    def test_clear_cache_funciona(self):
        ctx1 = assemble_p2_context(VERTENTE_LICITACAO, "art_53", include_fewshot=False)
        clear_assemble_cache()
        ctx2 = assemble_p2_context(VERTENTE_LICITACAO, "art_53", include_fewshot=False)
        # Mesmo conteúdo, instâncias diferentes (recarregadas do disco)
        assert ctx1 == ctx2


# ---------------------------------------------------------------------------
# assemble_p3_context (Camada 3 + 6 também no P3)
# ---------------------------------------------------------------------------

class TestAssembleP3:

    def test_mestre_p3_sempre_presente(self):
        ctx = assemble_p3_context(VERTENTE_LICITACAO, "art_53")
        # IRR-1, IRR-2, IRR-3 são as inviolatas do P3 — devem estar no prompt mestre
        assert "IRR-1" in ctx
        assert "IRR-2" in ctx
        assert "IRR-3" in ctx

    def test_zt_rules_presentes_no_mestre_p3(self):
        """As regras ZT da municipal-geral foram incorporadas ao P3 mestre."""
        ctx = assemble_p3_context(VERTENTE_ADMINISTRATIVO, "servidores")
        assert "ZT-1" in ctx
        assert "ZT-5" in ctx
        assert "ZT-8" in ctx

    def test_subtipo_dispensa_anexa_reference(self):
        ctx = assemble_p3_context(VERTENTE_LICITACAO, "dispensa")
        assert "REFERÊNCIA TEMÁTICA — REVISÃO (licitacao_14133/dispensa)" in ctx

    def test_armadilhas_anexa_para_subtipo_sensivel(self):
        ctx = assemble_p3_context(VERTENTE_LICITACAO, "dispensa")
        assert "ARMADILHAS TCE-CE" in ctx

    def test_armadilhas_nao_anexa_para_art_53(self):
        ctx = assemble_p3_context(VERTENTE_LICITACAO, "art_53")
        assert "ARMADILHAS TCE-CE" not in ctx

    def test_p3_nao_inclui_fewshot(self):
        """P3 revisa, não cria — few-shot da geração não agrega."""
        ctx = assemble_p3_context(VERTENTE_LICITACAO, "dispensa")
        assert "EXEMPLOS DE REFERÊNCIA" not in ctx

    def test_cache_p3_independente_de_p2(self):
        p2 = assemble_p2_context(VERTENTE_LICITACAO, "art_53", include_fewshot=False)
        p3 = assemble_p3_context(VERTENTE_LICITACAO, "art_53")
        # São contextos diferentes — P3 base é o prompt de revisão, P2 é geração
        assert p2 != p3
        # Mas ambos contêm o subtipo art_53? Não — art_53 não tem armadilhas e
        # P3 não tem few-shot. Verificar que P3 tem o mestre certo.
        assert "REVISÃO DE PARECER COM OBSERVAÇÕES" in p3

    def test_clear_cache_limpa_p3(self):
        ctx1 = assemble_p3_context(VERTENTE_LICITACAO, "dispensa")
        clear_assemble_cache()
        ctx2 = assemble_p3_context(VERTENTE_LICITACAO, "dispensa")
        assert ctx1 == ctx2  # mesmo conteúdo após recarga

    def test_p3_dentro_do_orcamento(self):
        """dispensa = mestre + subtipo + armadilhas — caso mais pesado para P3."""
        ctx = assemble_p3_context(VERTENTE_LICITACAO, "dispensa")
        assert len(ctx) < 60_000  # respeita _MAX_P3_CONTEXT_CHARS

    def test_degradacao_p3_quando_limite_apertado(self, monkeypatch):
        monkeypatch.setattr(prompt_service, "_MAX_P3_CONTEXT_CHARS", 30_000)
        clear_assemble_cache()
        ctx = assemble_p3_context(VERTENTE_LICITACAO, "dispensa")
        # Subtipo preservado; armadilhas caem.
        assert "REFERÊNCIA TEMÁTICA — REVISÃO" in ctx
        assert "ARMADILHAS TCE-CE" not in ctx
