"""
Export service: converte conteúdo do parecer em DOCX e PDF.

DOCX (Camada 5):
- delega para `docx_generator.gerar_parecer_bytes`, que renderiza no padrão
  byte-calibrado do escritório (Consolas/Garamond, ementa em CAPS com
  figure-dash, marcadores [REVISAR—] e [!VERIFICAR:!] em vermelho, bloco
  de assinaturas com espaços manuais calibrados).

PDF:
- gera o `.docx` pelo mesmo caminho acima e converte com `soffice --headless`.
  Garante que o PDF tenha layout, fontes e quebras idênticos ao .docx aberto
  no Word — sem renderizador HTML/CSS paralelo para manter em sincronia.
"""
from __future__ import annotations

import asyncio
import logging
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parecer import ParecerRequest, ParecerVersion
from app.services import docx_generator

logger = logging.getLogger(__name__)


# Timeout do soffice na conversão .docx → .pdf. Pareceres maiores (40+ páginas)
# ficam abaixo de 10s; 60s é folga generosa antes de declarar travamento.
_SOFFICE_PDF_TIMEOUT_S = 60


MESES = [
    "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


# ---------------------------------------------------------------------------
# Helpers compartilhados (DOCX)
# ---------------------------------------------------------------------------

def _formatar_data_extenso(municipio_uf: str = "Fortaleza/CE") -> str:
    """Formata a data atual no padrão 'Município/UF, DD de mês de AAAA'.

    Sem ponto final — o `docx_generator` adiciona ao montar o parágrafo.
    """
    now = datetime.now(timezone.utc)
    return f"{municipio_uf}, {now.day} de {MESES[now.month]} de {now.year}"


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


def _consulente_text(req: ParecerRequest, meta: dict) -> str:
    """Monta o texto do consulente para o bloco 'CONSULENTE:' do parecer."""
    orgao = meta["orgao_consulente"]
    municipio_uf = meta["municipio_uf"]
    if municipio_uf and municipio_uf != "[Município/UF]" and municipio_uf not in orgao:
        return f"{orgao} — {municipio_uf}"
    return orgao


# ---------------------------------------------------------------------------
# DOCX — delega para docx_generator (Camada 5)
# ---------------------------------------------------------------------------

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
        data_extenso=_formatar_data_extenso(meta["municipio_uf"]),
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
            ]
        ),
    )

    return docx_generator.gerar_parecer_bytes(minuta)


# ---------------------------------------------------------------------------
# PDF — converte o .docx via LibreOffice headless
# ---------------------------------------------------------------------------

def _convert_docx_to_pdf(docx_bytes: bytes) -> bytes:
    """Converte bytes de .docx em bytes de PDF via `soffice --headless`.

    Usa um perfil de usuário isolado em tempdir para não disputar o lock
    padrão do LibreOffice quando duas exportações rodam concorrentemente
    (mesmo padrão de `extractor._extract_doc_via_libreoffice`).

    Bloqueia ~1-3s por chamada — o caller deve envolver em `asyncio.to_thread`
    para não travar o event loop do FastAPI.
    """
    with tempfile.TemporaryDirectory(prefix="ione_pdf_") as workdir:
        input_path = Path(workdir) / "parecer.docx"
        input_path.write_bytes(docx_bytes)

        try:
            subprocess.run(
                [
                    "soffice",
                    f"-env:UserInstallation=file://{workdir}/profile",
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", workdir,
                    str(input_path),
                ],
                check=True,
                capture_output=True,
                timeout=_SOFFICE_PDF_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"LibreOffice PDF conversion timed out after {_SOFFICE_PDF_TIMEOUT_S}s"
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace")[:300]
            raise RuntimeError(
                f"LibreOffice PDF conversion failed (rc={exc.returncode}): {stderr}"
            )

        output_path = Path(workdir) / "parecer.pdf"
        if not output_path.exists():
            raise RuntimeError("LibreOffice produced no .pdf output")

        return output_path.read_bytes()


async def to_pdf(
    parecer_request: ParecerRequest,
    version: ParecerVersion,
    db: AsyncSession,
) -> bytes:
    """Gera PDF a partir do .docx — garante paridade visual com o Word."""
    docx_bytes = await to_docx(parecer_request, version, db)
    return await asyncio.to_thread(_convert_docx_to_pdf, docx_bytes)
