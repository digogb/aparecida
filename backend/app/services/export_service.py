"""
Export service: converts parecer content to DOCX and PDF formats.

Formato baseado no template profissional do escritório:
- Advocacia & Assessoria — Dr. Francisco Ione Pereira Lima
- Font: Times New Roman (serif), 12pt
- Seções: EMENTA, I — RELATÓRIO, II — FUNDAMENTOS, III — CONCLUSÃO
- Assinaturas: 2×2 grid com OAB
- Rodapé: endereço do escritório
"""
from __future__ import annotations

import io
import logging
from datetime import datetime, timezone
from typing import Any

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Emu, Pt, RGBColor
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parecer import ParecerRequest, ParecerVersion

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Escritório info (fixo — dados do template de referência)
# ---------------------------------------------------------------------------
ESCRITORIO_LINHA1 = "Advocacia & Assessoria"
ESCRITORIO_LINHA2 = "Dr. Francisco Ione Pereira Lima"
ESCRITORIO_ENDERECO = (
    "Rua Gen. Caiado de Castro 462, Luciano Cavalcante, Fortaleza-CE  |  "
    "Fone: (85) 3021-7701 / (85) 99981-4392 / (85) 99223-6716  |  "
    "E-mail: dr.ione@uol.com.br"
)

ADVOGADOS = [
    ("Francisco Ione Pereira Lima", "OAB/CE 4.585"),
    ("Matheus Nogueira Pereira Lima", "OAB/CE 31.251"),
    ("Flavio Henrique Luna Silva", "OAB/CE 31.252"),
    ("Valéria Matias de Alencar", "OAB/CE 36.666"),
]

MESES = [
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _formatar_data_extenso(municipio_uf: str) -> str:
    now = datetime.now(timezone.utc)
    municipio = municipio_uf.split("/")[0].strip() if "/" in municipio_uf else municipio_uf
    uf = municipio_uf.split("/")[1].strip() if "/" in municipio_uf else "CE"
    return f"{municipio}/{uf}, {now.day} de {MESES[now.month]} de {now.year}."


def _get_metadata(req: ParecerRequest) -> dict:
    """Extract metadata from classificacao or fallback to request fields."""
    classification = req.classificacao or {}
    municipio = classification.get("municipio", "")
    uf = classification.get("uf", "CE")
    municipio_uf = f"{municipio}/{uf}" if municipio else "[Município/UF]"
    return {
        "orgao_consulente": classification.get("orgao_consulente", req.sender_email or "[Órgão não informado]"),
        "municipio_uf": municipio_uf,
        "assunto": classification.get("assunto_resumido", req.subject or "[Assunto]"),
        "referencia": req.numero_parecer or "N/A",
    }


def _add_paragraph_border_bottom(paragraph) -> None:
    """Add a bottom border to a paragraph via XML."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)
    pPr.append(pBdr)


def _set_cell_border(cell, **kwargs):
    """Set borders on a table cell. kwargs: top, bottom, start, end with val, sz, color."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge, attrs in kwargs.items():
        element = OxmlElement(f"w:{edge}")
        for attr_name, attr_val in attrs.items():
            element.set(qn(f"w:{attr_name}"), str(attr_val))
        tcBorders.append(element)
    tcPr.append(tcBorders)


def _remove_table_borders(table):
    """Remove all borders from a table."""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    tblPr.append(borders)


# ---------------------------------------------------------------------------
# DOCX: Header
# ---------------------------------------------------------------------------

def _build_header(doc: Document) -> None:
    """Cabeçalho: Advocacia & Assessoria / Dr. Francisco Ione Pereira Lima."""
    # Linha 1
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_after = Pt(0)
    p1.paragraph_format.space_before = Pt(0)
    run1 = p1.add_run(ESCRITORIO_LINHA1)
    run1.font.name = "Times New Roman"
    run1.font.size = Pt(13)
    run1.font.small_caps = True

    # Linha 2
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_after = Pt(6)
    p2.paragraph_format.space_before = Pt(2)
    run2 = p2.add_run(ESCRITORIO_LINHA2)
    run2.font.name = "Times New Roman"
    run2.font.size = Pt(11)
    run2.bold = True
    run2.font.small_caps = True

    # Bottom border on last header paragraph
    _add_paragraph_border_bottom(p2)


# ---------------------------------------------------------------------------
# DOCX: Title + Identification
# ---------------------------------------------------------------------------

def _build_title_and_meta(doc: Document, req: ParecerRequest) -> None:
    meta = _get_metadata(req)

    # Título
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(14)
    title_p.paragraph_format.space_after = Pt(14)
    run = title_p.add_run("PARECER JURÍDICO")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)

    # Identification fields
    fields = [
        ("Órgão Consulente:", meta["orgao_consulente"]),
        ("Referência:", meta["referencia"]),
        ("Assunto:", meta["assunto"]),
    ]
    for label, value in fields:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(0)
        run_label = p.add_run(label + " ")
        run_label.bold = True
        run_label.font.name = "Times New Roman"
        run_label.font.size = Pt(11.5)
        run_value = p.add_run(value)
        run_value.font.name = "Times New Roman"
        run_value.font.size = Pt(11.5)


# ---------------------------------------------------------------------------
# DOCX: TipTap JSON → python-docx mapping
# ---------------------------------------------------------------------------

def _add_tiptap_content(doc: Document, content: list[dict[str, Any]]) -> None:
    """Map TipTap JSON nodes to python-docx elements with professional formatting."""
    for node in content:
        node_type = node.get("type", "")

        if node_type == "paragraph":
            para = doc.add_paragraph()
            para.paragraph_format.space_after = Pt(6)
            para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            # Text indent for normal paragraphs
            para.paragraph_format.first_line_indent = Cm(1.25)
            _add_inline_content(para, node.get("content", []))

        elif node_type == "heading":
            level = node.get("attrs", {}).get("level", 2)
            text = _extract_text(node.get("content", []))

            if level == 2:
                # Section heading (EMENTA, I — RELATÓRIO, etc.)
                para = doc.add_paragraph()
                para.paragraph_format.space_before = Pt(18)
                para.paragraph_format.space_after = Pt(8)
                run = para.add_run(text)
                run.bold = True
                run.font.name = "Times New Roman"
                run.font.size = Pt(12)
            elif level == 3:
                # Numbered subtitle (1. Da Legislação, etc.)
                para = doc.add_paragraph()
                para.paragraph_format.space_before = Pt(12)
                para.paragraph_format.space_after = Pt(4)
                run = para.add_run(text)
                run.bold = True
                run.font.name = "Times New Roman"
                run.font.size = Pt(12)
            else:
                para = doc.add_paragraph()
                _add_inline_content(para, node.get("content", []))

        elif node_type == "blockquote":
            # Blockquote: italic, indented left
            for child in node.get("content", []):
                para = doc.add_paragraph()
                para.paragraph_format.left_indent = Cm(2)
                para.paragraph_format.right_indent = Cm(1)
                para.paragraph_format.space_after = Pt(4)
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                _add_inline_content(para, child.get("content", []), italic=True)

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

        else:
            children = node.get("content", [])
            if children:
                _add_tiptap_content(doc, children)


def _add_inline_content(
    paragraph, content: list[dict[str, Any]], italic: bool = False
) -> None:
    """Add inline text nodes (with marks) to a paragraph."""
    for item in content:
        if item.get("type") == "text":
            text = item.get("text", "")
            run = paragraph.add_run(text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

            if italic:
                run.italic = True

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


def _extract_text(content: list[dict[str, Any]]) -> str:
    """Extract plain text from TipTap inline content."""
    return "".join(item.get("text", "") for item in content if item.get("type") == "text")


# ---------------------------------------------------------------------------
# DOCX: Local/Data + Assinaturas + Rodapé
# ---------------------------------------------------------------------------

def _build_closing(doc: Document, req: ParecerRequest) -> None:
    """Local, data e bloco de assinaturas."""
    meta = _get_metadata(req)

    # Local e data (right-aligned)
    data_p = doc.add_paragraph()
    data_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    data_p.paragraph_format.space_before = Pt(24)
    data_p.paragraph_format.space_after = Pt(6)
    run = data_p.add_run(_formatar_data_extenso(meta["municipio_uf"]))
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)

    # Assinaturas: 2×2 table sem bordas
    table = doc.add_table(rows=2, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    _remove_table_borders(table)

    for idx, (nome, oab) in enumerate(ADVOGADOS):
        row = idx // 2
        col = idx % 2
        cell = table.cell(row, col)

        # Clear default paragraph
        cell.paragraphs[0].clear()

        # Spacing before signature line
        spacer = cell.paragraphs[0]
        spacer.paragraph_format.space_before = Pt(36)
        spacer.paragraph_format.space_after = Pt(0)

        # Add top border to simulate signature line
        _set_cell_border(cell, top={"val": "single", "sz": "4", "color": "000000"})

        # Name (small caps, bold, centered)
        name_run = spacer.add_run(nome)
        name_run.bold = True
        name_run.font.name = "Times New Roman"
        name_run.font.size = Pt(11)
        name_run.font.small_caps = True
        spacer.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # OAB
        oab_p = cell.add_paragraph()
        oab_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        oab_p.paragraph_format.space_before = Pt(2)
        oab_p.paragraph_format.space_after = Pt(20)
        oab_run = oab_p.add_run(oab)
        oab_run.font.name = "Times New Roman"
        oab_run.font.size = Pt(10)


def _build_footer(doc: Document) -> None:
    """Rodapé: endereço do escritório com borda superior."""
    doc.add_paragraph()  # spacing

    footer_p = doc.add_paragraph()
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_p.paragraph_format.space_before = Pt(10)

    # Top border
    pPr = footer_p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    top = OxmlElement("w:top")
    top.set(qn("w:val"), "single")
    top.set(qn("w:sz"), "4")
    top.set(qn("w:space"), "1")
    top.set(qn("w:color"), "000000")
    pBdr.append(top)
    pPr.append(pBdr)

    run = footer_p.add_run(ESCRITORIO_ENDERECO)
    run.font.name = "Times New Roman"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)


# ---------------------------------------------------------------------------
# DOCX generation (public)
# ---------------------------------------------------------------------------

async def to_docx(
    parecer_request: ParecerRequest,
    version: ParecerVersion,
    db: AsyncSession,
) -> bytes:
    """Generate DOCX bytes from a parecer version's TipTap content."""
    doc = Document()

    # Page setup (A4)
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)

    # Default font
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.6

    # Build document
    _build_header(doc)
    _build_title_and_meta(doc, parecer_request)

    # Body from TipTap JSON
    tiptap = version.content_tiptap
    if tiptap and isinstance(tiptap, dict):
        content = tiptap.get("content", [])
        _add_tiptap_content(doc, content)
    elif version.content_html:
        doc.add_paragraph(version.content_html)

    # Closing: local/date + signatures
    _build_closing(doc, parecer_request)

    # Footer
    _build_footer(doc)

    # Serialize
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()


# ---------------------------------------------------------------------------
# PDF generation (public)
# ---------------------------------------------------------------------------

async def to_pdf(
    parecer_request: ParecerRequest,
    version: ParecerVersion,
    db: AsyncSession,
) -> bytes:
    """Generate PDF bytes from the pre-rendered HTML (P4 template)."""
    from weasyprint import HTML

    # content_html is already rendered by render_parecer_html (P4 template)
    # which matches the reference format exactly
    html_str = version.content_html
    if not html_str:
        html_str = "<html><body><p>Conteúdo não disponível.</p></body></html>"

    # WeasyPrint ignora @media print — o .parecer-container mantém padding: 2cm
    # da regra base, que duplica com @page margin. Forçar padding/margin 0.
    override_css = (
        "@page { size: A4; margin: 2.5cm 2cm 2cm 2cm; }"
        "body { background: none; }"
        ".parecer-container { padding: 0; margin: 0; max-width: none; box-shadow: none; }"
        "blockquote { break-inside: avoid; }"
        ".assinaturas { break-inside: avoid; }"
    )
    from weasyprint import CSS
    return HTML(string=html_str).write_pdf(
        stylesheets=[CSS(string=override_css)]
    )
