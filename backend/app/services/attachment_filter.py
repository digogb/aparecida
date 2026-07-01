"""
Gate de anexo-documento.

Usado para decidir se uma resposta numa thread já importada merece virar um novo
`ParecerRequest` "irmão". Só ingere réplicas que trazem um documento de verdade
(edital, laudo, ata, planilha, etc.) — não uma imagem de assinatura de e-mail.

"Tem anexo" sozinho é fraco: assinaturas de e-mail vêm como PNGs (logos). Por isso
filtramos por whitelist de extensão/MIME de documento, excluindo explicitamente `image/*`.
"""
from __future__ import annotations

from pathlib import PurePosixPath
from typing import Iterable

# Extensões de documento aceitas (lowercase, com ponto).
DOCUMENT_EXTS: frozenset[str] = frozenset(
    {
        ".pdf",
        ".doc",
        ".docx",
        ".odt",
        ".rtf",
        ".txt",
        ".xls",
        ".xlsx",
        ".csv",
        ".ods",
    }
)

# Prefixos MIME de documento. `image/*` é intencionalmente omitido.
DOCUMENT_MIME_PREFIXES: tuple[str, ...] = (
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml",
    "application/vnd.oasis.opendocument.text",
    "application/rtf",
    "text/rtf",
    "text/plain",
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml",
    "application/vnd.oasis.opendocument.spreadsheet",
)


def is_document_attachment(filename: str | None, mime_type: str | None) -> bool:
    """True se o anexo parece um documento (por extensão OU por MIME); nunca `image/*`."""
    mime = (mime_type or "").split(";", 1)[0].strip().lower()
    if mime.startswith("image/"):
        return False

    ext = PurePosixPath(filename or "").suffix.lower()
    if ext in DOCUMENT_EXTS:
        return True

    return any(mime.startswith(prefix) for prefix in DOCUMENT_MIME_PREFIXES)


def has_document_attachment(pares: Iterable[tuple[str | None, str | None]]) -> bool:
    """True se algum par (filename, mime_type) é um documento."""
    return any(is_document_attachment(filename, mime) for filename, mime in pares)
