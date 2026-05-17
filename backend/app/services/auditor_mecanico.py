"""
Auditor Mecânico — Gate IRR-1 + IRR-2
Pipeline v5.0 (Camada 4 — alinhado às skills parecer-lei-14133 e parecer-municipal-geral).

Portado de:
- parecer-lei-14133/scripts/auditor_mecanico.py
- parecer-municipal-geral/scripts/auditor_mecanico.py

Diferença em relação ao auditor das skills: opera sobre `sections` dict (resultado de
`parse_parecer_xml`) ou sobre TipTap JSON, sem depender de um `.docx` físico. Isso permite
rodar o gate **imediatamente após a geração** pelo P2, antes de salvar a versão, e
acionar revisão automática pelo P3 quando falhar.

REGRA IRR-1 — ementa em MAIÚSCULAS, exceto:
  - Indicadores ordinais 'º', '°', 'ª'
  - Letras de alíneas entre aspas ('a', 'b', 'c')

REGRA IRR-2 — parágrafos da fundamentação não podem ter 8+ linhas estimadas.
  Parâmetros: CHARS_PER_LINE = 78 (Consolas 12pt, margens 2,5/3,0/3,0/3,0 cm em A4).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

CHARS_PER_LINE = 78

# Referências normativas com grafia legal canônica — preservam minúsculas dentro da
# ementa toda em CAPS. Padrão derivado da skill v5.0:
#   "art. 125", "art. 124, inciso I, alínea 'b'", "Lei nº 14.133/2021",
#   "Lei Complementar n. 101/2000", "§ 1º", "§ 6º", "inciso II", "alínea 'b'",
#   "Súmula Vinculante 13", "CF art. 37, § 6º", "CTN art. 173"
# A lógica do gerador_docx.py das skills aplica .upper() no final, eliminando o problema
# no .docx — aqui auditamos antes da renderização, então toleramos as referências.
_LEGAL_REF_PATTERNS: list[re.Pattern] = [
    # art. NN, art. NN-A
    re.compile(r"\bart\.\s*\d+[\w\-]*", re.IGNORECASE),
    # Lei nº NNNN/AAAA, Lei n. NNNN/AAAA, Lei Complementar nº NN/AAAA
    re.compile(r"\bLei(?:\s+Complementar)?\s+n[º°\.]?\s*\d[\d\.\,/\-]*", re.IGNORECASE),
    # § NNº
    re.compile(r"§\s*\d+[º°ª]?"),
    # inciso II, inciso XXIII
    re.compile(r"\binciso\s+[IVXLCDM]+", re.IGNORECASE),
    # alínea 'b'
    re.compile(r"\balínea\s+['‘’][a-z]['‘’]", re.IGNORECASE),
    # parágrafo único, parágrafo NN
    re.compile(r"\bparágrafo\s+(?:único|\d+)", re.IGNORECASE),
    # caput
    re.compile(r"\bcaput\b", re.IGNORECASE),
    # Súmula Vinculante NN, Súmula NN
    re.compile(r"\bsúmula(?:\s+vinculante)?\s+n?[º°\.]?\s*\d+", re.IGNORECASE),
    # Acórdão NNNN/AAAA-Plenário
    re.compile(r"\bacórdão\s+n?[º°\.]?\s*\d[\d\./\-]*", re.IGNORECASE),
    # Tema NN, Tema NN de Repercussão Geral
    re.compile(r"\btema\s+\d+", re.IGNORECASE),
    # c/c (combinado com — conector jurídico canônico)
    re.compile(r"\bc/c\b"),
    # CF, CTN, LRF, ADCT, EC, ON, IN (siglas curtas em CAPS — já OK, listadas só por completude)
]

# Prefixos de parágrafos que NÃO entram no contador de linhas IRR-2 (títulos, fórmulas
# invariáveis, bloco de assinaturas etc.). Lista derivada da skill.
_TITULOS_PULAR = (
    "EMENTA",
    "PARECER JURÍDICO",
    "Órgão Consulente",
    "Consulente:",
    "I —", "II —", "III —",
    "I -", "II -", "III -",
    "Fortaleza",
    "FRANCISCO IONE", "MATHEUS", "FLÁVIO", "VALÉRIA", "OAB",
    "É o breve relatório", "É o parecer",
)

# Comprimento mínimo para considerar um parágrafo no IRR-2 (chars). Pula linhas curtas
# como fórmulas de fechamento.
_MIN_PARAGRAFO_CHARS = 100


@dataclass
class ParagrafoLongo:
    secao: str          # "fundamentos" | "relatorio" | "conclusao"
    indice: int          # posição do parágrafo dentro da seção (0-based)
    n_linhas: int        # linhas estimadas
    n_chars: int         # caracteres
    preview: str         # primeiros 150 chars


@dataclass
class AuditorResult:
    passed: bool
    violacoes: list[str] = field(default_factory=list)
    paragrafos_longos: list[ParagrafoLongo] = field(default_factory=list)
    ementa_ok: bool | None = None

    def as_log_dict(self) -> dict[str, Any]:
        """Serializa para gravação em ParecerVersion.gate_mecanico_log (JSONB)."""
        return {
            "passed": self.passed,
            "ementa_ok": self.ementa_ok,
            "violacoes": list(self.violacoes),
            "paragrafos_longos": [
                {
                    "secao": p.secao,
                    "indice": p.indice,
                    "n_linhas": p.n_linhas,
                    "n_chars": p.n_chars,
                    "preview": p.preview,
                }
                for p in self.paragrafos_longos
            ],
        }


def estimar_linhas(texto: str, chars_per_line: int = CHARS_PER_LINE) -> int:
    """Estimativa conservadora de linhas no .docx renderizado (idêntica ao auditor das skills)."""
    if not texto or not texto.strip():
        return 0
    linhas = 0
    for trecho in texto.split("\n"):
        if not trecho.strip():
            linhas += 1
            continue
        # Equivalente a math.ceil(len / chars_per_line), usando truque inteiro
        linhas += max(1, -(-len(trecho) // chars_per_line))
    return linhas


def _ementa_filtrada(txt: str) -> str:
    """Remove de `txt` os trechos que NÃO entram na checagem de IRR-1.

    Exceções permitidas pela skill v5.0:
    - Indicadores ordinais 'º', '°', 'ª'
    - Letras de alíneas entre aspas: 'a', 'b', 'c' (aspas ASCII ou curvas)
    - Referências normativas canônicas: "art. NN", "Lei nº NN/AAAA", "§ Nº",
      "inciso II", "alínea 'b'", "Súmula NN", "Acórdão NN/AAAA" — derivadas da
      grafia legal autoral do escritório, normalizadas para CAPS pelo gerador
      determinístico de DOCX (Camada 5) antes da gravação.

    Os trechos removidos são substituídos por espaço para preservar limites de palavras.
    """
    # 1) Mascarar referências normativas (canônica em minúsculas)
    masked = txt
    for pat in _LEGAL_REF_PATTERNS:
        masked = pat.sub(lambda m: " " * len(m.group(0)), masked)

    # 2) Remover indicadores ordinais e letras de alíneas entre aspas
    chars_relevantes: list[str] = []
    i = 0
    while i < len(masked):
        c = masked[i]
        # Padrão de alínea entre aspas: 'X', onde X é letra. Aceita ASCII ' e curvas ‘ ’.
        if c in ("'", "‘", "’") and i + 2 < len(masked) \
                and masked[i + 1].isalpha() and masked[i + 2] in ("'", "‘", "’"):
            i += 3
            continue
        if c not in ("º", "°", "ª"):
            chars_relevantes.append(c)
        i += 1
    return "".join(chars_relevantes)


def _auditar_ementa(ementa: str) -> tuple[bool | None, list[str]]:
    """Aplica IRR-1. Retorna (passou, violações)."""
    if not ementa or not ementa.strip():
        return None, ["REGRA IRR-1: ementa ausente ou vazia"]

    # A ementa pode vir com prefixo "EMENTA:" ou ser apenas o conteúdo. Aceitar ambos.
    txt = ementa.strip()
    filtrado = _ementa_filtrada(txt)

    if filtrado == filtrado.upper():
        return True, []

    minusculas = sorted({c for c in filtrado if c.islower()})
    return False, [
        f"REGRA IRR-1 VIOLADA: ementa contém minúsculas indevidas: {minusculas}"
    ]


def _auditar_secao_paragrafos(secao_nome: str, texto: str) -> list[ParagrafoLongo]:
    """Detecta parágrafos com 8+ linhas estimadas. Parágrafos são separados por \\n\\n."""
    if not texto:
        return []

    longos: list[ParagrafoLongo] = []
    paragrafos = [p.strip() for p in texto.split("\n\n")]

    for idx, p in enumerate(paragrafos):
        if not p or len(p) < _MIN_PARAGRAFO_CHARS:
            continue
        if p.startswith(_TITULOS_PULAR):
            continue
        # Pular blockquote em linha única (citação literal recuada)
        if p.startswith(">"):
            continue
        # Pular alíneas isoladas da conclusão
        if p.lstrip().startswith(("a)", "b)", "c)", "d)", "e)", "f)", "(a)", "(b)", "(c)")):
            # Mas se a alínea tem corpo extenso, ainda contamos.
            # (Mantém comportamento da skill: alíneas em prosa que ultrapassam 7 linhas
            # também são problema.)
            pass

        n_linhas = estimar_linhas(p)
        if n_linhas >= 8:
            longos.append(
                ParagrafoLongo(
                    secao=secao_nome,
                    indice=idx,
                    n_linhas=n_linhas,
                    n_chars=len(p),
                    preview=p[:150],
                )
            )

    return longos


def audit_sections(sections: dict) -> AuditorResult:
    """Aplica IRR-1 e IRR-2 sobre o dict de seções do parecer.

    `sections` é o resultado de `parse_parecer_xml` ou estrutura equivalente, com chaves
    `ementa`, `relatorio`, `fundamentos`, `conclusao` (strings).

    O gate aprova quando ambas as regras passam. Em caso de reprovação, o
    `AuditorResult.paragrafos_longos` lista exatamente quais parágrafos precisam ser
    quebrados (insumo para `revise_parecer`).
    """
    violacoes: list[str] = []
    paragrafos_longos: list[ParagrafoLongo] = []

    # IRR-1 — Ementa em maiúsculas
    ementa_ok, v_ementa = _auditar_ementa(sections.get("ementa", "") or "")
    violacoes.extend(v_ementa)

    # IRR-2 — Parágrafos longos (foco em fundamentos, mas confere todas as seções)
    for secao in ("relatorio", "fundamentos", "conclusao"):
        paragrafos_longos.extend(
            _auditar_secao_paragrafos(secao, sections.get(secao, "") or "")
        )

    if paragrafos_longos:
        violacoes.append(
            f"REGRA IRR-2 VIOLADA: {len(paragrafos_longos)} parágrafo(s) com 8+ linhas (limite: 7)"
        )

    passed = ementa_ok is True and not paragrafos_longos

    return AuditorResult(
        passed=passed,
        violacoes=violacoes,
        paragrafos_longos=paragrafos_longos,
        ementa_ok=ementa_ok,
    )


def format_revision_instructions(result: AuditorResult) -> str:
    """Formata as violações para passar como `observacoes` ao P3 (revise_parecer).

    Estratégia: produzir um briefing curto e acionável, com os parágrafos exatos a quebrar
    e a regra violada. O P3 já foi instruído (Camada 1) a quebrar parágrafos longos mesmo
    sem pedido explícito.
    """
    linhas: list[str] = []
    linhas.append("O auditor mecânico identificou violações às regras invioláveis do escritório.")
    linhas.append("Reescreva as seções afetadas corrigindo os problemas abaixo:")
    linhas.append("")

    if result.ementa_ok is False:
        linhas.append("- IRR-1 — A ementa contém minúsculas indevidas. Reescreva-a integralmente em MAIÚSCULAS, "
                      "preservando apenas indicadores ordinais (º, °, ª) e letras de alíneas entre aspas.")

    if result.paragrafos_longos:
        linhas.append(
            f"- IRR-2 — {len(result.paragrafos_longos)} parágrafo(s) com 8+ linhas estimadas. "
            "Quebre cada um em parágrafos menores (≤ 7 linhas), costurados por conectivos de transição."
        )
        linhas.append("")
        linhas.append("## TRECHOS MARCADOS PARA CORREÇÃO")
        for i, p in enumerate(result.paragrafos_longos[:10], start=1):
            linhas.append(
                f'{i}. (seção {p.secao}, ~{p.n_linhas} linhas, {p.n_chars} chars) '
                f'"{p.preview}..."'
            )
        if len(result.paragrafos_longos) > 10:
            linhas.append(f"... e mais {len(result.paragrafos_longos) - 10} parágrafo(s) longo(s).")

    return "\n".join(linhas)


def affected_sections(result: AuditorResult) -> list[str]:
    """Retorna as seções (subset de {ementa, relatorio, fundamentos, conclusao}) que
    precisam ser reescritas para resolver o gate. Útil como argumento para revise_parecer.
    """
    secoes: set[str] = set()
    if result.ementa_ok is False:
        secoes.add("ementa")
    for p in result.paragrafos_longos:
        secoes.add(p.secao)
    return sorted(secoes) or ["fundamentos"]  # fallback defensivo
