"""
Export service: converts parecer content to DOCX and PDF formats.
"""
from __future__ import annotations

import io
import logging
from datetime import datetime, timezone
from typing import Any

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parecer import ParecerRequest, ParecerVersion
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Escritorio info
# ---------------------------------------------------------------------------
ESCRITORIO_NOME = "Ionde Advogados & Associados"
ESCRITORIO_SUBTITULO = "Assessoria Jurídica em Direito Público Municipal"
ESCRITORIO_ENDERECO = "Rua Exemplo, 123 - Centro - São Carlos/SP - CEP 13560-000"
ESCRITORIO_CONTATO = "Tel: (16) 3333-0000 | contato@ionde.adv.br"


# ---------------------------------------------------------------------------
# TipTap JSON → python-docx mapping
# ---------------------------------------------------------------------------

def _add_tiptap_content(doc: Document, content: list[dict[str, Any]]) -> None:
    """Recursively map TipTap JSON nodes to python-docx elements."""
    for node in content:
        node_type = node.get("type", "")

        if node_type == "paragraph":
            para = doc.add_paragraph()
            _add_inline_content(para, node.get("content", []))

        elif node_type == "heading":
            level = node.get("attrs", {}).get("level", 1)
            heading = doc.add_heading(level=min(level, 4))
            _add_inline_content(heading, node.get("content", []))

        elif node_type == "bulletList":
            for item in node.get("content", []):
                if item.get("type") == "listItem":
                    for child in item.get("content", []):
                        para = doc.add_paragraph(style="List Bullet")
                        _add_inline_content(para, child.get("content", []))

        elif node_type == "orderedList":
            for item in node.get("content", []):
                if item.get("type") == "listItem":
                    for child in item.get("content", []):
                        para = doc.add_paragraph(style="List Number")
                        _add_inline_content(para, child.get("content", []))

        elif node_type == "blockquote":
            for child in node.get("content", []):
                para = doc.add_paragraph(style="Quote")
                _add_inline_content(para, child.get("content", []))

        elif node_type == "horizontalRule":
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = para.add_run("─" * 60)
            run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)

        elif node_type == "hardBreak":
            pass  # handled inline

        else:
            # Fallback: try to recurse into content
            children = node.get("content", [])
            if children:
                _add_tiptap_content(doc, children)


def _add_inline_content(paragraph, content: list[dict[str, Any]]) -> None:
    """Add inline text nodes (with marks) to a paragraph."""
    for item in content:
        if item.get("type") == "text":
            text = item.get("text", "")
            run = paragraph.add_run(text)
            for mark in item.get("marks", []):
                mark_type = mark.get("type", "")
                if mark_type == "bold":
                    run.bold = True
                elif mark_type == "italic":
                    run.italic = True
                elif mark_type == "underline":
                    run.underline = True
                elif mark_type == "strike":
                    run.font.strike = True
        elif item.get("type") == "hardBreak":
            paragraph.add_run("\n")


# ---------------------------------------------------------------------------
# DOCX generation
# ---------------------------------------------------------------------------

async def _get_advogados(db: AsyncSession) -> list[User]:
    """Fetch all active advogado + admin users for the signature block."""
    result = await db.execute(
        select(User).where(
            User.is_active.is_(True),
            User.role.in_([UserRole.advogado, UserRole.admin]),
        )
    )
    return list(result.scalars().all())


def _build_header(doc: Document) -> None:
    """Add escritorio header to the document."""
    header_para = doc.add_paragraph()
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header_para.add_run(ESCRITORIO_NOME)
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    sub_para = doc.add_paragraph()
    sub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub_para.add_run(ESCRITORIO_SUBTITULO)
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    addr_para = doc.add_paragraph()
    addr_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = addr_para.add_run(ESCRITORIO_ENDERECO)
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    contact_para = doc.add_paragraph()
    contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = contact_para.add_run(ESCRITORIO_CONTATO)
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    # Separator
    sep = doc.add_paragraph()
    sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sep.add_run("━" * 70)
    run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
    run.font.size = Pt(6)


def _build_parecer_meta(doc: Document, req: ParecerRequest) -> None:
    """Add parecer metadata block."""
    meta_lines = []
    if req.numero_parecer:
        meta_lines.append(f"PARECER Nº {req.numero_parecer}")
    meta_lines.append(f"Assunto: {req.subject or 'N/A'}")
    if req.tema:
        meta_lines.append(f"Tema: {req.tema.value.capitalize()}")
    meta_lines.append(
        f"Data: {datetime.now(timezone.utc).strftime('%d/%m/%Y')}"
    )
    if req.sender_email:
        meta_lines.append(f"Consulente: {req.sender_email}")

    for line in meta_lines:
        para = doc.add_paragraph()
        run = para.add_run(line)
        run.bold = True
        run.font.size = Pt(11)

    doc.add_paragraph()  # spacing


def _build_footer(doc: Document, advogados: list[User]) -> None:
    """Add signature block with all advogados."""
    doc.add_paragraph()  # spacing

    sep = doc.add_paragraph()
    sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sep.add_run("━" * 70)
    run.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)
    run.font.size = Pt(6)

    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_para.add_run("ASSINATURAS")
    run.bold = True
    run.font.size = Pt(10)

    doc.add_paragraph()  # spacing

    for adv in advogados:
        sig_para = doc.add_paragraph()
        sig_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        line_run = sig_para.add_run("_" * 40)
        line_run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        sig_para.add_run("\n")

        name_run = sig_para.add_run(adv.name)
        name_run.bold = True
        name_run.font.size = Pt(10)
        sig_para.add_run("\n")

        role_label = "Advogado" if adv.role == UserRole.advogado else "Sócio-Administrador"
        role_run = sig_para.add_run(role_label)
        role_run.font.size = Pt(9)
        role_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

        doc.add_paragraph()  # spacing between signatures


async def to_docx(
    parecer_request: ParecerRequest,
    version: ParecerVersion,
    db: AsyncSession,
) -> bytes:
    """Generate DOCX bytes from a parecer version's TipTap content."""
    doc = Document()

    # Page setup
    section = doc.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3)
    section.right_margin = Cm(2)

    # Default font
    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.5

    # Build document
    _build_header(doc)
    _build_parecer_meta(doc, parecer_request)

    # Body from TipTap JSON
    tiptap = version.content_tiptap
    if tiptap and isinstance(tiptap, dict):
        content = tiptap.get("content", [])
        _add_tiptap_content(doc, content)
    elif version.content_html:
        # Fallback: plain text from HTML
        doc.add_paragraph(version.content_html)

    # Footer with signatures
    advogados = await _get_advogados(db)
    _build_footer(doc, advogados)

    # Serialize to bytes
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

_PDF_CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm 2.5cm 3cm;
    @bottom-center {
        content: "Página " counter(page) " de " counter(pages);
        font-size: 8pt;
        color: #999;
    }
}
body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}
.header {
    text-align: center;
    margin-bottom: 20px;
}
.header h1 {
    font-size: 16pt;
    color: #1A365D;
    margin: 0;
}
.header .subtitle {
    font-size: 10pt;
    color: #666;
    margin: 4px 0;
}
.header .info {
    font-size: 8pt;
    color: #999;
}
.separator {
    border: none;
    border-top: 2px solid #1A365D;
    margin: 15px 0;
}
.meta {
    margin-bottom: 20px;
}
.meta p {
    font-weight: bold;
    margin: 4px 0;
}
.content {
    margin-bottom: 30px;
}
.content h1, .content h2, .content h3, .content h4 {
    color: #1A365D;
    margin-top: 16px;
}
.content blockquote {
    border-left: 3px solid #1A365D;
    padding-left: 12px;
    color: #555;
    margin: 12px 0;
}
.signatures {
    margin-top: 40px;
    text-align: center;
}
.signature-block {
    display: inline-block;
    width: 45%;
    margin: 20px 2%;
    text-align: center;
}
.signature-line {
    border-top: 1px solid #999;
    width: 80%;
    margin: 0 auto 4px auto;
}
.signature-name {
    font-weight: bold;
    font-size: 10pt;
}
.signature-role {
    font-size: 9pt;
    color: #666;
}
"""


def _tiptap_to_html(content: list[dict[str, Any]]) -> str:
    """Convert TipTap JSON content to HTML string."""
    parts: list[str] = []

    for node in content:
        node_type = node.get("type", "")

        if node_type == "paragraph":
            inner = _inline_to_html(node.get("content", []))
            parts.append(f"<p>{inner}</p>")

        elif node_type == "heading":
            level = node.get("attrs", {}).get("level", 1)
            level = min(level, 4)
            inner = _inline_to_html(node.get("content", []))
            parts.append(f"<h{level}>{inner}</h{level}>")

        elif node_type == "bulletList":
            items = _list_items_html(node)
            parts.append(f"<ul>{items}</ul>")

        elif node_type == "orderedList":
            items = _list_items_html(node)
            parts.append(f"<ol>{items}</ol>")

        elif node_type == "blockquote":
            inner = _tiptap_to_html(node.get("content", []))
            parts.append(f"<blockquote>{inner}</blockquote>")

        elif node_type == "horizontalRule":
            parts.append("<hr>")

        else:
            children = node.get("content", [])
            if children:
                parts.append(_tiptap_to_html(children))

    return "\n".join(parts)


def _list_items_html(node: dict[str, Any]) -> str:
    items: list[str] = []
    for item in node.get("content", []):
        if item.get("type") == "listItem":
            inner = _tiptap_to_html(item.get("content", []))
            items.append(f"<li>{inner}</li>")
    return "\n".join(items)


def _inline_to_html(content: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in content:
        if item.get("type") == "text":
            text = _escape_html(item.get("text", ""))
            for mark in item.get("marks", []):
                mark_type = mark.get("type", "")
                if mark_type == "bold":
                    text = f"<strong>{text}</strong>"
                elif mark_type == "italic":
                    text = f"<em>{text}</em>"
                elif mark_type == "underline":
                    text = f"<u>{text}</u>"
                elif mark_type == "strike":
                    text = f"<s>{text}</s>"
            parts.append(text)
        elif item.get("type") == "hardBreak":
            parts.append("<br>")
    return "".join(parts)


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _build_pdf_html(
    req: ParecerRequest,
    version: ParecerVersion,
    advogados: list[User],
) -> str:
    """Build full HTML document for PDF rendering."""
    # Body content
    tiptap = version.content_tiptap
    if tiptap and isinstance(tiptap, dict):
        body_html = _tiptap_to_html(tiptap.get("content", []))
    elif version.content_html:
        body_html = version.content_html
    else:
        body_html = "<p>Conteúdo não disponível.</p>"

    # Meta
    meta_lines = []
    if req.numero_parecer:
        meta_lines.append(f"PARECER Nº {req.numero_parecer}")
    meta_lines.append(f"Assunto: {req.subject or 'N/A'}")
    if req.tema:
        meta_lines.append(f"Tema: {req.tema.value.capitalize()}")
    meta_lines.append(
        f"Data: {datetime.now(timezone.utc).strftime('%d/%m/%Y')}"
    )
    if req.sender_email:
        meta_lines.append(f"Consulente: {req.sender_email}")
    meta_html = "\n".join(f"<p>{_escape_html(l)}</p>" for l in meta_lines)

    # Signatures
    sig_blocks = []
    for adv in advogados:
        role_label = "Advogado" if adv.role == UserRole.advogado else "Sócio-Administrador"
        sig_blocks.append(
            f'<div class="signature-block">'
            f'<div class="signature-line"></div>'
            f'<div class="signature-name">{_escape_html(adv.name)}</div>'
            f'<div class="signature-role">{role_label}</div>'
            f"</div>"
        )
    sig_html = "\n".join(sig_blocks)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <style>{_PDF_CSS}</style>
</head>
<body>
    <div class="header">
        <h1>{_escape_html(ESCRITORIO_NOME)}</h1>
        <div class="subtitle">{_escape_html(ESCRITORIO_SUBTITULO)}</div>
        <div class="info">{_escape_html(ESCRITORIO_ENDERECO)}</div>
        <div class="info">{_escape_html(ESCRITORIO_CONTATO)}</div>
    </div>
    <hr class="separator">
    <div class="meta">
        {meta_html}
    </div>
    <div class="content">
        {body_html}
    </div>
    <hr class="separator">
    <div class="signatures">
        {sig_html}
    </div>
</body>
</html>"""


async def to_pdf(
    parecer_request: ParecerRequest,
    version: ParecerVersion,
    db: AsyncSession,
) -> bytes:
    """Generate PDF bytes from a parecer version's content via WeasyPrint."""
    from weasyprint import HTML

    advogados = await _get_advogados(db)
    html_str = _build_pdf_html(parecer_request, version, advogados)
    return HTML(string=html_str).write_pdf()
