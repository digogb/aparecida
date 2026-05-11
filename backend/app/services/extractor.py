"""
Text extraction from PDF, DOCX, and plain-text files.

extract_pdf  -> (text, method)  — pdfplumber primary, Tesseract OCR fallback
extract_docx -> (text, method)  — python-docx paragraphs + tables
extract_file -> (text, method, status) — dispatcher by file extension
"""
from __future__ import annotations

import io
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import chardet
import filetype
import pdfplumber
import pytesseract
from docx import Document

logger = logging.getLogger(__name__)

# Average characters per page below this threshold triggers OCR fallback
_OCR_THRESHOLD = 100

# LibreOffice conversion timeout (soffice can hang on malformed input)
_SOFFICE_TIMEOUT_S = 60


def _sanitize_text(text: str) -> str:
    """Strip NUL bytes — PostgreSQL TEXT columns reject 0x00 and abort the INSERT."""
    if not text:
        return text
    return text.replace("\x00", "")


def _extract_doc_via_libreoffice(file_bytes: bytes) -> str:
    """Convert legacy .doc (binary OLE) to text using `soffice --headless`.

    Uses an isolated user profile so concurrent calls don't contend on the
    default LibreOffice lock. Raises RuntimeError on any conversion failure.
    """
    with tempfile.TemporaryDirectory(prefix="ione_doc_") as workdir:
        input_path = Path(workdir) / "input.doc"
        input_path.write_bytes(file_bytes)

        try:
            subprocess.run(
                [
                    "soffice",
                    f"-env:UserInstallation=file://{workdir}/profile",
                    "--headless",
                    "--convert-to", "txt:Text",
                    "--outdir", workdir,
                    str(input_path),
                ],
                check=True,
                capture_output=True,
                timeout=_SOFFICE_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"LibreOffice timed out after {_SOFFICE_TIMEOUT_S}s")
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"LibreOffice failed (rc={exc.returncode}): {stderr}")

        output_path = Path(workdir) / "input.txt"
        if not output_path.exists():
            raise RuntimeError("LibreOffice produced no .txt output")

        return output_path.read_text(encoding="utf-8", errors="replace")


def extract_pdf(file_bytes: bytes) -> Tuple[str, str]:
    """Extract text from a PDF.

    Returns (text, method) where method is 'pdfplumber' or 'tesseract_ocr'.
    Falls back to Tesseract when average characters per page < _OCR_THRESHOLD.
    """
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = pdf.pages
        if not pages:
            return "", "pdfplumber"

        page_texts = [page.extract_text() or "" for page in pages]
        total_chars = sum(len(t) for t in page_texts)
        avg_chars = total_chars / len(pages)

        if avg_chars >= _OCR_THRESHOLD:
            return "\n".join(page_texts), "pdfplumber"

    # Fallback: render each page as image and OCR
    logger.info(
        "PDF sparse (avg %.1f chars/page), switching to Tesseract OCR", avg_chars
    )
    ocr_texts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            img = page.to_image(resolution=200).original
            ocr_texts.append(pytesseract.image_to_string(img, lang="por"))

    return "\n".join(ocr_texts), "tesseract_ocr"


def extract_docx(file_bytes: bytes) -> Tuple[str, str]:
    """Extract text from a DOCX file (paragraphs and tables).

    Returns (text, 'python_docx').
    """
    doc = Document(io.BytesIO(file_bytes))
    parts: list[str] = []

    for para in doc.paragraphs:
        stripped = para.text.strip()
        if stripped:
            parts.append(stripped)

    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                parts.append(" | ".join(cells))

    return "\n".join(parts), "python_docx"


def _detect_encoding(file_bytes: bytes) -> str:
    result = chardet.detect(file_bytes)
    return result.get("encoding") or "utf-8"


def extract_file(
    filename: str, file_bytes: bytes
) -> Tuple[str, Optional[str], str]:
    """Dispatcher: extract text from a file based on its extension.

    Returns (text, method, status) where:
      - method is an ExtractionMethod enum value string or None
      - status is an ExtractionStatus enum value string: 'success', 'partial', 'failed'

    Handles password-protected files and encoding errors gracefully.
    """
    lower = filename.lower()
    try:
        if lower.endswith(".pdf"):
            text, method = extract_pdf(file_bytes)
            status = "success" if text.strip() else "partial"
            return _sanitize_text(text), method, status

        if lower.endswith(".docx"):
            text, method = extract_docx(file_bytes)
            status = "success" if text.strip() else "partial"
            return _sanitize_text(text), method, status

        if lower.endswith((".txt", ".text")):
            encoding = _detect_encoding(file_bytes)
            text = file_bytes.decode(encoding, errors="replace")
            return _sanitize_text(text), None, "success"

        if lower.endswith(".doc"):
            try:
                text = _extract_doc_via_libreoffice(file_bytes)
            except Exception as exc:
                logger.error("LibreOffice failed for %s: %s", filename, exc)
                return "", "fallback_libreoffice", "failed"
            status = "success" if text.strip() else "partial"
            return _sanitize_text(text), "fallback_libreoffice", status

        # Extension unknown or missing — try to detect via magic bytes
        kind = filetype.guess(file_bytes)
        if kind is not None:
            logger.info(
                "Detected file type by magic bytes: %s -> %s (%s)",
                filename, kind.extension, kind.mime,
            )
            guessed_name = f"_detected_.{kind.extension}"
            return extract_file(guessed_name, file_bytes)

        logger.warning("Unsupported file type for extraction: %s", filename)
        return "", None, "failed"

    except Exception as exc:
        msg = str(exc).lower()
        if "password" in msg or "encrypted" in msg:
            logger.warning("Password-protected or encrypted file skipped: %s", filename)
        else:
            logger.error("Extraction failed for %s: %s", filename, exc)
        return "", None, "failed"
