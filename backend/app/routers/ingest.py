"""
Ingest router: parse a .eml file and create a ParecerRequest.
Used for POC/manual flow — bypasses Gmail API entirely.
"""
from __future__ import annotations

import email as email_lib
import email.policy
import os
import re
import uuid
from email.header import decode_header as _decode_header
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parecer import Attachment as AttachmentModel

UPLOADS_DIR = Path("/app/uploads")

from app.database import get_db
from app.models.municipio import Municipio
from app.models.parecer import (
    Attachment,
    ExtractionMethod,
    ExtractionStatus,
    ParecerRequest,
    ParecerStatus,
)
from app.services.content_assembler import assemble
from app.services.extractor import extract_file

PREFIX = "/api"
TAGS = ["ingest"]

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decode_str(value: str) -> str:
    """Decode RFC2047-encoded email header value."""
    parts = []
    for raw, charset in _decode_header(value):
        if isinstance(raw, bytes):
            parts.append(raw.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(raw)
    return "".join(parts)


def _strip_html(html: str) -> str:
    from bs4 import BeautifulSoup
    return BeautifulSoup(html, "html.parser").get_text(separator="\n")


def _extract_body(msg: email_lib.message.Message) -> str:
    """Walk MIME tree and return plain text body. Prefers text/plain."""
    plain = ""
    html = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = part.get("Content-Disposition", "")
            if "attachment" in cd:
                continue
            if ct == "text/plain" and not plain:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                plain = payload.decode(charset, errors="replace") if payload else ""
            elif ct == "text/html" and not html:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                raw = payload.decode(charset, errors="replace") if payload else ""
                html = _strip_html(raw)
    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or "utf-8"
        text = payload.decode(charset, errors="replace") if payload else ""
        if msg.get_content_type() == "text/html":
            return _strip_html(text)
        return text

    return plain or html


def _collect_attachments(
    msg: email_lib.message.Message,
) -> list[tuple[str, str, bytes]]:
    """Return list of (filename, content_type, bytes) for each attachment."""
    result = []
    if not msg.is_multipart():
        return result
    for part in msg.walk():
        cd = part.get("Content-Disposition", "")
        filename_raw = part.get_filename()
        if not filename_raw:
            continue
        filename = _decode_str(filename_raw)
        content_type = part.get_content_type()
        payload = part.get_payload(decode=True)
        if payload:
            result.append((filename, content_type, payload))
    return result


def _extract_sender_email(from_header: str) -> str:
    """Extract bare email from 'Name <email>' or 'email'."""
    match = re.search(r"<([^>]+)>", from_header)
    if match:
        return match.group(1).strip().lower()
    return from_header.strip().lower()


def _extract_domain(email_addr: str) -> str:
    match = re.search(r"@([\w.-]+)", email_addr)
    return match.group(1).lower() if match else ""


async def _identify_municipio(domain: str, db: AsyncSession):
    result = await db.execute(select(Municipio).where(Municipio.is_active.is_(True)))
    for m in result.scalars():
        domains = [d.lower() for d in (m.dominios_email or [])]
        if domain in domains:
            return m
    return None


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/parecer-requests/ingest-eml", status_code=201)
async def ingest_eml(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Parse a .eml file and create a ParecerRequest ready for classification."""
    if not file.filename or not file.filename.lower().endswith(".eml"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .eml")

    raw = await file.read()
    try:
        msg = email_lib.message_from_bytes(raw, policy=email_lib.policy.compat32)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Falha ao parsear .eml: {exc}")

    subject = _decode_str(msg.get("Subject") or "")
    # Strip common forward/reply prefixes
    subject = re.sub(r"^(ENC|FWD|RES|RE|FW):\s*", "", subject, flags=re.IGNORECASE).strip()

    from_header = msg.get("From") or ""
    sender_email = _extract_sender_email(_decode_str(from_header))
    message_id = msg.get("Message-ID") or str(uuid.uuid4())
    thread_id = msg.get("In-Reply-To") or message_id

    # Deduplicate by thread_id
    existing = await db.execute(
        select(ParecerRequest).where(ParecerRequest.gmail_thread_id == thread_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Parecer já importado para este email")

    # Resolve municipio from sender domain
    domain = _extract_domain(sender_email)
    municipio = await _identify_municipio(domain, db) if domain else None

    # Extract body
    body = _extract_body(msg)

    # Extract attachments
    attachments_meta = _collect_attachments(msg)
    attachment_texts: list[str] = []
    attachment_records: list[dict] = []

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content_type, file_bytes in attachments_meta:
        text, method, status = extract_file(filename, file_bytes)

        # Persist file to disk
        safe_name = re.sub(r"[^\w.\-]", "_", filename)
        file_id = uuid.uuid4()
        storage_path = str(UPLOADS_DIR / f"{file_id}_{safe_name}")
        with open(storage_path, "wb") as f:
            f.write(file_bytes)

        attachment_records.append({
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(file_bytes),
            "extracted_text": text or None,
            "extraction_method": ExtractionMethod(method) if method else None,
            "extraction_status": ExtractionStatus(status),
            "storage_path": storage_path,
        })
        if text:
            attachment_texts.append(text)

    extracted_text = assemble(body, attachment_texts)

    # Sempre prefixa assunto + remetente para que P1 tenha contexto mínimo mesmo
    # quando o corpo foi esvaziado pela limpeza (ex: encaminhamentos onde o único
    # conteúdo visível é a assinatura + cabeçalhos "De:/Assunto:" removidos pelo cleaner)
    header_context = f"Assunto: {subject}\nRemetente: {sender_email}"
    extracted_text = f"{header_context}\n\n{extracted_text}" if extracted_text else header_context

    # Create ParecerRequest
    parecer = ParecerRequest(
        id=uuid.uuid4(),
        gmail_thread_id=thread_id,
        gmail_message_id=message_id,
        sender_email=sender_email,
        subject=subject,
        municipio_id=municipio.id if municipio else None,
        extracted_text=extracted_text,
        extraction_status=ExtractionStatus.success if extracted_text else ExtractionStatus.partial,
        status=ParecerStatus.pendente,
        raw_payload={"source": "eml_upload", "original_from": from_header},
    )
    db.add(parecer)
    await db.flush()

    for rec in attachment_records:
        db.add(Attachment(request_id=parecer.id, **rec))

    await db.commit()
    await db.refresh(parecer)

    # Dispara pipeline P1 (classify) → P2 (generate) em background
    from app.services.pipeline import process_parecer_pipeline
    background_tasks.add_task(process_parecer_pipeline, str(parecer.id))

    return {
        "id": str(parecer.id),
        "subject": parecer.subject,
        "sender_email": parecer.sender_email,
        "municipio_id": str(parecer.municipio_id) if parecer.municipio_id else None,
        "attachments_count": len(attachment_records),
        "status": parecer.status,
    }


@router.get("/attachments/{attachment_id}/file")
async def download_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Serve the original attachment file."""
    result = await db.execute(
        select(AttachmentModel).where(AttachmentModel.id == attachment_id)
    )
    att = result.scalar_one_or_none()
    if not att:
        raise HTTPException(status_code=404, detail="Anexo não encontrado")
    if not att.storage_path or not os.path.exists(att.storage_path):
        raise HTTPException(status_code=404, detail="Arquivo não disponível")

    return FileResponse(
        path=att.storage_path,
        filename=att.filename,
        media_type=att.content_type or "application/octet-stream",
    )
