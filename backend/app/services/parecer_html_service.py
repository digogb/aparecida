"""
P4 — Template HTML para renderização do Parecer Jurídico
Pipeline: Pareceres Jurídicos — Ionde Advogados & Associados
Versão: 4.1

Uso: Código Python puro. Recebe dados do parecer (dict) e gera HTML.
NÃO usa IA — renderização 100% determinística.

O HTML gerado:
- Tem paginação automática via CSS (page-break)
- Cabeçalho e rodapé em todas as páginas (@media print)
- Formatação profissional compatível com impressão e WeasyPrint
- Conteúdo fluido (não depende de div.pagina fixa)
"""

from datetime import date
from typing import Optional
import json
import re


def render_parecer_html(parecer: dict) -> str:
    """
    Renderiza parecer jurídico em HTML profissional.
    
    Args:
        parecer: dict com as chaves do XML parseado:
            - metadata: dict com orgao_consulente, municipio_uf, assunto, referencia, data_elaboracao
            - ementa: str
            - relatorio: str
            - fundamentos: str
            - conclusao: str
            - citacoes_verificar: list (opcional, não renderizado no HTML final)
            - ressalvas: list (opcional, não renderizado no HTML final)
    
    Returns:
        HTML string completa, pronta para WeasyPrint ou browser.
    """
    meta = parecer.get("metadata", {})
    if isinstance(meta, str):
        meta = json.loads(meta)
    
    orgao = meta.get("orgao_consulente", "[Órgão não informado]")
    municipio_uf = meta.get("municipio_uf", "[Município/UF]")
    assunto = meta.get("assunto", "[Assunto]")
    referencia = meta.get("referencia") or "N/A"
    data_str = meta.get("data_elaboracao", date.today().isoformat())
    
    # Formatar data por extenso
    data_extenso = _formatar_data_extenso(data_str, municipio_uf)
    
    # Converter markdown-like do conteúdo para HTML
    ementa_html = _texto_para_html(parecer.get("ementa", ""))
    relatorio_html = _texto_para_html(parecer.get("relatorio", ""))
    fundamentos_html = _texto_para_html(parecer.get("fundamentos", ""))
    conclusao_html = _texto_para_html(parecer.get("conclusao", ""))
    
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Parecer Jurídico — {_escape(assunto)}</title>
    <style>
        /* ═══ RESET E BASE ═══ */
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: 'Garamond', 'Times New Roman', 'Noto Serif', serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #000;
            background: #f0f0f0;
        }}

        /* ═══ CONTAINER PRINCIPAL (tela) ═══ */
        .parecer-container {{
            max-width: 21cm;
            margin: 20px auto;
            padding: 2cm;
            background: #fff;
            box-shadow: 0 0 8px rgba(0,0,0,.18);
        }}

        /* ═══ CABEÇALHO ═══ */
        .cabecalho {{
            border-bottom: 1.5pt solid #000;
            padding-bottom: 0.35cm;
            margin-bottom: 0.7cm;
        }}
        .cabecalho .linha1 {{
            text-align: center;
            font-variant: small-caps;
            font-size: 13pt;
            letter-spacing: 2px;
        }}
        .cabecalho .linha2 {{
            text-align: center;
            font-weight: bold;
            font-variant: small-caps;
            font-size: 11pt;
            letter-spacing: 1px;
            padding-top: 3px;
        }}

        /* ═══ TÍTULO ═══ */
        h1.titulo-parecer {{
            text-align: center;
            font-size: 13pt;
            font-weight: bold;
            margin: 14px 0 16px;
            letter-spacing: 1px;
        }}

        /* ═══ IDENTIFICAÇÃO ═══ */
        .identificacao {{
            margin-bottom: 16px;
        }}
        .identificacao p {{
            margin: 3px 0;
            font-size: 11.5pt;
        }}

        /* ═══ EMENTA ═══ */
        .ementa {{
            margin: 16px 0;
            padding: 10px 16px;
            border-left: 3px solid #333;
            background: #f8f8f8;
            font-size: 11pt;
            text-align: justify;
        }}

        /* ═══ SEÇÕES ═══ */
        .secao {{
            font-weight: bold;
            font-size: 12pt;
            margin-top: 20px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* ═══ CONTEÚDO ═══ */
        .conteudo {{
            text-align: justify;
        }}
        .conteudo p {{
            text-indent: 2em;
            margin-bottom: 10px;
            font-size: 12pt;
        }}
        .conteudo p.sem-recuo {{
            text-indent: 0;
        }}
        .conteudo p.subtitulo {{
            text-indent: 0;
            font-weight: bold;
            margin-top: 14px;
            margin-bottom: 6px;
        }}

        /* ═══ CITAÇÕES ═══ */
        blockquote {{
            margin: 10px 2cm 10px 1.2cm;
            padding: 8px 12px;
            border-left: 3px solid #666;
            background: #f5f5f5;
            font-size: 11pt;
            text-align: justify;
            font-style: italic;
        }}
        blockquote em {{
            font-style: normal;
            font-weight: bold;
        }}

        /* ═══ CONCLUSÃO ═══ */
        .conclusao-item {{
            margin: 8px 0 8px 2.5cm;
            text-align: justify;
        }}

        /* ═══ LOCAL E DATA ═══ */
        .local-data {{
            margin-top: 30px;
            text-align: right;
            font-size: 12pt;
        }}

        /* ═══ ASSINATURAS ═══ */
        .assinaturas {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin-top: 50px;
        }}
        .assinatura {{
            width: 46%;
            text-align: center;
            margin-bottom: 38px;
        }}
        .assinatura .linha-assinatura {{
            border-top: 1px solid #000;
            margin-top: 42px;
            padding-top: 5px;
        }}
        .assinatura .nome {{
            font-weight: bold;
            font-variant: small-caps;
            font-size: 11pt;
        }}
        .assinatura .oab {{
            font-size: 10pt;
            margin-top: 2px;
        }}

        /* ═══ RODAPÉ ═══ */
        .rodape {{
            border-top: 1pt solid #000;
            padding-top: 0.25cm;
            margin-top: 1cm;
            font-size: 9pt;
            text-align: center;
            color: #333;
            line-height: 1.4;
        }}

        /* ═══ IMPRESSÃO ═══ */
        @media print {{
            body {{
                background: none;
            }}
            .parecer-container {{
                box-shadow: none;
                margin: 0;
                padding: 0;
                max-width: none;
            }}
            
            /* Cabeçalho e rodapé em todas as páginas */
            .cabecalho {{
                position: running(cabecalho);
            }}
            .rodape {{
                position: running(rodape);
            }}
            
            @page {{
                size: A4;
                margin: 2cm;
                @top-center {{
                    content: element(cabecalho);
                }}
                @bottom-center {{
                    content: element(rodape);
                }}
            }}
            
            /* Evitar quebra no meio de citações e conclusão */
            blockquote {{
                break-inside: avoid;
            }}
            .assinaturas {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>

<div class="parecer-container">
    
    <!-- CABEÇALHO -->
    <div class="cabecalho">
        <div class="linha1">Advocacia &amp; Assessoria</div>
        <div class="linha2">Dr. Francisco Ione Pereira Lima</div>
    </div>

    <!-- TÍTULO E IDENTIFICAÇÃO -->
    <h1 class="titulo-parecer">PARECER JURÍDICO</h1>
    
    <div class="identificacao">
        <p><strong>Órgão Consulente:</strong> {_escape(orgao)}</p>
        <p><strong>Referência:</strong> {_escape(referencia)}</p>
        <p><strong>Assunto:</strong> {_escape(assunto)}</p>
    </div>

    <!-- EMENTA -->
    <div class="ementa">
        {ementa_html}
    </div>

    <!-- RELATÓRIO -->
    <div class="secao">I — Relatório</div>
    <div class="conteudo">
        {relatorio_html}
    </div>

    <!-- FUNDAMENTOS -->
    <div class="secao">II — Fundamentos</div>
    <div class="conteudo">
        {fundamentos_html}
    </div>

    <!-- CONCLUSÃO -->
    <div class="secao">III — Conclusão</div>
    <div class="conteudo">
        {conclusao_html}
    </div>

    <!-- LOCAL, DATA E ASSINATURAS -->
    <div class="local-data">
        {_escape(data_extenso)}
    </div>

    <div class="assinaturas">
        <div class="assinatura">
            <div class="linha-assinatura">
                <div class="nome">Francisco Ione Pereira Lima</div>
                <div class="oab">OAB/CE 4.585</div>
            </div>
        </div>
        <div class="assinatura">
            <div class="linha-assinatura">
                <div class="nome">Matheus Nogueira Pereira Lima</div>
                <div class="oab">OAB/CE 31.251</div>
            </div>
        </div>
        <div class="assinatura">
            <div class="linha-assinatura">
                <div class="nome">Flavio Henrique Luna Silva</div>
                <div class="oab">OAB/CE 31.252</div>
            </div>
        </div>
        <div class="assinatura">
            <div class="linha-assinatura">
                <div class="nome">Valéria Matias de Alencar</div>
                <div class="oab">OAB/CE 36.666</div>
            </div>
        </div>
    </div>

    <!-- RODAPÉ -->
    <div class="rodape">
        Rua Gen. Caiado de Castro 462, Luciano Cavalcante, Fortaleza-CE &nbsp;|&nbsp;
        Fone: (85) 3021-7701 / (85) 99981-4392 / (85) 99223-6716 &nbsp;|&nbsp;
        E-mail: dr.ione@uol.com.br
    </div>

</div>

</body>
</html>"""


def _escape(text: str) -> str:
    """Escapa HTML entities."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _texto_para_html(texto: str) -> str:
    """
    Converte o texto do parecer (com formatação leve) para HTML.
    
    Suporta:
    - Parágrafos (linhas em branco)
    - Blockquotes (linhas começando com >)
    - Subtítulos numerados (ex: "1. Da Legislação")
    - Alíneas (a), b), c))
    - **negrito**
    """
    if not texto:
        return ""
    
    lines = texto.strip().split("\n")
    html_parts = []
    in_blockquote = False
    blockquote_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Blockquote
        if stripped.startswith(">"):
            if not in_blockquote:
                in_blockquote = True
                blockquote_lines = []
            content = stripped[1:].strip()
            if content:
                blockquote_lines.append(content)
            else:
                blockquote_lines.append("<br>")
            continue
        elif in_blockquote:
            # Fechar blockquote
            bq_content = " ".join(blockquote_lines)
            bq_content = _apply_inline_formatting(bq_content)
            html_parts.append(f"<blockquote>{bq_content}</blockquote>")
            in_blockquote = False
            blockquote_lines = []
        
        if not stripped:
            continue
        
        # Subtítulos numerados (ex: "1. Considerações Preliminares")
        if re.match(r'^\d+\.\s+[A-Z]', stripped):
            html_parts.append(
                f'<p class="subtitulo">{_apply_inline_formatting(_escape_content(stripped))}</p>'
            )
            continue
        
        # Alíneas
        if re.match(r'^[a-z]\)', stripped):
            html_parts.append(
                f'<div class="conclusao-item">{_apply_inline_formatting(_escape_content(stripped))}</div>'
            )
            continue
        
        # Parágrafo normal
        css_class = ""
        if stripped.startswith("É o breve relatório") or stripped.startswith("É o parecer") or stripped.startswith("Diante do exposto"):
            css_class = ' class="sem-recuo"'
        
        html_parts.append(
            f"<p{css_class}>{_apply_inline_formatting(_escape_content(stripped))}</p>"
        )
    
    # Fechar blockquote pendente
    if in_blockquote and blockquote_lines:
        bq_content = " ".join(blockquote_lines)
        bq_content = _apply_inline_formatting(bq_content)
        html_parts.append(f"<blockquote>{bq_content}</blockquote>")
    
    return "\n        ".join(html_parts)


def _escape_content(text: str) -> str:
    """Escapa HTML entities no conteúdo (sem escapar markdown)."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _apply_inline_formatting(text: str) -> str:
    """Converte **negrito** para <strong>."""
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)


def _formatar_data_extenso(data_iso: str, municipio_uf: str) -> str:
    """Formata data ISO para extenso brasileiro."""
    meses = [
        "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    try:
        partes = data_iso.split("-")
        ano = int(partes[0])
        mes = int(partes[1])
        dia = int(partes[2])
        
        # Extrair município (sem /UF)
        municipio = municipio_uf.split("/")[0].strip() if "/" in municipio_uf else municipio_uf
        uf = municipio_uf.split("/")[1].strip() if "/" in municipio_uf else "CE"
        
        return f"{municipio}/{uf}, {dia} de {meses[mes]} de {ano}."
    except (IndexError, ValueError):
        return f"{municipio_uf}, {date.today().strftime('%d de %B de %Y')}."


# ═══════════════════════════════════════════════════════════════
# Parser do XML de saída do P2/P3
# ═══════════════════════════════════════════════════════════════

def parse_parecer_xml(xml_text: str) -> dict:
    """
    Parse simples do XML estruturado retornado pelo P2/P3.
    Usa regex para extrair seções — não precisa de parser XML pesado
    porque o formato é controlado e flat.
    """
    sections = {}
    tags = [
        "metadata", "ementa", "relatorio", "fundamentos",
        "conclusao", "citacoes_verificar", "ressalvas",
        "secoes_alteradas", "notas_revisor"
    ]
    
    for tag in tags:
        pattern = rf"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, xml_text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Tentar parse JSON para campos estruturados
            if tag in ("metadata", "citacoes_verificar", "ressalvas", "secoes_alteradas", "notas_revisor"):
                try:
                    content = json.loads(content)
                except (json.JSONDecodeError, TypeError):
                    pass
            sections[tag] = content
    
    return sections
