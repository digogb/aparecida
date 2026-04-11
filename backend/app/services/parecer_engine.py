from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.parecer import (
    ParecerRequest,
    ParecerStatus,
    ParecerStatusHistory,
    ParecerVersion,
    VersionSource,
)
from app.services.parecer_ai_service import classify_email, generate_parecer, revise_parecer
from app.services.parecer_html_service import render_parecer_html, parse_parecer_xml
from app.services.prompt_service import get_prompt_version

logger = logging.getLogger(__name__)


# ─── TipTap JSON builder com formatação rica ───

def _parse_inline_marks(text: str) -> list[dict]:
    """Converte **negrito** em marks do TipTap."""
    nodes: list[dict] = []
    parts = re.split(r"(\*\*.+?\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            nodes.append({
                "type": "text",
                "text": part[2:-2],
                "marks": [{"type": "bold"}],
            })
        else:
            nodes.append({"type": "text", "text": part})
    return nodes if nodes else [{"type": "text", "text": text}]


def _parse_block(text: str) -> list[dict]:
    """
    Parseia um bloco de texto (separado por \\n\\n) em nodes TipTap.
    Reconhece:
    - > blockquote (linhas começando com >)
    - Subtítulos numerados (ex: "1. Da Legislação", "3.2. Do Objeto")
    - Alíneas (a), b), c))
    - Parágrafos normais com **negrito**
    """
    lines = text.strip().split("\n")
    nodes: list[dict] = []

    # Detectar blockquote (todas as linhas começam com >)
    bq_lines = []
    normal_lines = []
    in_blockquote = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(">"):
            if normal_lines:
                nodes.extend(_flush_normal_lines(normal_lines))
                normal_lines = []
            bq_lines.append(stripped[1:].strip())
            in_blockquote = True
        else:
            if bq_lines:
                nodes.append(_make_blockquote(bq_lines))
                bq_lines = []
                in_blockquote = False
            if stripped:
                normal_lines.append(stripped)

    if bq_lines:
        nodes.append(_make_blockquote(bq_lines))
    if normal_lines:
        nodes.extend(_flush_normal_lines(normal_lines))

    return nodes


def _flush_normal_lines(lines: list[str]) -> list[dict]:
    """Converte linhas normais acumuladas em nodes TipTap."""
    text = " ".join(lines)
    nodes: list[dict] = []

    # Subtítulo numerado (ex: "1. Da Legislação", "3.2. Do Objeto")
    if re.match(r"^\d+(\.\d+)*\.?\s+[A-Z]", text):
        nodes.append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": _parse_inline_marks(text),
        })
    # Alínea (a), b), etc.)
    elif re.match(r"^[a-z]\)", text):
        nodes.append({
            "type": "paragraph",
            "content": _parse_inline_marks(text),
        })
    else:
        nodes.append({
            "type": "paragraph",
            "content": _parse_inline_marks(text),
        })

    lines.clear()
    return nodes


def _make_blockquote(lines: list[str]) -> dict:
    """Cria um node blockquote TipTap a partir de linhas."""
    paragraphs: list[dict] = []
    current: list[str] = []

    for line in lines:
        if not line:
            if current:
                text = " ".join(current)
                paragraphs.append({
                    "type": "paragraph",
                    "content": _parse_inline_marks(text),
                })
                current = []
        else:
            current.append(line)

    if current:
        text = " ".join(current)
        paragraphs.append({
            "type": "paragraph",
            "content": _parse_inline_marks(text),
        })

    return {
        "type": "blockquote",
        "content": paragraphs or [{"type": "paragraph", "content": [{"type": "text", "text": ""}]}],
    }


_ADVOGADOS = [
    ("Francisco Ione Pereira Lima", "OAB/CE 4.585"),
    ("Matheus Nogueira Pereira Lima", "OAB/CE 31.251"),
    ("Flavio Henrique Luna Silva", "OAB/CE 31.252"),
    ("Valéria Matias de Alencar", "OAB/CE 36.666"),
]

_MESES = [
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]

# Nomes dos advogados usados para detectar bloco de assinatura duplicado
_NOMES_ADVOGADOS = [nome for nome, _ in _ADVOGADOS]


def _strip_signature_block(text: str) -> str:
    """Remove bloco de assinaturas/data duplicado do final do texto da conclusão.

    A IA às vezes inclui local/data e nomes dos advogados no corpo da conclusão,
    mas o código já adiciona essas informações separadamente. Esta função detecta
    e remove o bloco duplicado.
    """
    import re as _re

    lines = text.rstrip().split("\n")
    # Procurar de baixo para cima: encontrar a primeira linha que NÃO seja
    # assinatura, data/local, ou linha em branco
    cut_index = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if not stripped:
            continue
        # Linha com nome de advogado + OAB
        if any(nome in stripped for nome in _NOMES_ADVOGADOS):
            cut_index = i
            continue
        # Linha de data/local (ex: "Potengi/CE, 22 de março de 2026.")
        if _re.match(r'^[\w\s]+/[A-Z]{2},\s+\d+\s+de\s+\w+\s+de\s+\d{4}', stripped):
            cut_index = i
            continue
        # Linha com apenas traços (separador)
        if _re.match(r'^[-—–]+$', stripped):
            cut_index = i
            continue
        break

    if cut_index < len(lines):
        text = "\n".join(lines[:cut_index]).rstrip()

    return text


def _sections_to_tiptap(sections: dict, metadata: dict | None = None) -> dict:
    """Converte seções do parecer para formato TipTap JSON com formatação rica."""
    conclusao = _strip_signature_block(sections.get("conclusao", ""))
    section_map = [
        ("EMENTA", sections.get("ementa", "")),
        ("I — RELATÓRIO", sections.get("relatorio", "")),
        ("II — FUNDAMENTOS", sections.get("fundamentos", "")),
        ("III — CONCLUSÃO", conclusao),
    ]
    content: list[dict] = []
    for title, text in section_map:
        content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": title}],
        })
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        for block in blocks:
            content.extend(_parse_block(block))

    return {"type": "doc", "content": content}


def _build_merged_tiptap(
    sections: dict,
    original_nodes: dict[str, list[dict]],
    secoes_alteradas: list[str],
) -> dict:
    """Constrói TipTap mesclando nodes originais (seções inalteradas) com
    reconstrução formatada (seções alteradas pela IA)."""
    import copy

    section_map = [
        ("EMENTA", "ementa"),
        ("I — RELATÓRIO", "relatorio"),
        ("II — FUNDAMENTOS", "fundamentos"),
        ("III — CONCLUSÃO", "conclusao"),
    ]
    content: list[dict] = []
    for title, key in section_map:
        content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": title}],
        })

        if key in secoes_alteradas:
            # Seção alterada: reconstruir do texto da IA
            text = sections.get(key, "")
            if key == "conclusao":
                text = _strip_signature_block(text)
            blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
            for block in blocks:
                content.extend(_parse_block(block))
        else:
            # Seção inalterada: preservar nodes TipTap originais
            orig = original_nodes.get(key, [])
            if orig:
                content.extend(copy.deepcopy(orig))
            else:
                text = sections.get(key, "")
                blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
                for block in blocks:
                    content.extend(_parse_block(block))

    return {"type": "doc", "content": content}


def _extract_text_from_node(node: dict) -> str:
    """Extrai texto de qualquer node TipTap recursivamente, preservando
    formatação markdown (bold, blockquotes, subtítulos)."""
    ntype = node.get("type", "")

    if ntype == "text":
        text = node.get("text", "")
        marks = node.get("marks", [])
        has_bold = any(m.get("type") == "bold" for m in marks)
        if has_bold and text.strip():
            return f"**{text}**"
        return text

    parts = []
    for child in node.get("content", []):
        parts.append(_extract_text_from_node(child))
    inner = "".join(parts)

    if ntype == "blockquote":
        # Prefixar cada linha com >
        lines = inner.split("\n")
        return "\n".join(f"> {line}" for line in lines)

    if ntype == "heading":
        level = node.get("attrs", {}).get("level", 3)
        if level == 3:
            # Subtítulo numerado — manter como está
            return inner

    return inner


def _build_metadata(pr: ParecerRequest, classification: dict) -> dict:
    """Monta o dict de metadata para render_parecer_html."""
    municipio = classification.get("municipio", "")
    uf = classification.get("uf", "CE")
    municipio_uf = f"{municipio}/{uf}" if municipio else "[Município/UF]"
    return {
        "orgao_consulente": classification.get("orgao_consulente", pr.sender_email or ""),
        "municipio_uf": municipio_uf,
        "assunto": classification.get("assunto_resumido", pr.subject or ""),
        "referencia": pr.numero_parecer or "",
        "data_elaboracao": datetime.now(timezone.utc).date().isoformat(),
    }


async def _next_numero_sequencial(db: AsyncSession) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"PAR-{year}-"
    result = await db.execute(
        select(func.max(cast(func.substr(ParecerRequest.numero_parecer, len(prefix) + 1), Integer)))
        .where(ParecerRequest.numero_parecer.like(f"{prefix}%"))
    )
    max_num = result.scalar_one() or 0
    return f"{prefix}{max_num + 1:04d}"


async def generate(parecer_request_id: str, db: AsyncSession) -> ParecerVersion:
    result = await db.execute(
        select(ParecerRequest)
        .where(ParecerRequest.id == parecer_request_id)
        .options(selectinload(ParecerRequest.attachments))
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        raise ValueError(f"ParecerRequest {parecer_request_id} nao encontrado")

    if not pr.extracted_text:
        raise ValueError("ParecerRequest sem texto extraido para gerar parecer")

    # Usa classificação P1 existente ou classifica agora
    classification = pr.classificacao
    if not classification:
        attachment_texts = [a.extracted_text for a in pr.attachments if a.extracted_text]
        classification = await classify_email(pr.extracted_text, attachment_texts)
        pr.classificacao = classification

    # Coleta textos dos anexos
    attachment_texts = [a.extracted_text for a in pr.attachments if a.extracted_text]

    # P2 — Gerar parecer
    sections = await generate_parecer(classification, attachment_texts, pr.extracted_text)

    # Renderizar HTML profissional (P4)
    metadata = _build_metadata(pr, classification)
    parecer_dict = {**sections, "metadata": metadata}
    html = render_parecer_html(parecer_dict)
    tiptap = _sections_to_tiptap(sections, metadata)

    # Próximo número de versão
    version_result = await db.execute(
        select(func.coalesce(func.max(ParecerVersion.version_number), 0))
        .where(ParecerVersion.request_id == pr.id)
    )
    next_version = version_result.scalar_one() + 1

    version = ParecerVersion(
        request_id=pr.id,
        version_number=next_version,
        source=VersionSource.ia_gerado,
        content_tiptap=tiptap,
        content_html=html,
        prompt_version=get_prompt_version(),
        citacoes_verificar=sections.get("citacoes_verificar") or [],
        ressalvas=sections.get("ressalvas") or [],
        notas_revisor=[],
    )
    db.add(version)

    if not pr.numero_parecer:
        pr.numero_parecer = await _next_numero_sequencial(db)

    old_status = pr.status
    pr.status = ParecerStatus.gerado

    db.add(
        ParecerStatusHistory(
            request_id=pr.id,
            from_status=old_status,
            to_status=ParecerStatus.gerado,
            notes=f"Minuta v{next_version} gerada por IA (pipeline v{get_prompt_version()})",
        )
    )

    await db.commit()
    await db.refresh(version)

    from app.services.event_dispatcher import dispatch_parecer_event
    await dispatch_parecer_event(str(pr.id), db)

    return version


_SECTION_KEYS = {
    "EMENTA": "ementa",
    "I \u2014 RELATÓRIO": "relatorio",
    "II \u2014 FUNDAMENTOS": "fundamentos",
    "III \u2014 CONCLUSÃO": "conclusao",
}

_MAIN_SECTIONS = ["ementa", "relatorio", "fundamentos", "conclusao"]


def _extract_sections_from_tiptap(tiptap: dict) -> dict[str, str]:
    sections: dict[str, str] = {s: "" for s in _MAIN_SECTIONS}
    current_section = None
    text_buffer: list[str] = []
    for node in tiptap.get("content", []):
        if node.get("type") == "heading":
            if current_section and text_buffer:
                sections[current_section] = "\n\n".join(text_buffer)
                text_buffer = []
            title = "".join(c.get("text", "") for c in node.get("content", []))
            current_section = _SECTION_KEYS.get(title)
        elif current_section:
            text = _extract_text_from_node(node)
            if text:
                text_buffer.append(text)
    if current_section and text_buffer:
        sections[current_section] = "\n\n".join(text_buffer)
    return sections


def _extract_sections_as_nodes(tiptap: dict) -> dict[str, list[dict]]:
    """Extrai os nodes TipTap originais agrupados por seção (preserva formatação)."""
    sections: dict[str, list[dict]] = {s: [] for s in _MAIN_SECTIONS}
    current_section = None
    for node in tiptap.get("content", []):
        if node.get("type") == "heading":
            title = "".join(c.get("text", "") for c in node.get("content", []))
            matched = _SECTION_KEYS.get(title)
            if matched is not None:
                current_section = matched
                continue
        if current_section:
            sections[current_section].append(node)
    return sections


async def _load_current_sections(
    pr: ParecerRequest, db: AsyncSession,
) -> tuple[dict[str, str], dict[str, list[dict]], ParecerVersion]:
    """Carrega seções texto + nodes TipTap originais da melhor versão disponível."""
    all_versions_result = await db.execute(
        select(ParecerVersion)
        .where(ParecerVersion.request_id == pr.id)
        .order_by(ParecerVersion.version_number.desc())
    )
    all_versions = list(all_versions_result.scalars().all())
    if not all_versions:
        raise ValueError("Nenhuma versao anterior encontrada para reprocessar")

    last_version = all_versions[0]

    parecer_atual: dict[str, str] = {}
    original_nodes: dict[str, list[dict]] = {}
    for version in all_versions:
        if not version.content_tiptap:
            continue
        extracted = _extract_sections_from_tiptap(version.content_tiptap)
        if all(extracted.get(s) for s in _MAIN_SECTIONS):
            parecer_atual = extracted
            original_nodes = _extract_sections_as_nodes(version.content_tiptap)
            break

    if not parecer_atual:
        parecer_atual = _extract_sections_from_tiptap(last_version.content_tiptap or {})
        original_nodes = _extract_sections_as_nodes(last_version.content_tiptap or {})

    return parecer_atual, original_nodes, last_version


async def preview_correction(
    parecer_request_id: str, observacoes: str, db: AsyncSession,
) -> dict:
    """Chama P3 e retorna preview das correções sem salvar.

    Retorna:
        {
            "secoes_alteradas": ["fundamentos", "conclusao"],
            "original": {"ementa": "...", "relatorio": "...", ...},
            "revisado": {"fundamentos": "...", "conclusao": "..."},
            "notas_revisor": [...],
            "citacoes_verificar": [...],
        }
    """
    result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == parecer_request_id)
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        raise ValueError(f"ParecerRequest {parecer_request_id} nao encontrado")

    parecer_atual, _, last_version = await _load_current_sections(pr, db)

    parecer_atual.update({
        "citacoes_verificar": last_version.citacoes_verificar or [],
        "ressalvas": last_version.ressalvas or [],
        "notas_revisor": last_version.notas_revisor or [],
    })

    revisao = await revise_parecer(parecer_atual, observacoes, _MAIN_SECTIONS)

    secoes_alteradas = revisao.get("secoes_alteradas", [])
    if isinstance(secoes_alteradas, str):
        secoes_alteradas = [s.strip() for s in secoes_alteradas.split(",") if s.strip()]

    # Montar dict de seções revisadas (só as que mudaram)
    revisado: dict[str, str] = {}
    for secao in secoes_alteradas:
        if secao in revisao:
            revisado[secao] = revisao[secao]

    novas_notas = revisao.get("notas_revisor") or []
    if isinstance(novas_notas, str):
        novas_notas = [novas_notas] if novas_notas else []

    # Extrair trechos_revisados da resposta da IA
    trechos = revisao.get("trechos_revisados") or []
    if isinstance(trechos, str):
        trechos = []

    return {
        "secoes_alteradas": secoes_alteradas,
        "revisado": revisado,
        "trechos": trechos,
        "notas_revisor": novas_notas,
        "citacoes_verificar": revisao.get("citacoes_verificar") or [],
    }


async def apply_correction(
    parecer_request_id: str,
    secoes_aprovadas: dict[str, str],
    observacoes: str,
    notas_revisor: list[str],
    citacoes_verificar: list,
    db: AsyncSession,
) -> ParecerVersion:
    """Aplica apenas as seções aprovadas pelo advogado e cria nova versão."""
    result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == parecer_request_id)
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        raise ValueError(f"ParecerRequest {parecer_request_id} nao encontrado")

    parecer_atual, original_nodes, last_version = await _load_current_sections(pr, db)

    # Mesclar: seções aprovadas substituem as originais
    for secao, texto in secoes_aprovadas.items():
        if secao in _MAIN_SECTIONS:
            parecer_atual[secao] = texto

    # Acumular notas/citações
    all_notas = (last_version.notas_revisor or []) + notas_revisor
    all_citacoes = (last_version.citacoes_verificar or []) + citacoes_verificar

    # Renderizar
    classification = pr.classificacao or {}
    metadata = _build_metadata(pr, classification)
    parecer_dict = {**parecer_atual, "metadata": metadata}
    html = render_parecer_html(parecer_dict)

    # TipTap: preservar nodes originais para seções NÃO aprovadas,
    # reconstruir apenas as aprovadas
    secoes_alteradas = list(secoes_aprovadas.keys())
    tiptap = _build_merged_tiptap(parecer_atual, original_nodes, secoes_alteradas)

    next_version_num = last_version.version_number + 1

    version = ParecerVersion(
        request_id=pr.id,
        version_number=next_version_num,
        source=VersionSource.ia_reprocessado,
        content_tiptap=tiptap,
        content_html=html,
        reprocess_instructions=observacoes,
        prompt_version=get_prompt_version(),
        citacoes_verificar=all_citacoes,
        ressalvas=last_version.ressalvas or [],
        notas_revisor=all_notas,
    )
    db.add(version)

    old_status = pr.status
    pr.status = ParecerStatus.em_correcao
    pr.revisoes = (pr.revisoes or 0) + 1

    db.add(
        ParecerStatusHistory(
            request_id=pr.id,
            from_status=old_status,
            to_status=ParecerStatus.em_correcao,
            notes=f"Minuta v{next_version_num} revisada por IA — {len(secoes_aprovadas)} seção(ões) aprovada(s)",
        )
    )

    await db.commit()
    await db.refresh(version)

    return version
