"""
Export service: converte conteúdo do parecer em DOCX e PDF.

DOCX (Camada 5):
- delega para `docx_generator.gerar_parecer_bytes`, que renderiza no padrão
  byte-calibrado do escritório (Consolas/Garamond, ementa em CAPS com
  figure-dash, marcadores [REVISAR—] e [!VERIFICAR:!] em vermelho, bloco
  de assinaturas com espaços manuais calibrados).
- `template_parecer.docx` em `backend/app/templates/` deixa de ser fonte
  de formatação; é apenas documentação histórica.

PDF:
- HTML + WeasyPrint preservado da implementação anterior (usado para envio
  por e-mail e visualização rápida).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parecer import ParecerRequest, ParecerVersion
from app.services import docx_generator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constantes institucionais (compartilhadas pelo HTML/PDF)
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
# Helpers compartilhados
# ---------------------------------------------------------------------------

def _formatar_data_extenso(
    municipio_uf: str = "Fortaleza/CE",
    com_ponto: bool = True,
) -> str:
    """Formata a data atual no padrão 'Município/UF, DD de mês de AAAA[.]'.

    `com_ponto=False` é usado pelo docx_generator (que adiciona seu próprio
    ponto final). O HTML/PDF usa `com_ponto=True`.
    """
    now = datetime.now(timezone.utc)
    sep = "." if com_ponto else ""
    return f"{municipio_uf}, {now.day} de {MESES[now.month]} de {now.year}{sep}"


def _get_metadata(req: ParecerRequest) -> dict:
    classification = req.classificacao or {}
    municipio = classification.get("municipio", "")
    uf = classification.get("uf", "CE")
    municipio_uf = f"{municipio}/{uf}" if municipio else "[Município/UF]"
    return {
        "orgao_consulente": classification.get(
            "orgao_consulente", req.sender_email or "[Órgão não informado]"
        ),
        "municipio_uf": municipio_uf,
        "assunto": classification.get("assunto_resumido", req.subject or "[Assunto]"),
        "referencia": req.numero_parecer or "N/A",
        "subtipo": classification.get("subtipo", ""),
        "vertente": classification.get("vertente", ""),
    }


# ---------------------------------------------------------------------------
# Decoração / filtro para o PDF (HTML)
# ---------------------------------------------------------------------------

_ADVOGADO_NOMES = {n for n, _ in ADVOGADOS}
_SKIP_TEXTS = {ESCRITORIO_LINHA1, ESCRITORIO_LINHA2, "PARECER JURÍDICO"}


def _extract_text(content: list[dict[str, Any]]) -> str:
    return "".join(item.get("text", "") for item in content if item.get("type") == "text")


def _is_decoration_node(node: dict[str, Any]) -> bool:
    """Marca nodes do TipTap que são decoração — pulados na renderização HTML/PDF."""
    text = _extract_text(node.get("content", []))
    if not text:
        return False
    if text.strip() in _SKIP_TEXTS:
        return True
    if text.startswith("Órgão Consulente:") or text.startswith("Referência:") or text.startswith("Assunto:"):
        return True
    if text.count("OAB/") >= 2:
        return True
    stripped = text.strip()
    if stripped in _ADVOGADO_NOMES or stripped.startswith("OAB/"):
        return True
    if "Rua Gen. Caiado de Castro" in text:
        return True
    for m in MESES[1:]:
        if f" de {m} de " in text and text.strip().endswith("."):
            return True
    return False


def _filter_tiptap_content(content: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [node for node in content if not _is_decoration_node(node)]


# ---------------------------------------------------------------------------
# DOCX — delega para docx_generator (Camada 5)
# ---------------------------------------------------------------------------

def _consulente_text(req: ParecerRequest, meta: dict) -> str:
    """Monta o texto do consulente para o bloco 'CONSULENTE:' do parecer."""
    orgao = meta["orgao_consulente"]
    municipio_uf = meta["municipio_uf"]
    if municipio_uf and municipio_uf != "[Município/UF]" and municipio_uf not in orgao:
        return f"{orgao} — {municipio_uf}"
    return orgao


async def to_docx(
    parecer_request: ParecerRequest,
    version: ParecerVersion,
    db: AsyncSession,
) -> bytes:
    """Gera o .docx no padrão byte-calibrado do escritório (Camada 5).

    Caminho:
        version.content_tiptap → minuta_from_tiptap → gerar_parecer_bytes → bytes
    """
    meta = _get_metadata(parecer_request)

    tiptap = version.content_tiptap or {}
    if not isinstance(tiptap, dict):
        tiptap = {}

    minuta = docx_generator.minuta_from_tiptap(
        tiptap=tiptap,
        consulente=_consulente_text(parecer_request, meta),
        data_extenso=_formatar_data_extenso(meta["municipio_uf"], com_ponto=False),
        subtipo=meta["subtipo"],
        vertente=meta["vertente"],
    )

    # Salvaguardas: se a IA produziu um parecer com campos vazios, garante
    # que o gerador receba placeholders compreensíveis em vez de quebrar com KeyError.
    if not minuta["ementa_palavras_chave"]:
        minuta["ementa_palavras_chave"] = ["PARECER JURÍDICO"]
    if not minuta["relatorio_paragrafos"]:
        minuta["relatorio_paragrafos"] = ["É o breve relatório. Passa-se à fundamentação."]
    if not minuta["fundamentos_paragrafos"]:
        minuta["fundamentos_paragrafos"] = ["[Fundamentos pendentes de revisão.]"]
    if not minuta["conclusao_dispositivo"]:
        minuta["conclusao_dispositivo"] = "Diante do exposto, o parecer é submetido à superior consideração."
    if not minuta["recomendacoes_alineas"]:
        # Conclusão sem alíneas: minuta válida, gerador apenas pula o bloco.
        minuta["recomendacoes_alineas"] = []

    logger.info(
        "DOCX export: parecer=%s versao=%s vertente=%s subtipo=%s alineas=%d marcadores=%d",
        parecer_request.id,
        version.version_number,
        meta["vertente"] or "?",
        meta["subtipo"] or "?",
        len(minuta["recomendacoes_alineas"]),
        sum(
            docx_generator.contar_marcadores(t)
            for t in [
                *minuta["relatorio_paragrafos"],
                *minuta["fundamentos_paragrafos"],
                minuta["conclusao_dispositivo"],
                *[a[1] for a in minuta["recomendacoes_alineas"]],
                minuta.get("advertencia_protetiva") or "",
            ]
        ),
    )

    return docx_generator.gerar_parecer_bytes(minuta)


# ---------------------------------------------------------------------------
# PDF — HTML + WeasyPrint (preservado)
# ---------------------------------------------------------------------------

def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# Regex compartilhada com o docx_generator para destacar marcadores em vermelho
# também no HTML/PDF.
import re as _re

_PADRAO_MARCADOR_HTML = _re.compile(
    r"\[REVISAR\s*[\-–—]\s*[^\]]+\]|\[!VERIFICAR:[^!]+!\]",
    _re.IGNORECASE,
)


def _highlight_markers(html: str) -> str:
    """Envolve marcadores de revisão humana em <span> vermelho/negrito no HTML."""
    def _wrap(m):
        return f'<span style="color:#C00000; font-weight:bold;">{m.group(0)}</span>'

    return _PADRAO_MARCADOR_HTML.sub(_wrap, html)


def _tiptap_inline_to_html(content: list[dict[str, Any]], force_italic: bool = False) -> str:
    parts: list[str] = []
    for item in content:
        if item.get("type") == "text":
            text = _escape_html(item.get("text", ""))
            marks = item.get("marks", [])
            for mark in marks:
                mt = mark.get("type", "")
                if mt == "bold":
                    text = f"<strong>{text}</strong>"
                elif mt == "italic":
                    text = f"<em>{text}</em>"
                elif mt == "underline":
                    text = f"<u>{text}</u>"
                elif mt == "strike":
                    text = f"<s>{text}</s>"
            if force_italic and not any(m.get("type") == "italic" for m in marks):
                text = f"<em>{text}</em>"
            parts.append(text)
        elif item.get("type") == "hardBreak":
            parts.append("<br>")
    return _highlight_markers("".join(parts))


def _tiptap_body_to_html(content: list[dict[str, Any]]) -> str:
    html_parts: list[str] = []
    for node in content:
        nt = node.get("type", "")

        if nt == "paragraph":
            inline = _tiptap_inline_to_html(node.get("content", []))
            html_parts.append(
                f'<p style="text-indent:1.25cm; margin-bottom:6px; text-align:justify;">{inline}</p>'
            )

        elif nt == "heading":
            level = node.get("attrs", {}).get("level", 2)
            inline = _tiptap_inline_to_html(node.get("content", []))
            if level == 2:
                html_parts.append(
                    f'<h2 style="font-size:12pt; font-weight:bold; text-transform:uppercase; '
                    f'letter-spacing:0.5px; margin-top:20px; margin-bottom:8px;">{inline}</h2>'
                )
            elif level == 3:
                html_parts.append(
                    f'<h3 style="font-size:12pt; font-weight:bold; margin-top:14px; '
                    f'margin-bottom:6px;">{inline}</h3>'
                )
            else:
                html_parts.append(f"<p>{inline}</p>")

        elif nt == "blockquote":
            bq_parts = []
            for child in node.get("content", []):
                inline = _tiptap_inline_to_html(child.get("content", []), force_italic=True)
                bq_parts.append(f"<p>{inline}</p>")
            html_parts.append(
                f'<blockquote style="margin:10px 2cm 10px 1.2cm; padding:8px 12px; '
                f'border-left:3px solid #666; background:#f5f5f5; font-size:11pt; '
                f'text-align:justify; font-style:italic;">{"".join(bq_parts)}</blockquote>'
            )

        elif nt in ("bulletList", "orderedList"):
            tag = "ul" if nt == "bulletList" else "ol"
            items = []
            for item in node.get("content", []):
                if item.get("type") == "listItem":
                    for child in item.get("content", []):
                        inline = _tiptap_inline_to_html(child.get("content", []))
                        items.append(f"<li>{inline}</li>")
            html_parts.append(
                f'<{tag} style="margin-left:2em; margin-bottom:10px;">{"".join(items)}</{tag}>'
            )

        elif nt == "horizontalRule":
            html_parts.append("<hr>")

        else:
            children = node.get("content", [])
            if children:
                html_parts.append(_tiptap_body_to_html(children))

    return "\n".join(html_parts)


def _build_pdf_html(req: ParecerRequest, version: ParecerVersion) -> str:
    meta = _get_metadata(req)

    body_html = ""
    tiptap = version.content_tiptap
    if tiptap and isinstance(tiptap, dict):
        body_html = _tiptap_body_to_html(_filter_tiptap_content(tiptap.get("content", [])))
    elif version.content_html:
        body_html = version.content_html

    sigs = ""
    for nome, oab in ADVOGADOS:
        sigs += f"""
        <div class="assinatura">
            <div class="linha-assinatura">
                <div class="nome">{_escape_html(nome)}</div>
                <div class="oab">{oab}</div>
            </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
@page {{ size: A4; margin: 2.5cm 2cm 2cm 2cm; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Times New Roman', 'Noto Serif', serif; font-size: 12pt;
        line-height: 1.6; color: #000; background: none; }}

.cabecalho {{ border-bottom: 1.5pt solid #000; padding-bottom: 0.35cm; margin-bottom: 0.7cm; }}
.cabecalho .linha1 {{ text-align: center; font-variant: small-caps; font-size: 13pt; letter-spacing: 2px; }}
.cabecalho .linha2 {{ text-align: center; font-weight: bold; font-variant: small-caps; font-size: 11pt;
                      letter-spacing: 1px; padding-top: 3px; }}

h1.titulo {{ text-align: center; font-size: 13pt; font-weight: bold; margin: 14px 0 16px;
             letter-spacing: 1px; }}

.identificacao {{ margin-bottom: 16px; }}
.identificacao p {{ margin: 3px 0; font-size: 11.5pt; }}

.conteudo {{ text-align: justify; }}
.conteudo p {{ font-size: 12pt; margin-bottom: 6px; }}

blockquote {{ break-inside: avoid; }}

.local-data {{ margin-top: 30px; text-align: right; font-size: 12pt; }}

.assinaturas {{ display: flex; flex-wrap: wrap; justify-content: space-between;
                margin-top: 50px; break-inside: avoid; }}
.assinatura {{ width: 46%; text-align: center; margin-bottom: 38px; }}
.assinatura .linha-assinatura {{ border-top: 1px solid #000; margin-top: 42px; padding-top: 5px; }}
.assinatura .nome {{ font-weight: bold; font-variant: small-caps; font-size: 11pt; }}
.assinatura .oab {{ font-size: 10pt; margin-top: 2px; }}

.rodape {{ border-top: 1pt solid #000; padding-top: 0.25cm; margin-top: 1cm;
           font-size: 9pt; text-align: center; color: #333; line-height: 1.4; }}
</style>
</head>
<body>

<div class="cabecalho">
    <div class="linha1">{_escape_html(ESCRITORIO_LINHA1)}</div>
    <div class="linha2">{_escape_html(ESCRITORIO_LINHA2)}</div>
</div>

<h1 class="titulo">PARECER JURÍDICO</h1>

<div class="identificacao">
    <p><strong>Órgão Consulente:</strong> {_escape_html(meta["orgao_consulente"])}</p>
    <p><strong>Referência:</strong> {_escape_html(meta["referencia"])}</p>
    <p><strong>Assunto:</strong> {_escape_html(meta["assunto"])}</p>
</div>

<div class="conteudo">
{body_html}
</div>

<div class="local-data">
    {_escape_html(_formatar_data_extenso(meta["municipio_uf"]))}
</div>

<div class="assinaturas">
{sigs}
</div>

<div class="rodape">
    {_escape_html(ESCRITORIO_ENDERECO)}
</div>

</body>
</html>"""


async def to_pdf(
    parecer_request: ParecerRequest,
    version: ParecerVersion,
    db: AsyncSession,
) -> bytes:
    """Gera PDF via HTML + WeasyPrint — mesma estrutura visual do DOCX."""
    from weasyprint import HTML

    html_str = _build_pdf_html(parecer_request, version)
    return HTML(string=html_str).write_pdf()
