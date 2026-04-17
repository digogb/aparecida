"""
Email worker: processes pending parecer_requests by fetching emails from Gmail,
extracting attachment content, identifying municipalities, and assembling text.
"""
from __future__ import annotations

import base64
import logging
import re
from typing import Any, Optional

from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
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

logger = logging.getLogger(__name__)
settings = Settings()

_GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ---------------------------------------------------------------------------
# Gmail client
# ---------------------------------------------------------------------------

def _build_gmail_service():
    """Build Gmail API service — OAuth2 (refresh token) ou Service Account."""
    if settings.GMAIL_REFRESH_TOKEN:
        from google.oauth2.credentials import Credentials

        creds = Credentials(
            token=None,
            refresh_token=settings.GMAIL_REFRESH_TOKEN,
            client_id=settings.GMAIL_CLIENT_ID,
            client_secret=settings.GMAIL_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_file(
        settings.GMAIL_CREDENTIALS_PATH,
        scopes=_GMAIL_SCOPES,
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _decode_b64(data: str) -> bytes:
    # Gmail uses URL-safe base64; pad to a multiple of 4
    return base64.urlsafe_b64decode(data + "==")


def _strip_html(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(separator="\n")


def _part_text(part: dict[str, Any]) -> str:
    data = part.get("body", {}).get("data", "")
    if not data:
        return ""
    raw = _decode_b64(data).decode("utf-8", errors="replace")
    if part.get("mimeType", "") == "text/html":
        return _strip_html(raw)
    return raw


def _walk_payload(payload: dict[str, Any]) -> str:
    """Recursively extract body text; prefers text/plain over text/html."""
    mime = payload.get("mimeType", "")
    parts = payload.get("parts", [])

    if mime == "text/plain":
        return _part_text(payload)
    if mime == "text/html" and not parts:
        return _part_text(payload)

    plain, html = "", ""
    for part in parts:
        sub = _walk_payload(part)
        if part.get("mimeType") == "text/plain":
            plain += sub
        elif part.get("mimeType") == "text/html":
            html += sub
        else:
            plain += sub  # multipart/* — accumulate into plain bucket

    return plain or html


def _collect_attachment_meta(
    payload: dict[str, Any],
    message_id: str,
    result: list[dict[str, Any]],
) -> None:
    """Walk the MIME tree and collect attachment metadata."""
    for part in payload.get("parts", []):
        filename = part.get("filename", "")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")
        if filename and attachment_id:
            result.append(
                {
                    "filename": filename,
                    "mime_type": part.get("mimeType", ""),
                    "size": body.get("size", 0),
                    "attachment_id": attachment_id,
                    "message_id": message_id,
                }
            )
        _collect_attachment_meta(part, message_id, result)


def _download_attachment_bytes(
    service, message_id: str, attachment_id: str
) -> bytes:
    att = (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )
    return _decode_b64(att.get("data", ""))


def _extract_domain(email: str) -> str:
    match = re.search(r"@([\w.-]+)", email)
    return match.group(1).lower() if match else ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def fetch_email(message_id: str) -> dict[str, Any]:
    """Fetch a Gmail message and return body, metadata, and attachment list.

    Returns a dict with keys:
      thread_id, message_id, subject, sender, body, attachments (list of meta dicts)
    """
    service = _build_gmail_service()
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    payload = msg.get("payload", {})
    headers = {
        h["name"].lower(): h["value"] for h in payload.get("headers", [])
    }

    body = _walk_payload(payload)

    attachments: list[dict[str, Any]] = []
    _collect_attachment_meta(payload, message_id, attachments)

    return {
        "thread_id": msg.get("threadId"),
        "message_id": message_id,
        "subject": headers.get("subject", ""),
        "sender": headers.get("from", ""),
        "body": body,
        "attachments": attachments,
    }


async def identify_municipio(
    email_domain: str, db: AsyncSession
) -> Optional[Municipio]:
    """Return the Municipio whose dominios_email list contains *email_domain*."""
    result = await db.execute(
        select(Municipio).where(Municipio.is_active.is_(True))
    )
    for municipio in result.scalars():
        domains = [d.lower() for d in (municipio.dominios_email or [])]
        if email_domain.lower() in domains:
            return municipio
    return None


async def process_pending_requests(db: AsyncSession) -> None:
    """Fetch and process every parecer_request with status='pendente'."""
    result = await db.execute(
        select(ParecerRequest).where(
            ParecerRequest.status == ParecerStatus.pendente
        )
    )
    pending = result.scalars().all()

    if not pending:
        return

    service = _build_gmail_service()

    for req in pending:
        if not req.gmail_message_id:
            continue

        try:
            email_data = await fetch_email(req.gmail_message_id)

            # Resolve municipality from sender domain if not already set
            if not req.municipio_id:
                domain = _extract_domain(email_data["sender"])
                if domain:
                    municipio = await identify_municipio(domain, db)
                    if municipio:
                        req.municipio_id = municipio.id

            # Update thread metadata
            req.gmail_thread_id = req.gmail_thread_id or email_data["thread_id"]
            req.subject = req.subject or email_data["subject"]
            req.sender_email = req.sender_email or email_data["sender"]

            # Download attachments, extract text, persist Attachment rows
            attachment_texts: list[str] = []
            for meta in email_data["attachments"]:
                file_bytes = _download_attachment_bytes(
                    service, meta["message_id"], meta["attachment_id"]
                )
                text, method, status = extract_file(meta["filename"], file_bytes)

                attachment = Attachment(
                    request_id=req.id,
                    filename=meta["filename"],
                    content_type=meta["mime_type"],
                    size_bytes=meta["size"],
                    extracted_text=text or None,
                    extraction_method=(
                        ExtractionMethod(method) if method else None
                    ),
                    extraction_status=ExtractionStatus(status),
                )
                db.add(attachment)

                if text:
                    attachment_texts.append(text)

            # Assemble final extracted text
            req.extracted_text = assemble(email_data["body"], attachment_texts)
            req.extraction_status = ExtractionStatus.success
            req.status = ParecerStatus.classificado

        except Exception:
            logger.exception(
                "Failed to process parecer_request %s", req.id
            )

    await db.commit()
