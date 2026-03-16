from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

import anthropic
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.parecer import (
    ParecerModelo,
    ParecerRequest,
    ParecerStatus,
    ParecerStatusHistory,
    ParecerVersion,
    VersionSource,
)
from app.prompts.parecer_generico import SYSTEM_PROMPT as PROMPT_GENERICO
from app.prompts.parecer_licitacao import SYSTEM_PROMPT as PROMPT_LICITACAO

logger = logging.getLogger(__name__)

CLAUDE_MODEL = "claude-sonnet-4-20250514"

SECTION_MARKERS = ["EMENTA", "RELATORIO", "FUNDAMENTACAO", "CONCLUSAO"]


def _select_prompt(modelo: ParecerModelo | None) -> str:
    if modelo == ParecerModelo.licitacao:
        return PROMPT_LICITACAO
    return PROMPT_GENERICO


def _parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    pattern = r"\[(" + "|".join(SECTION_MARKERS) + r")\]"
    parts = re.split(pattern, text)

    current_key = None
    for part in parts:
        stripped = part.strip()
        if stripped in SECTION_MARKERS:
            current_key = stripped
        elif current_key:
            sections[current_key] = stripped
            current_key = None

    return sections


def _sections_to_html(sections: dict[str, str]) -> str:
    html_parts: list[str] = []
    for marker in SECTION_MARKERS:
        content = sections.get(marker, "")
        html_parts.append(f"<h2>{marker}</h2>")
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for p in paragraphs:
            html_parts.append(f"<p>{p}</p>")
    return "\n".join(html_parts)


def _sections_to_tiptap(sections: dict[str, str]) -> dict:
    content: list[dict] = []
    for marker in SECTION_MARKERS:
        text = sections.get(marker, "")
        content.append(
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": marker}],
            }
        )
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for p in paragraphs:
            content.append(
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": p}],
                }
            )
    return {"type": "doc", "content": content}


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
        select(ParecerRequest).where(ParecerRequest.id == parecer_request_id)
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        raise ValueError(f"ParecerRequest {parecer_request_id} nao encontrado")

    if not pr.extracted_text:
        raise ValueError("ParecerRequest sem texto extraido para gerar parecer")

    system_prompt = _select_prompt(pr.modelo)

    municipio_info = ""
    if pr.municipio_id:
        from app.models.municipio import Municipio

        mun_result = await db.execute(
            select(Municipio).where(Municipio.id == pr.municipio_id)
        )
        mun = mun_result.scalar_one_or_none()
        if mun:
            municipio_info = f"\nMunicipio consulente: {mun.name} - {mun.state}"

    user_content = (
        f"Consulta juridica recebida por email:\n"
        f"Assunto: {pr.subject or 'N/A'}\n"
        f"Remetente: {pr.sender_email or 'N/A'}"
        f"{municipio_info}\n\n"
        f"Texto da consulta:\n{pr.extracted_text}"
    )

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    raw_text = response.content[0].text
    sections = _parse_sections(raw_text)
    html = _sections_to_html(sections)
    tiptap = _sections_to_tiptap(sections)

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
            notes=f"Minuta v{next_version} gerada por IA",
        )
    )

    await db.commit()
    await db.refresh(version)

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

    system_prompt = _select_prompt(pr.modelo)

    user_content = (
        f"Consulta juridica original:\n"
        f"Assunto: {pr.subject or 'N/A'}\n\n"
        f"Texto da consulta:\n{pr.extracted_text}\n\n"
        f"---\n\n"
        f"Minuta atual (v{last_version.version_number}):\n"
        f"{last_version.content_html}\n\n"
        f"---\n\n"
        f"Observacoes do revisor para incorporar na nova versao:\n"
        f"{observacoes}"
    )

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    raw_text = response.content[0].text
    sections = _parse_sections(raw_text)
    html = _sections_to_html(sections)
    tiptap = _sections_to_tiptap(sections)

    next_version_num = last_version.version_number + 1

    version = ParecerVersion(
        request_id=pr.id,
        version_number=next_version_num,
        source=VersionSource.ia_reprocessado,
        content_tiptap=tiptap,
        content_html=html,
        reprocess_instructions=observacoes,
    )
    db.add(version)

    old_status = pr.status
    pr.status = ParecerStatus.gerado

    db.add(
        ParecerStatusHistory(
            request_id=pr.id,
            from_status=old_status,
            to_status=ParecerStatus.gerado,
            notes=f"Minuta v{next_version_num} reprocessada por IA com observacoes",
        )
    )

    await db.commit()
    await db.refresh(version)

    return version
