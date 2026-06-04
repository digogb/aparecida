"""Testes da camada de leis municipais (índice sempre + lei relevante por tema)."""
from __future__ import annotations

import pytest

from app.services import leis_municipios as L


@pytest.fixture(autouse=True)
def _clear_cache():
    L.clear_cache()
    yield
    L.clear_cache()


def _integrais(bloco: str) -> list[str]:
    return [
        ln[len("### TEXTO INTEGRAL — "):]
        for ln in bloco.splitlines()
        if ln.startswith("### TEXTO INTEGRAL —")
    ]


def _index_count(bloco: str) -> int:
    return sum(1 for ln in bloco.splitlines() if ln.startswith("- **"))


def test_municipio_desconhecido_retorna_none():
    assert L.assemble_municipal_context("Cidade Inexistente", "servidores", "x") is None


def test_resolve_municipio_tolera_acento_e_caixa():
    # SALITRE não tem acento, mas a normalização deve casar variações de caixa.
    assert L._municipio_folder("salitre").name == "SALITRE"
    assert L._municipio_folder("SALITRE").name == "SALITRE"
    assert L._municipio_folder("Araripe").name == "ARARIPE"


def test_indice_sempre_presente_mesmo_sem_tema_casado():
    # Consulta de licitação (aditivo de locação) não casa lei de servidor — mas o
    # índice das leis locais deve aparecer mesmo assim, sem texto integral.
    bloco = L.assemble_municipal_context(
        "Salitre", subtipo="aditivo", assunto="prorrogação de contrato de locação de imóvel"
    )
    assert bloco is not None
    assert _index_count(bloco) >= 1
    assert _integrais(bloco) == []


def test_tema_servidor_inclui_estatuto_integral():
    bloco = L.assemble_municipal_context(
        "Salitre", subtipo="servidores", assunto="estabilidade de servidor efetivo"
    )
    assert bloco is not None
    integrais = _integrais(bloco)
    assert any("ESTATUTO" in t.upper() for t in integrais)


def test_top_match_grande_entra_apesar_do_orcamento():
    # O Estatuto de Salitre (~66k chars) excede o orçamento pequeno, mas como é o
    # match nº1 deve entrar mesmo assim (force_top_match=True por padrão).
    bloco = L.assemble_municipal_context(
        "Salitre", subtipo="servidores", assunto="servidor", full_text_budget=5_000
    )
    assert any("ESTATUTO" in t.upper() for t in _integrais(bloco))


def test_p3_nao_forca_lei_grande():
    # Na revisão (force_top_match=False, orçamento apertado) o estatuto grande NÃO
    # entra integral — só o índice permanece.
    bloco = L.assemble_municipal_context(
        "Salitre", subtipo="servidores", assunto="servidor",
        full_text_budget=5_000, force_top_match=False,
    )
    assert bloco is not None
    assert _integrais(bloco) == []
    assert _index_count(bloco) >= 1


def test_sinonimo_previdencia_casa_rpps():
    # subtipo "previdenciario" deve casar a lei de RPPS de Araripe via sinônimos,
    # mesmo o título sendo só "Lei Municipal nº 927/2009".
    bloco = L.assemble_municipal_context(
        "Araripe", subtipo="previdenciario", assunto="aposentadoria"
    )
    assert bloco is not None
    assert len(_integrais(bloco)) >= 1
