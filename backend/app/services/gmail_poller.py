"""
Gmail inbox poller: verifica periodicamente o Gmail por novas mensagens
e cria ParecerRequests automaticamente.

Fluxo:
  1. Lê o último historyId salvo em system_config
  2. Chama history.list para obter mensagens adicionadas desde então
  3. Para cada mensagem nova no INBOX: extrai corpo + anexos, cria ParecerRequest
  4. Atualiza o historyId no banco
  5. Dispara o pipeline P1→P2 em background
"""
from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.models.municipio import Municipio
from app.models.parecer import (
    Attachment,
    ExtractionMethod,
    ExtractionStatus,
    ParecerRequest,
    ParecerStatus,
)
from app.models.system_config import SystemConfig
from app.services.content_assembler import assemble
from app.services.extractor import extract_file

logger = logging.getLogger(__name__)

_HISTORY_KEY = "gmail_last_history_id"
_GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
_UPLOADS_DIR = Path("/app/uploads")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def _build_service():
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

    creds_path = Path(settings.GMAIL_CREDENTIALS_PATH)
    if creds_path.exists():
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(
            str(creds_path), scopes=_GMAIL_SCOPES
        )
        if settings.GMAIL_SENDER_EMAIL:
            creds = creds.with_subject(settings.GMAIL_SENDER_EMAIL)
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    raise ValueError(
        "Gmail não configurado. Defina GMAIL_REFRESH_TOKEN (OAuth2) "
        "ou GMAIL_CREDENTIALS_PATH (Service Account)."
    )


def _is_configured() -> bool:
    return bool(settings.GMAIL_REFRESH_TOKEN or Path(settings.GMAIL_CREDENTIALS_PATH).exists())


# ---------------------------------------------------------------------------
# Message parsing (sync — Google client is sync)
# ---------------------------------------------------------------------------

import base64


def _decode_b64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "==")


def _strip_html(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(separator="\n")


def _walk_payload(payload: dict[str, Any]) -> str:
    mime = payload.get("mimeType", "")
    parts = payload.get("parts", [])

    if mime == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            raw = _decode_b64(data).decode("utf-8", errors="replace")
            return raw

    if mime == "text/html" and not parts:
        data = payload.get("body", {}).get("data", "")
        if data:
            raw = _decode_b64(data).decode("utf-8", errors="replace")
            return _strip_html(raw)

    plain, html = "", ""
    for part in parts:
        sub = _walk_payload(part)
        if part.get("mimeType") == "text/plain":
            plain += sub
        elif part.get("mimeType") == "text/html":
            html += sub
        else:
            plain += sub

    return plain or html


def _collect_attachments(
    payload: dict[str, Any],
    message_id: str,
    result: list[dict[str, Any]],
) -> None:
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
        _collect_attachments(part, message_id, result)


def _download_attachment(service, message_id: str, attachment_id: str) -> bytes:
    att = (
        service.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )
    return _decode_b64(att.get("data", ""))


def _extract_domain(email_addr: str) -> str:
    match = re.search(r"@([\w.-]+)", email_addr)
    return match.group(1).lower() if match else ""


def _extract_sender_email(from_header: str) -> str:
    match = re.search(r"<([^>]+)>", from_header)
    if match:
        return match.group(1).strip().lower()
    return from_header.strip().lower()


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

async def _get_or_create_config(db: AsyncSession, key: str) -> SystemConfig:
    result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
    cfg = result.scalar_one_or_none()
    if cfg is None:
        cfg = SystemConfig(key=key, value=None)
        db.add(cfg)
    return cfg


async def _identify_municipio(domain: str, db: AsyncSession) -> Municipio | None:
    result = await db.execute(select(Municipio).where(Municipio.is_active.is_(True)))
    for m in result.scalars():
        domains = [d.lower() for d in (m.dominios_email or [])]
        if domain in domains:
            return m
    return None


async def _already_imported(thread_id: str, message_id: str, db: AsyncSession) -> bool:
    result = await db.execute(
        select(ParecerRequest).where(
            (ParecerRequest.gmail_thread_id == thread_id)
            | (ParecerRequest.gmail_message_id == message_id)
        )
    )
    return result.scalar_one_or_none() is not None


async def _ingest_message(
    service,
    message_id: str,
    thread_id: str,
    db: AsyncSession,
) -> bool:
    """Fetch a Gmail message, create ParecerRequest, trigger pipeline. Returns True if created."""
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    payload = msg.get("payload", {})
    headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}

    subject_raw = headers.get("subject", "")
    subject = re.sub(r"^(ENC|FWD|RES|RE|FW):\s*", "", subject_raw, flags=re.IGNORECASE).strip()
    from_header = headers.get("from", "")
    sender_email = _extract_sender_email(from_header)
    domain = _extract_domain(sender_email)

    body = _walk_payload(payload)

    attachment_metas: list[dict[str, Any]] = []
    _collect_attachments(payload, message_id, attachment_metas)

    attachment_texts: list[str] = []
    attachment_records: list[dict] = []

    _UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    for meta in attachment_metas:
        try:
            file_bytes = _download_attachment(service, meta["message_id"], meta["attachment_id"])
            text, method, status = extract_file(meta["filename"], file_bytes)

            safe_name = re.sub(r"[^\w.\-]", "_", meta["filename"])
            file_id = uuid.uuid4()
            storage_path = str(_UPLOADS_DIR / f"{file_id}_{safe_name}")
            with open(storage_path, "wb") as f:
                f.write(file_bytes)

            attachment_records.append(
                {
                    "filename": meta["filename"],
                    "content_type": meta["mime_type"],
                    "size_bytes": meta["size"],
                    "extracted_text": text or None,
                    "extraction_method": ExtractionMethod(method) if method else None,
                    "extraction_status": ExtractionStatus(status),
                    "storage_path": storage_path,
                }
            )
            if text:
                attachment_texts.append(text)
        except Exception:
            logger.exception("Gmail poller: falha ao processar anexo %s", meta["filename"])

    extracted_text = assemble(body, attachment_texts)
    header_context = f"Assunto: {subject}\nRemetente: {sender_email}"
    extracted_text = f"{header_context}\n\n{extracted_text}" if extracted_text else header_context

    municipio = await _identify_municipio(domain, db) if domain else None

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
        raw_payload={"source": "gmail_polling", "original_from": from_header},
    )
    db.add(parecer)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        logger.info(
            "Gmail poller: mensagem %s (thread %s) já importada por outra instância — ignorando",
            message_id,
            thread_id,
        )
        return False

    for rec in attachment_records:
        db.add(Attachment(request_id=parecer.id, **rec))

    await db.commit()
    await db.refresh(parecer)

    from app.services.notification import notify_parecer_event
    from app.services.pipeline import process_parecer_pipeline

    await notify_parecer_event("parecer.created", parecer.id, "pendente")
    await process_parecer_pipeline(str(parecer.id))

    logger.info(
        "Gmail poller: criado parecer %s — %s (%s)",
        parecer.id,
        subject,
        sender_email,
    )
    return True


# ---------------------------------------------------------------------------
# Backlog recovery (historyId expirado)
# ---------------------------------------------------------------------------

async def _recover_unread_backlog(service, db: AsyncSession) -> int:
    """
    Chamado quando o historyId expira (sistema offline > 7 dias).
    Busca todos os emails não lidos no INBOX dos últimos 30 dias e importa
    os que ainda não foram processados.
    """
    count = 0
    page_token = None

    while True:
        kwargs: dict = {
            "userId": "me",
            "q": "in:INBOX is:unread newer_than:30d",
            "maxResults": 100,
        }
        if page_token:
            kwargs["pageToken"] = page_token

        resp = service.users().messages().list(**kwargs).execute()
        messages = resp.get("messages", [])

        for msg in messages:
            message_id = msg["id"]
            thread_id = msg.get("threadId", message_id)

            if await _already_imported(thread_id, message_id, db):
                continue
            try:
                created = await _ingest_message(service, message_id, thread_id, db)
                if created:
                    count += 1
            except Exception:
                logger.exception(
                    "Gmail poller (backlog): erro ao ingerir mensagem %s", message_id
                )
                await db.rollback()

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    if count:
        logger.info("Gmail poller: backlog recuperado — %d parecer(es) criado(s)", count)

    return count


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def poll_inbox() -> int:
    """
    Verifica novas mensagens no Gmail desde o último polling.
    Retorna o número de ParecerRequests criados.
    """
    if not _is_configured():
        logger.debug("Gmail poller: credenciais não configuradas, pulando")
        return 0

    try:
        service = _build_service()
    except ValueError as exc:
        logger.warning("Gmail poller: %s", exc)
        return 0

    async with async_session() as db:
        cfg = await _get_or_create_config(db, _HISTORY_KEY)

        if not cfg.value:
            # Primeira execução: registra historyId atual e sai sem importar backlog
            profile = service.users().getProfile(userId="me").execute()
            cfg.value = str(profile.get("historyId", "1"))
            cfg.updated_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info("Gmail poller: inicializado com historyId=%s", cfg.value)
            return 0

        last_history_id = cfg.value

        try:
            resp = (
                service.users()
                .history()
                .list(
                    userId="me",
                    startHistoryId=last_history_id,
                    labelId="INBOX",
                    historyTypes=["messageAdded"],
                )
                .execute()
            )
        except Exception as exc:
            error_str = str(exc)
            # historyId expira após ~7 dias sem atividade
            if "startHistoryId" in error_str or "404" in error_str or "400" in error_str:
                logger.warning(
                    "Gmail poller: historyId %s expirado — recuperando backlog de não lidos",
                    last_history_id,
                )
                count = await _recover_unread_backlog(service, db)
                profile = service.users().getProfile(userId="me").execute()
                cfg.value = str(profile.get("historyId", "1"))
                cfg.updated_at = datetime.now(timezone.utc)
                await db.commit()
                return count
            else:
                logger.exception("Gmail poller: erro ao consultar history.list")
            return 0

        new_history_id = resp.get("historyId", last_history_id)
        history_records = resp.get("history", [])

        # Coleta IDs únicos de mensagens adicionadas ao INBOX
        message_ids: dict[str, str] = {}  # message_id → thread_id
        for record in history_records:
            for added in record.get("messagesAdded", []):
                msg = added.get("message", {})
                labels = msg.get("labelIds", [])
                if "INBOX" in labels and "TRASH" not in labels and "SPAM" not in labels:
                    message_ids[msg["id"]] = msg.get("threadId", msg["id"])

        count = 0
        for message_id, thread_id in message_ids.items():
            if await _already_imported(thread_id, message_id, db):
                continue
            try:
                created = await _ingest_message(service, message_id, thread_id, db)
                if created:
                    count += 1
            except Exception:
                logger.exception(
                    "Gmail poller: erro ao ingerir mensagem %s", message_id
                )
                await db.rollback()

        cfg.value = str(new_history_id)
        cfg.updated_at = datetime.now(timezone.utc)
        await db.commit()

        if count:
            logger.info("Gmail poller: %d novo(s) parecer(es) criado(s)", count)

        return count
