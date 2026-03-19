from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from sqlalchemy import func, select
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


def _sections_to_tiptap(sections: dict) -> dict:
    """Converte seções do parecer para formato TipTap JSON com formatação rica."""
    section_map = [
        ("EMENTA", sections.get("ementa", "")),
        ("I — RELATÓRIO", sections.get("relatorio", "")),
        ("II — FUNDAMENTOS", sections.get("fundamentos", "")),
        ("III — CONCLUSÃO", sections.get("conclusao", "")),
    ]
    content: list[dict] = []
    for title, text in section_map:
        content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": title}],
        })
        # Dividir por parágrafos (linhas duplas) e parsear cada bloco
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        for block in blocks:
            content.extend(_parse_block(block))

    return {"type": "doc", "content": content}


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
        select(func.count())
        .select_from(ParecerRequest)
        .where(ParecerRequest.numero_parecer.like(f"{prefix}%"))
    )
    count = result.scalar_one()
    return f"{prefix}{count + 1:04d}"


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
    tiptap = _sections_to_tiptap(sections)

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


async def reprocess(
    parecer_request_id: str, observacoes: str, db: AsyncSession
) -> ParecerVersion:
    result = await db.execute(
        select(ParecerRequest).where(ParecerRequest.id == parecer_request_id)
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        raise ValueError(f"ParecerRequest {parecer_request_id} nao encontrado")

    last_version_result = await db.execute(
        select(ParecerVersion)
        .where(ParecerVersion.request_id == pr.id)
        .order_by(ParecerVersion.version_number.desc())
        .limit(1)
    )
    last_version = last_version_result.scalar_one_or_none()
    if last_version is None:
        raise ValueError("Nenhuma versao anterior encontrada para reprocessar")

    # Reconstruir dict de seções da versão atual
    parecer_atual = {
        "ementa": "",
        "relatorio": "",
        "fundamentos": "",
        "conclusao": "",
        "citacoes_verificar": last_version.citacoes_verificar or [],
        "ressalvas": last_version.ressalvas or [],
        "notas_revisor": last_version.notas_revisor or [],
    }

    # Extrair seções do HTML atual via parse do TipTap JSON
    if last_version.content_tiptap:
        tiptap = last_version.content_tiptap
        current_section = None
        text_buffer: list[str] = []
        section_keys = {
            "EMENTA": "ementa",
            "RELATÓRIO": "relatorio",
            "FUNDAMENTOS": "fundamentos",
            "CONCLUSÃO": "conclusao",
        }
        for node in tiptap.get("content", []):
            if node.get("type") == "heading":
                if current_section and text_buffer:
                    parecer_atual[current_section] = "\n\n".join(text_buffer)
                    text_buffer = []
                title = "".join(
                    c.get("text", "") for c in node.get("content", [])
                )
                current_section = section_keys.get(title)
            elif node.get("type") == "paragraph" and current_section:
                text = "".join(c.get("text", "") for c in node.get("content", []))
                if text:
                    text_buffer.append(text)
        if current_section and text_buffer:
            parecer_atual[current_section] = "\n\n".join(text_buffer)

    # P3 — Revisar com observações
    secoes = ["ementa", "relatorio", "fundamentos", "conclusao"]
    revisao = await revise_parecer(parecer_atual, observacoes, secoes)

    # Merge: substituir apenas seções alteradas
    secoes_alteradas = revisao.get("secoes_alteradas", [])
    if isinstance(secoes_alteradas, str):
        secoes_alteradas = [s.strip() for s in secoes_alteradas.split(",") if s.strip()]

    for secao in secoes_alteradas:
        if secao in revisao:
            parecer_atual[secao] = revisao[secao]

    # Acumular notas e citações
    novas_notas = revisao.get("notas_revisor") or []
    if isinstance(novas_notas, str):
        novas_notas = [novas_notas] if novas_notas else []
    novas_citacoes = revisao.get("citacoes_verificar") or []

    parecer_atual["notas_revisor"] = (parecer_atual.get("notas_revisor") or []) + novas_notas
    parecer_atual["citacoes_verificar"] = (parecer_atual.get("citacoes_verificar") or []) + novas_citacoes

    # Re-renderizar HTML e TipTap
    classification = pr.classificacao or {}
    metadata = _build_metadata(pr, classification)
    parecer_dict = {**parecer_atual, "metadata": metadata}
    html = render_parecer_html(parecer_dict)
    tiptap = _sections_to_tiptap(parecer_atual)

    next_version_num = last_version.version_number + 1

    version = ParecerVersion(
        request_id=pr.id,
        version_number=next_version_num,
        source=VersionSource.ia_reprocessado,
        content_tiptap=tiptap,
        content_html=html,
        reprocess_instructions=observacoes,
        prompt_version=get_prompt_version(),
        citacoes_verificar=parecer_atual.get("citacoes_verificar") or [],
        ressalvas=parecer_atual.get("ressalvas") or [],
        notas_revisor=parecer_atual.get("notas_revisor") or [],
    )
    db.add(version)

    old_status = pr.status
    pr.status = ParecerStatus.gerado
    pr.revisoes = (pr.revisoes or 0) + 1

    db.add(
        ParecerStatusHistory(
            request_id=pr.id,
            from_status=old_status,
            to_status=ParecerStatus.gerado,
            notes=f"Minuta v{next_version_num} revisada por IA (P3, revisao #{pr.revisoes})",
        )
    )

    await db.commit()
    await db.refresh(version)

    return version
