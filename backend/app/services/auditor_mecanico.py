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

REGRA IRR-3 — em modo quase-processual (impugnação, recurso, contrarrazões), nenhum
  marcador residual sobre norma da parte adversa pode permanecer no texto final. A
  IA recebe a IRR-3 no P2 para confirmar normas via web_search e converter achados
  em parágrafo dedicado. Marcador residual reprova o gate (override Dr. Ione, checklist
  v2.4 — Dimensão E.7).
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

# IRR-3 — marcadores residuais sobre norma da parte adversa. Em modo quase-processual,
# o P2 deve confirmar a norma adversa via web_search e converter o achado em parágrafo
# dedicado. Marcador remanescente no texto final reprova o gate.
#
# Dois padrões: (a) qualquer [VERIFICAR ...] ou [!VERIFICAR: ... !] cru; (b) [REVISAR — ...]
# que mencione explicitamente a parte adversa (recorrente, impugnante, contrarrazões,
# notificação adversa, parte adversa, "INVOCADA PELA PARTE").
_VERIFICAR_PATTERN = re.compile(r"\[\s*!?\s*VERIFICAR\b[^\]]*\]?", re.IGNORECASE)
_REVISAR_ADVERSA_PATTERN = re.compile(
    r"\[\s*REVISAR\s+[—\-–][^\]]*?"
    r"(?:PARTE\s+ADVERSA|INVOCADA\s+PELA\s+PARTE|RECORRENTE|IMPUGNANTE|"
    r"CONTRARRAZ[ÕOÕÕ]ES|NOTIFICA[ÇCÇ][AÃÃ]O\s+ADVERSA|"
    r"INVOCADA\s+(?:POR|PELO|PELA)\s+(?:RECORRENTE|IMPUGNANTE|LICITANTE))"
    r"[^\]]*\]",
    re.IGNORECASE,
)

# CITAÇÃO LITERAL DE ARTIGO DE LEI (item 3.3 — Opção B). Transcrever o TEXTO de um
# artigo entre aspas ou em recuo `>` é proibido: o modelo reproduz de memória e fabrica
# a redação (ex.: "art. 107 da Lei 14.133" com texto que NÃO é o da lei — aparência de
# transcrição fiel que engana o revisor). Padrão = paráfrase; se a redação exata importa,
# marcador [REVISAR]. NÃO afeta citação de JURISPRUDÊNCIA em recuo (começa com o texto do
# julgado/ementa, não com "Art. N") nem referência inline curta ("nos termos do art. 107").
# (a) Recuo `>` iniciado por "Art. N"/"Artigo N".
_ART_INICIO_PATTERN = re.compile(r"^[\"'“‘\s]*(?:Art\.?|Artigo)\s*\d+", re.IGNORECASE)
# (b) Aspas envolvendo transcrição de artigo com corpo substancial (≥ 60 chars).
_ASPAS_ARTIGO_PATTERN = re.compile(
    r"[\"“]\s*(?:Art\.?|Artigo)\s*\d+[^\"”]{60,}[\"”]",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class ParagrafoLongo:
    secao: str          # "fundamentos" | "relatorio" | "conclusao"
    indice: int          # posição do parágrafo dentro da seção (0-based)
    n_linhas: int        # linhas estimadas
    n_chars: int         # caracteres
    preview: str         # primeiros 150 chars


@dataclass
class MarcadorResidual:
    secao: str          # "ementa" | "relatorio" | "fundamentos" | "conclusao"
    marcador: str        # texto completo do marcador encontrado
    tipo: str            # "verificar" | "revisar_adversa"


@dataclass
class CitacaoLiteralLei:
    secao: str          # "relatorio" | "fundamentos" | "conclusao"
    trecho: str          # preview do trecho ofensor (até 150 chars)


@dataclass
class AuditorResult:
    passed: bool
    violacoes: list[str] = field(default_factory=list)
    paragrafos_longos: list[ParagrafoLongo] = field(default_factory=list)
    ementa_ok: bool | None = None
    marcadores_residuais: list[MarcadorResidual] = field(default_factory=list)
    citacoes_literais: list[CitacaoLiteralLei] = field(default_factory=list)

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
            "marcadores_residuais": [
                {"secao": m.secao, "marcador": m.marcador, "tipo": m.tipo}
                for m in self.marcadores_residuais
            ],
            "citacoes_literais": [
                {"secao": c.secao, "trecho": c.trecho} for c in self.citacoes_literais
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


def _detectar_marcadores_residuais(
    secao_nome: str, texto: str
) -> list[MarcadorResidual]:
    """IRR-3 — marcadores residuais sobre norma da parte adversa.

    Detecta:
      - [VERIFICAR ...] ou [!VERIFICAR: ... !] — sempre proibidos em texto final
        (o P2 deve resolvê-los antes do fechamento).
      - [REVISAR — ...] que mencione recorrente, impugnante, contrarrazões,
        parte adversa, "INVOCADA PELA PARTE", etc.

    Marcadores `[REVISAR — ...]` neutros (acórdão a confirmar, valor de dispensa,
    decreto a publicar) NÃO entram aqui — eles continuam admissíveis e são tratados
    pelo painel de revisão humana do editor.
    """
    if not texto:
        return []

    achados: list[MarcadorResidual] = []
    for match in _VERIFICAR_PATTERN.finditer(texto):
        achados.append(
            MarcadorResidual(secao=secao_nome, marcador=match.group(0), tipo="verificar")
        )
    for match in _REVISAR_ADVERSA_PATTERN.finditer(texto):
        achados.append(
            MarcadorResidual(
                secao=secao_nome, marcador=match.group(0), tipo="revisar_adversa",
            )
        )
    return achados


def _detectar_citacao_literal_lei(secao_nome: str, texto: str) -> list[CitacaoLiteralLei]:
    """Item 3.3 (Opção B) — transcrição literal do texto de um artigo de lei.

    Detecta blocos que reproduzem o TEXTO de um artigo como se fosse transcrição fiel:
      (a) recuo `>` iniciado por "Art. N"/"Artigo N";
      (b) trecho entre aspas iniciado por "Art. N" com corpo substancial (≥ 60 chars).

    NÃO detecta: referência inline curta ("nos termos do art. 107 da Lei 14.133") nem
    citação de JURISPRUDÊNCIA em recuo (que começa com o texto do julgado, não "Art. N").
    """
    if not texto:
        return []

    achados: list[CitacaoLiteralLei] = []
    vistos: set[str] = set()

    def _add(trecho: str) -> None:
        chave = trecho[:60].lower()
        if chave not in vistos:
            vistos.add(chave)
            achados.append(CitacaoLiteralLei(secao=secao_nome, trecho=trecho[:150]))

    # (a) Blockquote iniciado por "Art. N"
    for linha in texto.split("\n"):
        stripped = linha.lstrip()
        if stripped.startswith(">"):
            conteudo = stripped.lstrip(">").strip()
            if _ART_INICIO_PATTERN.match(conteudo):
                _add(conteudo)

    # (b) Aspas envolvendo transcrição de artigo
    for match in _ASPAS_ARTIGO_PATTERN.finditer(texto):
        _add(match.group(0))

    return achados


def audit_sections(sections: dict, modo: str | None = None) -> AuditorResult:
    """Aplica IRR-1, IRR-2 e (em modo quase-processual) IRR-3 sobre o dict de seções.

    `sections` é o resultado de `parse_parecer_xml` ou estrutura equivalente, com chaves
    `ementa`, `relatorio`, `fundamentos`, `conclusao` (strings).

    `modo` vem da classificação P1 (`consultivo_puro` ou `quase_processual`). Em modo
    quase-processual, marcadores residuais sobre norma da parte adversa reprovam o gate.

    O gate aprova quando todas as regras aplicáveis passam. Em caso de reprovação, os
    campos `paragrafos_longos` e `marcadores_residuais` listam o que precisa ser
    corrigido pelo P3.
    """
    violacoes: list[str] = []
    paragrafos_longos: list[ParagrafoLongo] = []
    marcadores_residuais: list[MarcadorResidual] = []

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

    # IRR-3 — Marcadores residuais sobre norma da parte adversa (só em quase-processual)
    if modo == "quase_processual":
        for secao in ("ementa", "relatorio", "fundamentos", "conclusao"):
            marcadores_residuais.extend(
                _detectar_marcadores_residuais(secao, sections.get(secao, "") or "")
            )
        if marcadores_residuais:
            violacoes.append(
                f"REGRA IRR-3 VIOLADA: {len(marcadores_residuais)} marcador(es) residual(is) "
                "sobre norma da parte adversa em texto final (modo quase-processual)"
            )

    # Citação literal de artigo de lei (item 3.3 — Opção B). Vale em qualquer modo.
    citacoes_literais: list[CitacaoLiteralLei] = []
    for secao in ("relatorio", "fundamentos", "conclusao"):
        citacoes_literais.extend(
            _detectar_citacao_literal_lei(secao, sections.get(secao, "") or "")
        )
    if citacoes_literais:
        violacoes.append(
            f"CITAÇÃO LITERAL VIOLADA: {len(citacoes_literais)} transcrição(ões) literal(is) "
            "de artigo de lei (aspas/recuo) — devem virar paráfrase ou [REVISAR]"
        )

    passed = (
        ementa_ok is True
        and not paragrafos_longos
        and not marcadores_residuais
        and not citacoes_literais
    )

    return AuditorResult(
        passed=passed,
        violacoes=violacoes,
        paragrafos_longos=paragrafos_longos,
        ementa_ok=ementa_ok,
        marcadores_residuais=marcadores_residuais,
        citacoes_literais=citacoes_literais,
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

    if result.marcadores_residuais:
        linhas.append("")
        linhas.append(
            f"- IRR-3 — {len(result.marcadores_residuais)} marcador(es) residual(is) sobre norma da "
            "parte adversa. Em modo quase-processual, toda norma invocada pela parte adversa "
            "deve ter sido confirmada (existência, vigência, teor) antes do fechamento. "
            "Substitua cada marcador por parágrafo dedicado de 1 a 2 parágrafos, registrando "
            "(a) o achado quanto à norma adversa, (b) a norma efetivamente vigente sobre a matéria, "
            "(c) o impacto sobre o argumento da parte adversa. Nenhum [VERIFICAR] ou [REVISAR — ...PARTE ADVERSA...] "
            "pode permanecer no texto final."
        )
        linhas.append("")
        linhas.append("## MARCADORES A RESOLVER")
        for i, m in enumerate(result.marcadores_residuais[:10], start=1):
            linhas.append(f'{i}. (seção {m.secao}, tipo {m.tipo}) {m.marcador}')
        if len(result.marcadores_residuais) > 10:
            linhas.append(
                f"... e mais {len(result.marcadores_residuais) - 10} marcador(es)."
            )

    if result.citacoes_literais:
        linhas.append("")
        linhas.append(
            f"- CITAÇÃO LITERAL DE LEI — {len(result.citacoes_literais)} trecho(s) reproduzem o "
            "TEXTO de um artigo de lei entre aspas ou em recuo `>`. A redação pode ter sido "
            "reproduzida de memória e não corresponder à lei (erro grave de confiabilidade). "
            "Converta CADA um em PARÁFRASE funcional em prosa, SEM aspas e SEM `>`, no formato "
            '"o art. X estabelece, em síntese, que...". Se a redação literal for indispensável e '
            "você não a confirmou por web_search, substitua por "
            "[REVISAR — TEXTO LITERAL DO ART. X DA LEI Y NÃO CONFIRMADO; CONFERIR REDAÇÃO OFICIAL]. "
            "Esta regra NÃO se aplica a citação de jurisprudência."
        )
        linhas.append("")
        linhas.append("## TRANSCRIÇÕES A CONVERTER EM PARÁFRASE")
        for i, c in enumerate(result.citacoes_literais[:10], start=1):
            linhas.append(f'{i}. (seção {c.secao}) "{c.trecho}..."')
        if len(result.citacoes_literais) > 10:
            linhas.append(
                f"... e mais {len(result.citacoes_literais) - 10} transcrição(ões)."
            )

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
    for m in result.marcadores_residuais:
        secoes.add(m.secao)
    for c in result.citacoes_literais:
        secoes.add(c.secao)
    return sorted(secoes) or ["fundamentos"]  # fallback defensivo
