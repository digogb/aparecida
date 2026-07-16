"""
Leis municipais como referência nos pareceres.

As leis locais de cada município ficam em `backend/leis_municipios/<MUNICIPIO>/*.md`
(um arquivo por lei). Esta camada:

1. **Índice (sempre):** lista título + ementa de TODAS as leis do município da
   consulta — barato, e dá à IA a ciência do que existe localmente.
2. **Texto integral (relevante por tema):** inclui o corpo completo apenas da(s)
   lei(s) cujo título/ementa casa com o assunto/subtipo da consulta (ex.: consulta
   sobre servidor → Estatuto dos Servidores), respeitando um orçamento de chars.

Decisão de design (jun/2026, aprovada pelo usuário): "índice sempre + lei
relevante por tema" — porque o acervo de um município (Salitre ~120k chars)
estoura sozinho o orçamento do P2. Ver prompt_service._MAX_P2_CONTEXT_CHARS.

O bloco montado é apendado ao system prompt do P2/P3 em parecer_ai_service —
fora do `lru_cache` de assemble_p2_context (que não conhece município).
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

# backend/leis_municipios — mesmo nível de PROMPTS_DIR/SKILLS_DIR.
LEIS_DIR = Path(__file__).parent.parent.parent / "leis_municipios"

# Orçamento padrão de texto integral por parecer (chars). O índice não conta —
# é curto. Um estatuto sozinho tem ~66k chars; com `force_top_match` a lei nº1
# entra mesmo excedendo isto (ver assemble_municipal_context).
DEFAULT_FULL_TEXT_BUDGET = 60_000

# Pontuação mínima de relevância para incluir o texto integral de uma lei.
_SCORE_THRESHOLD = 2


def _strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )


def _norm(s: str) -> str:
    """Normaliza para casamento: sem acento, minúsculo, só alfanumérico+espaço."""
    s = _strip_accents(s or "").lower()
    return re.sub(r"[^a-z0-9\s]", " ", s)


# Stopwords PT que não ajudam no casamento de tema.
_STOPWORDS = frozenset(
    """de da do das dos a o e os as no na nos nas para por com sem que dispoe sobre
    municipio municipal lei n nº numero outras providencias estado ceara poder
    publico publicos publica art artigo""".split()
)

# Expansão de sinônimos: o subtipo da classificação nem sempre casa literalmente
# com o título da lei (ex.: subtipo "previdenciario" × lei "RPPS"). Cada token de
# consulta é expandido com os equivalentes para melhorar o recall.
_SYNONYMS: dict[str, tuple[str, ...]] = {
    "servidor": ("estatuto", "servidores", "regime", "juridico"),
    "servidores": ("estatuto", "servidor", "regime", "juridico"),
    "concurso": ("estatuto", "servidores", "provimento", "cargo"),
    "previdenciario": ("rpps", "previdencia", "aposentadoria", "previdenciario"),
    "previdencia": ("rpps", "aposentadoria", "previdenciario"),
    "aposentadoria": ("rpps", "previdencia"),
    "temporario": ("temporarios", "seletivo", "excepcional", "determinado"),
    "temporarios": ("temporario", "seletivo", "excepcional", "determinado"),
    "magisterio": ("professor", "professores", "educacao", "carreira", "carreiras"),
    "professor": ("magisterio", "educacao"),
    "educacao": ("magisterio", "professor"),
    "cargo": ("cargos", "carreira", "carreiras", "provimento"),
}


def _tokens(text: str) -> list[str]:
    return [t for t in _norm(text).split() if len(t) > 2 and t not in _STOPWORDS]


@dataclass(frozen=True)
class LeiMunicipal:
    filename: str
    title: str
    ementa: str
    body: str

    @property
    def index_line(self) -> str:
        ementa = self.ementa.strip()
        if len(ementa) > 220:
            ementa = ementa[:217].rstrip() + "..."
        return f"- **{self.title}**" + (f" — {ementa}" if ementa else "")


def _municipio_folder(municipio: str) -> Path | None:
    """Resolve o nome do município (ex.: 'Salitre') para a pasta (ex.: SALITRE),
    tolerando acento/caixa."""
    if not municipio or not LEIS_DIR.is_dir():
        return None
    alvo = _norm(municipio).strip()
    if not alvo:
        return None
    for child in LEIS_DIR.iterdir():
        if child.is_dir() and _norm(child.name).strip() == alvo:
            return child
    return None


_RE_HEADING = re.compile(r"^#\s+(.*)$", re.MULTILINE)
_RE_EMENTA = re.compile(r"\**EMENTA\:?\**\s*[:\-]?\s*(.+)", re.IGNORECASE)


def _parse_lei(path: Path) -> LeiMunicipal | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Falha ao ler lei municipal %s: %s", path, exc)
        return None
    if not raw.strip():
        return None

    # Título: primeiro heading '# ...' que não seja só o número do arquivo; senão
    # o nome do arquivo sem extensão.
    title = path.stem
    for m in _RE_HEADING.finditer(raw):
        cand = m.group(1).strip()
        # pula headings de paginação tipo "PAGE 1" ou rótulos de seção
        if cand and not re.fullmatch(r"(?i)page\s*\d+|---.*", cand):
            title = cand
            break
    title = re.sub(r"^\d+\s*-\s*", "", title).strip()

    # Ementa: linha com "EMENTA:" se houver; senão primeira frase de conteúdo
    # (pulando headings '#' e a linha '---' — senão a ementa repete o título).
    ementa = ""
    m = _RE_EMENTA.search(raw)
    if m:
        ementa = m.group(1).strip().strip("*").strip()
    else:
        for line in raw.splitlines():
            raw_line = line.strip()
            if not raw_line or raw_line.startswith("#") or raw_line.startswith("---"):
                continue
            s = raw_line.strip("*").strip()
            if len(s) > 30:
                ementa = s
                break

    return LeiMunicipal(filename=path.name, title=title, ementa=ementa, body=raw.strip())


@lru_cache(maxsize=32)
def _load_municipal_laws(folder: str) -> tuple[LeiMunicipal, ...]:
    """Carrega e parseia todas as leis .md de uma pasta de município (cacheado)."""
    p = Path(folder)
    leis: list[LeiMunicipal] = []
    for md in sorted(p.glob("*.md")):
        lei = _parse_lei(md)
        if lei:
            leis.append(lei)
    return tuple(leis)


def _score(lei: LeiMunicipal, query: set[str]) -> int:
    """Pontua a relevância de uma lei pela interseção de tokens entre o tema da
    consulta e o (título + ementa) da lei. Título pesa o dobro."""
    title_tokens = set(_tokens(lei.title))
    ementa_tokens = set(_tokens(lei.ementa))
    score = 0
    for q in query:
        if q in title_tokens:
            score += 2
        elif q in ementa_tokens:
            score += 1
    return score


def _expand(tokens: list[str]) -> set[str]:
    out: set[str] = set()
    for t in tokens:
        out.add(t)
        out.update(_SYNONYMS.get(t, ()))
    return out


def assemble_municipal_context(
    municipio: str,
    subtipo: str = "",
    assunto: str = "",
    full_text_budget: int = DEFAULT_FULL_TEXT_BUDGET,
    force_top_match: bool = True,
) -> str | None:
    """Monta o bloco de leis municipais para apendar ao system prompt.

    Retorna None quando não há leis para o município (ou município desconhecido).
    Sempre inclui o índice; o texto integral entra só das leis relevantes ao tema
    (subtipo + assunto), até o orçamento de chars.

    `force_top_match`: na geração (P2) a lei de maior relevância entra integral
    mesmo que sozinha exceda o orçamento (um estatuto não pode ficar de fora por
    tamanho). Na revisão (P3), `False` — o orçamento é apertado e o parecer já
    traz as citações, então só entram leis que caibam (índice sempre presente).
    """
    folder = _municipio_folder(municipio)
    if folder is None:
        return None
    leis = _load_municipal_laws(str(folder))
    if not leis:
        return None

    municipio_nome = municipio.strip() or folder.name.title()

    # Casa as leis relevantes ao tema da consulta.
    query = _expand(_tokens(f"{subtipo} {assunto}"))
    scored = sorted(
        ((_score(lei, query), lei) for lei in leis),
        key=lambda x: x[0],
        reverse=True,
    )

    # Inclui o texto integral das leis relevantes. A de MAIOR relevância entra
    # sempre (mesmo que sozinha exceda o orçamento — um estatuto tem ~66k chars e
    # excluí-lo por tamanho anularia a escolha "lei relevante por tema"). As
    # demais entram só enquanto couberem no orçamento acumulado.
    chosen: list[LeiMunicipal] = []
    used = 0
    for score, lei in scored:
        if score < _SCORE_THRESHOLD:
            break
        if not chosen and force_top_match:  # top match — entra incondicionalmente
            chosen.append(lei)
            used += len(lei.body)
            continue
        if used + len(lei.body) <= full_text_budget:
            chosen.append(lei)
            used += len(lei.body)

    index = "\n".join(lei.index_line for lei in leis)

    parts = [
        f"## LEIS MUNICIPAIS DE {municipio_nome.upper()}",
        "Leis locais vigentes neste município, disponíveis como referência. "
        "Quando a consulta envolver matéria regida por uma destas leis, "
        "**fundamente com o dispositivo municipal específico** (art./inciso/parágrafo) "
        "no mesmo formato das demais citações legais (citação recuada + paráfrase "
        "funcional). Se a matéria depende de lei municipal que NÃO está listada "
        "abaixo, registre essa ausência em vez de presumir o conteúdo.",
        f"### Índice das leis locais\n{index}",
    ]

    if chosen:
        for lei in chosen:
            parts.append(f"### TEXTO INTEGRAL — {lei.title}\n{lei.body}")
        logger.info(
            "Leis municipais: municipio=%s leis_indexadas=%d texto_integral=%s chars=%d",
            municipio_nome, len(leis), [doc.filename for doc in chosen], used,
        )
    else:
        logger.info(
            "Leis municipais: municipio=%s leis_indexadas=%d (só índice — nenhuma casou tema '%s/%s')",
            municipio_nome, len(leis), subtipo, assunto,
        )

    return "\n\n".join(parts)


def clear_cache() -> None:
    """Limpa o cache de leis carregadas — útil em testes e após editar os .md."""
    _load_municipal_laws.cache_clear()
