"""
T1 — Serviço de Prompts
Carrega, versiona e monta os system prompts para cada etapa do pipeline v5.0.

Pipeline v5.0 (Camada 1 — alinhada às skills parecer-lei-14133 e parecer-municipal-geral):
- P1: classificação (segue v4.1; refinamento de schema é Camada 2)
- P2: roteado por vertente → p2_parecer_lei_14133 ou p2_parecer_municipal_geral
- P3: revisão (segue v4.1)
"""
from __future__ import annotations

import functools
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPT_VERSION = "5.0"
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"

# Limite duro do system prompt P2 montado (chars ≈ tokens * 4).
# Sonnet 4.6 TPM = 30k; com user_message ~15k tokens, system deve ficar < 10k tokens (~40k chars).
# Mas durante a operação real do escritório (2-3 pareceres/dia) podemos esticar até ~25k tokens
# de system prompt — fica acima do TPM mas dentro do limite por requisição (200k context).
# Acima de 100k chars (~25k tokens) acionamos degradação removendo as camadas opcionais.
_MAX_P2_CONTEXT_CHARS = 100_000


# Vertentes do P2 (Camada 1)
VERTENTE_LICITACAO = "licitacao_14133"
VERTENTE_ADMINISTRATIVO = "administrativo"
VERTENTE_TRIBUTARIO = "tributario_financeiro"
VERTENTE_TERCEIRO_SETOR = "terceiro_setor"


# Mapeamento do P1 v4.1 (area_principal) → vertente do P2 v5.0.
# Mantido como fallback para reprocessamento de pareceres antigos cujo `classificacao` no
# banco ainda foi gravado no schema v4.1. O P1 v5.0 já devolve `vertente` diretamente.
_AREA_TO_VERTENTE: dict[str, str] = {
    "licitacoes_contratos": VERTENTE_LICITACAO,
    "terceiro_setor": VERTENTE_TERCEIRO_SETOR,
    "responsabilidade_fiscal": VERTENTE_TRIBUTARIO,
    "tributos_municipais": VERTENTE_TRIBUTARIO,
    "repasses_financeiros": VERTENTE_TRIBUTARIO,
    "agentes_publicos": VERTENTE_ADMINISTRATIVO,
    "controle_improbidade": VERTENTE_ADMINISTRATIVO,
    "previdenciario": VERTENTE_ADMINISTRATIVO,
    "urbanismo": VERTENTE_ADMINISTRATIVO,
    "bens_servicos_publicos": VERTENTE_ADMINISTRATIVO,
    "outro": VERTENTE_ADMINISTRATIVO,
}


def load_prompt(stage: str) -> str:
    """
    Carrega o system prompt para a etapa.
    stage: "p1_classification" | "p2_parecer_lei_14133" | "p2_parecer_municipal_geral" | "p3_parecer_revision"
    """
    path = PROMPTS_DIR / f"{stage}.txt"
    return path.read_text(encoding="utf-8")


def resolve_vertente(classification: dict | None) -> str:
    """Resolve a vertente do P2 a partir da classificação P1.

    Prioridade:
    1. Campo explícito `vertente` na classificação (Camada 2 — quando o P1 refinado roda).
    2. Mapeamento de `area_principal` para vertente (compatibilidade com P1 v4.1).
    3. Fallback: administrativo.
    """
    if not classification:
        return VERTENTE_ADMINISTRATIVO

    explicit = classification.get("vertente")
    if isinstance(explicit, str) and explicit in {
        VERTENTE_LICITACAO,
        VERTENTE_ADMINISTRATIVO,
        VERTENTE_TRIBUTARIO,
        VERTENTE_TERCEIRO_SETOR,
    }:
        return explicit

    area = (classification.get("area_principal") or "").strip().lower()
    return _AREA_TO_VERTENTE.get(area, VERTENTE_ADMINISTRATIVO)


def _examples_filename(vertente: str) -> str:
    if vertente == VERTENTE_LICITACAO:
        return "examples_lei_14133.md"
    return "examples_municipal_geral.md"


def _prompt_filename(vertente: str) -> str:
    if vertente == VERTENTE_LICITACAO:
        return "p2_parecer_lei_14133"
    return "p2_parecer_municipal_geral"


def build_p2_prompt(vertente: str, include_fewshot: bool = True) -> str:
    """
    Monta o prompt do P2 conforme a vertente do parecer.

    vertente: "licitacao_14133" → prompt da skill parecer-lei-14133
              outras → prompt da skill parecer-municipal-geral

    Few-shot examples são apendados como referência de estilo (estrutura tripartite estrita,
    ementa em MAIÚSCULAS com figure-dash, fundamentos em prosa contínua sem subdivisão
    numerada, paráfrase funcional após citação, advertência protetiva em prosa sóbria).
    """
    base = load_prompt(_prompt_filename(vertente))
    if not include_fewshot:
        return base

    fewshot_path = PROMPTS_DIR / _examples_filename(vertente)
    if not fewshot_path.exists():
        logger.warning("Few-shot examples não encontrado: %s", fewshot_path)
        return base

    fewshot = fewshot_path.read_text(encoding="utf-8")
    return base + "\n\n---\n\n## EXEMPLOS DE REFERÊNCIA\n\n" + fewshot


def get_prompt_version() -> str:
    return PROMPT_VERSION


# ---------------------------------------------------------------------------
# Camada 3 — Carregamento modular de references por subtipo
# ---------------------------------------------------------------------------

# Subtipos da vertente licitação para os quais o índice TCE-CE é obrigatório.
# Coincidem com os "5 sensíveis" das skills (dispensa por valor, dispensa
# emergencial, adesão a ata, prorrogação, sanção).
_SUBTIPOS_SENSIVEIS_LICITACAO = frozenset(
    {"dispensa", "adesao_ata", "aditivo", "sancao"}
)

# Mapeamento (vertente, subtipo) → arquivo .md em skills/.../references/.
# As chaves de subtipo casam com a lista fechada do P1 (Camada 2).
# Quando um subtipo não tem reference dedicada, o P2 ainda recebe o prompt
# mestre da vertente — só não há carga extra de Camada C.
_SUBTIPO_REFERENCES: dict[tuple[str, str], str] = {
    # parecer-lei-14133/references/
    (VERTENTE_LICITACAO, "art_53"): "fase-preparatoria.md",
    (VERTENTE_LICITACAO, "dispensa"): "dispensa.md",
    (VERTENTE_LICITACAO, "inexigibilidade"): "inexigibilidade.md",
    (VERTENTE_LICITACAO, "credenciamento"): "inexigibilidade.md",
    (VERTENTE_LICITACAO, "adesao_ata"): "sistema-registro-precos.md",
    (VERTENTE_LICITACAO, "aditivo"): "contratos-aditivos.md",
    (VERTENTE_LICITACAO, "sancao"): "sancoes-contratuais.md",
    (VERTENTE_LICITACAO, "impugnacao_recurso"): "impugnacoes-recursos.md",
    # parecer-municipal-geral/references/administrativo/
    (VERTENTE_ADMINISTRATIVO, "servidores"): "servidores-publicos.md",
    (VERTENTE_ADMINISTRATIVO, "concurso_publico"): "servidores-publicos.md",
    (VERTENTE_ADMINISTRATIVO, "improbidade"): "improbidade-consultivo-ex-ante.md",
    (VERTENTE_ADMINISTRATIVO, "ato_administrativo"): "atos-administrativos.md",
    (VERTENTE_ADMINISTRATIVO, "bens_publicos"): "bens-publicos.md",
    (VERTENTE_ADMINISTRATIVO, "convenio"): "convenios-administrativos.md",
    (VERTENTE_ADMINISTRATIVO, "desapropriacao"): "desapropriacao.md",
    (VERTENTE_ADMINISTRATIVO, "fundeb"): "fundeb.md",
    (VERTENTE_ADMINISTRATIVO, "lai"): "lai-transparencia.md",
    (VERTENTE_ADMINISTRATIVO, "lrf_pessoal"): "lrf-vertente-administrativa.md",
    (VERTENTE_ADMINISTRATIVO, "pad"): "pad-sindicancia.md",
    (VERTENTE_ADMINISTRATIVO, "processo_administrativo"): "processo-administrativo.md",
    (VERTENTE_ADMINISTRATIVO, "regularizacao_fundiaria"): "regularizacao-fundiaria.md",
    (VERTENTE_ADMINISTRATIVO, "responsabilidade_civil"): "responsabilidade-civil-estado.md",
    (VERTENTE_ADMINISTRATIVO, "servico_publico"): "servicos-publicos.md",
    (VERTENTE_ADMINISTRATIVO, "urbanismo"): "urbanismo-municipal.md",
    (VERTENTE_ADMINISTRATIVO, "competencia"): "competencias-municipais.md",
    (VERTENTE_ADMINISTRATIVO, "lei_organica"): "lei-organica-processo-legislativo.md",
    # parecer-municipal-geral/references/tributario-financeiro/
    (VERTENTE_TRIBUTARIO, "tributario_iptu"): "iptu.md",
    (VERTENTE_TRIBUTARIO, "tributario_iss"): "iss-lc-116.md",
    (VERTENTE_TRIBUTARIO, "tributario_itbi"): "itbi.md",
    (VERTENTE_TRIBUTARIO, "taxas"): "taxas-municipais.md",
    (VERTENTE_TRIBUTARIO, "contribuicao_melhoria"): "contribuicao-melhoria.md",
    (VERTENTE_TRIBUTARIO, "refis"): "beneficios-fiscais.md",
    (VERTENTE_TRIBUTARIO, "lrf_fiscal"): "lrf-limites-fiscais.md",
    (VERTENTE_TRIBUTARIO, "credito_tributario"): "credito-tributario.md",
    (VERTENTE_TRIBUTARIO, "execucao_fiscal"): "execucao-fiscal-lef.md",
    (VERTENTE_TRIBUTARIO, "competencia_tributaria"): "competencia-tributaria-municipal.md",
    (VERTENTE_TRIBUTARIO, "despesa_publica"): "despesa-publica-4320.md",
    (VERTENTE_TRIBUTARIO, "planejamento_orcamentario"): "planejamento-orcamentario.md",
    (VERTENTE_TRIBUTARIO, "precatorios"): "precatorios-rpvs.md",
    (VERTENTE_TRIBUTARIO, "prescricao"): "prescricao-decadencia-tributaria.md",
    (VERTENTE_TRIBUTARIO, "reparticao_receitas"): "reparticao-receitas.md",
    (VERTENTE_TRIBUTARIO, "restos_a_pagar"): "restos-a-pagar.md",
    # parecer-municipal-geral/references/terceiro-setor/
    (VERTENTE_TERCEIRO_SETOR, "terceiro_mrosc"): "mrosc-lei-13019.md",
    (VERTENTE_TERCEIRO_SETOR, "terceiro_cebas"): "cebas-certificacao.md",
    (VERTENTE_TERCEIRO_SETOR, "terceiro_chamamento"): "chamamento-publico.md",
    (VERTENTE_TERCEIRO_SETOR, "terceiro_os"): "os-contrato-gestao.md",
    (VERTENTE_TERCEIRO_SETOR, "terceiro_oscip"): "oscip-termo-parceria.md",
    (VERTENTE_TERCEIRO_SETOR, "terceiro_prestacao_contas"): "prestacao-contas-terceiro-setor.md",
    (VERTENTE_TERCEIRO_SETOR, "terceiro_ecossistema"): "ecossistema-terceiro-setor.md",
}

# Mapa vertente → pasta-pai dentro de skills/parecer-municipal-geral/references/.
# `licitacao_14133` é tratado à parte porque vive em outra skill.
_VERTENTE_TO_SUBFOLDER = {
    VERTENTE_ADMINISTRATIVO: "administrativo",
    VERTENTE_TRIBUTARIO: "tributario-financeiro",
    VERTENTE_TERCEIRO_SETOR: "terceiro-setor",
}


def _reference_path(vertente: str, filename: str) -> Path:
    if vertente == VERTENTE_LICITACAO:
        return SKILLS_DIR / "parecer-lei-14133" / "references" / filename
    folder = _VERTENTE_TO_SUBFOLDER.get(vertente)
    if not folder:
        return SKILLS_DIR / "parecer-municipal-geral" / "references" / filename
    return SKILLS_DIR / "parecer-municipal-geral" / "references" / folder / filename


def _armadilhas_path() -> Path:
    return SKILLS_DIR / "parecer-lei-14133" / "references" / "armadilhas-tce-ce.md"


def _load_text(path: Path) -> str | None:
    """Lê um arquivo de reference; devolve None se não existir."""
    if not path.exists():
        logger.warning("Reference inexistente: %s", path)
        return None
    return path.read_text(encoding="utf-8")


@functools.lru_cache(maxsize=128)
def assemble_p2_context(
    vertente: str,
    subtipo: str = "",
    modo: str = "consultivo_puro",
    include_fewshot: bool = True,
) -> str:
    """Monta o system prompt P2 modular para (vertente, subtipo, modo).

    Camadas:
      A. Prompt mestre da vertente (`p2_parecer_*.txt`) — sempre.
      B. Reference do subtipo (`skills/.../references/...`) — quando há mapeamento.
      C. Armadilhas TCE-CE (`armadilhas-tce-ce.md`) — apenas para os subtipos
         sensíveis da vertente licitação (dispensa, adesão a ata, aditivo, sanção).
      D. Few-shot examples (`examples_*.md`) — quando `include_fewshot=True`.

    O `modo` é usado apenas para logging hoje; deixamos no schema porque a
    Camada 6 vai consumir ele (em quase-processual o orçamento de tool use
    cresce).

    Há cache em memória (`lru_cache`) — references não mudam entre execuções.

    Validação de orçamento: se o resultado exceder `_MAX_P2_CONTEXT_CHARS`,
    a camada C (armadilhas) é descartada e um warning é logado.
    """
    base = build_p2_prompt(vertente, include_fewshot=include_fewshot)
    parts: list[str] = [base]
    layers: list[str] = ["A:mestre"]
    if include_fewshot:
        layers.append("D:fewshot")

    # Camada B — subtipo-specific
    filename = _SUBTIPO_REFERENCES.get((vertente, subtipo))
    if filename:
        body = _load_text(_reference_path(vertente, filename))
        if body:
            parts.append(
                f"## REFERÊNCIA TEMÁTICA ({vertente}/{subtipo})\n\n{body}"
            )
            layers.append(f"B:{filename}")

    # Camada C — armadilhas TCE-CE (subtipos sensíveis da licitação)
    armadilhas_loaded = False
    if vertente == VERTENTE_LICITACAO and subtipo in _SUBTIPOS_SENSIVEIS_LICITACAO:
        body = _load_text(_armadilhas_path())
        if body:
            parts.append(f"## ARMADILHAS TCE-CE\n\n{body}")
            layers.append("C:armadilhas-tce-ce")
            armadilhas_loaded = True

    assembled = "\n\n---\n\n".join(parts)
    chars = len(assembled)

    if chars > _MAX_P2_CONTEXT_CHARS and armadilhas_loaded:
        # Degradação — remove a camada C e remonta.
        logger.warning(
            "P2 context %d chars > %d budget — descartando camada C (armadilhas) "
            "para vertente=%s subtipo=%s",
            chars, _MAX_P2_CONTEXT_CHARS, vertente, subtipo,
        )
        parts.pop()  # remove armadilhas (último anexado)
        layers.pop()
        assembled = "\n\n---\n\n".join(parts)
        chars = len(assembled)

    logger.info(
        "P2 context montado: vertente=%s subtipo=%s modo=%s chars=%d layers=%s",
        vertente, subtipo, modo, chars, "+".join(layers),
    )
    return assembled


def clear_assemble_cache() -> None:
    """Limpa o cache do assemble_p2_context — útil em testes e após editar references."""
    assemble_p2_context.cache_clear()
    assemble_p3_context.cache_clear()


# ---------------------------------------------------------------------------
# Camada 3 + 6 também para o P3 (revisão)
# ---------------------------------------------------------------------------

# Limite mais apertado que P2: o user_message do P3 já carrega o XML do parecer
# original (~10-15k tokens). Mantemos o system prompt < 60k chars (~15k tokens).
_MAX_P3_CONTEXT_CHARS = 60_000


@functools.lru_cache(maxsize=128)
def assemble_p3_context(
    vertente: str,
    subtipo: str = "",
    modo: str = "consultivo_puro",
) -> str:
    """Monta o system prompt P3 modular para revisão dirigida (vertente, subtipo, modo).

    Camadas:
      A. Prompt mestre de revisão (`p3_parecer_revision.txt`) — sempre.
      B. Reference do subtipo — quando há mapeamento.
      C. Armadilhas TCE-CE — para os subtipos sensíveis da vertente licitação.

    Diferenças em relação a `assemble_p2_context`:
    - Sem few-shot (P3 revisa, não cria; few-shot da geração não agrega).
    - Orçamento mais apertado (60k chars vs 100k do P2) — o user_message do P3
      carrega o XML do parecer original.
    - Em caso de estouro, derruba primeiro a Camada C (armadilhas).
    """
    base = load_prompt("p3_parecer_revision")
    parts: list[str] = [base]
    layers: list[str] = ["A:mestre_p3"]

    filename = _SUBTIPO_REFERENCES.get((vertente, subtipo))
    if filename:
        body = _load_text(_reference_path(vertente, filename))
        if body:
            parts.append(
                f"## REFERÊNCIA TEMÁTICA — REVISÃO ({vertente}/{subtipo})\n\n"
                "Use estas diretrizes ao reescrever a seção. NÃO replique conteúdo "
                "literal — apenas ajuste o parecer original para alinhar com o que "
                "se segue.\n\n"
                f"{body}"
            )
            layers.append(f"B:{filename}")

    armadilhas_loaded = False
    if vertente == VERTENTE_LICITACAO and subtipo in _SUBTIPOS_SENSIVEIS_LICITACAO:
        body = _load_text(_armadilhas_path())
        if body:
            parts.append(f"## ARMADILHAS TCE-CE — atenção redobrada na revisão\n\n{body}")
            layers.append("C:armadilhas-tce-ce")
            armadilhas_loaded = True

    assembled = "\n\n---\n\n".join(parts)
    chars = len(assembled)

    if chars > _MAX_P3_CONTEXT_CHARS and armadilhas_loaded:
        logger.warning(
            "P3 context %d chars > %d budget — descartando camada C (armadilhas) "
            "para vertente=%s subtipo=%s",
            chars, _MAX_P3_CONTEXT_CHARS, vertente, subtipo,
        )
        parts.pop()
        layers.pop()
        assembled = "\n\n---\n\n".join(parts)
        chars = len(assembled)

    logger.info(
        "P3 context montado: vertente=%s subtipo=%s modo=%s chars=%d layers=%s",
        vertente, subtipo, modo, chars, "+".join(layers),
    )
    return assembled
