"""
Email sender: sends parecer DOCX as a Gmail reply on the original thread.
"""
from __future__ import annotations

import base64
import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.parecer import ParecerRequest, ParecerStatus, ParecerStatusHistory

logger = logging.getLogger(__name__)

_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def _build_gmail_service():
    creds = service_account.Credentials.from_service_account_file(
        settings.GMAIL_CREDENTIALS_PATH,
        scopes=_GMAIL_SCOPES,
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _build_email_body(req: ParecerRequest) -> str:
    """Build formal reply body text."""
    subject = req.subject or "Consulta Jurídica"
    numero = req.numero_parecer or "S/N"

    return (
        f"Prezado(a),\n\n"
        f"Segue em anexo o Parecer Jurídico nº {numero}, "
        f'referente à consulta "{subject}".\n\n'
        f"O documento encontra-se em formato DOCX para sua conveniência.\n\n"
        f"Permanecemos à disposição para eventuais esclarecimentos.\n\n"
        f"Atenciosamente,\n"
        f"Ione Advogados & Associados\n"
        f"Assessoria Jurídica em Direito Público Municipal"
    )


async def send_parecer(
    parecer_request: ParecerRequest,
    docx_bytes: bytes,
    db: AsyncSession,
    changed_by_id: str | None = None,
) -> None:
    """Send the parecer DOCX as a reply in the original Gmail thread.

    Updates parecer_request.status to 'enviado' and records
    the transition in parecer_status_history.
    """
    if not parecer_request.sender_email:
        raise ValueError("ParecerRequest sem sender_email — nao e possivel enviar.")

    service = _build_gmail_service()

    # Build MIME message
    msg = MIMEMultipart()
    msg["To"] = parecer_request.sender_email
    msg["Subject"] = f"Re: {parecer_request.subject or 'Parecer Jurídico'}"

    # References / In-Reply-To for threading
    if parecer_request.gmail_message_id:
        msg["In-Reply-To"] = parecer_request.gmail_message_id
        msg["References"] = parecer_request.gmail_message_id

    # Body
    body_text = _build_email_body(parecer_request)
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    # DOCX attachment
    filename = f"Parecer_{parecer_request.numero_parecer or 'SN'}.docx"
    attachment = MIMEApplication(
        docx_bytes,
        _subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)

    # Encode and send
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")

    send_body: dict = {"raw": raw}
    if parecer_request.gmail_thread_id:
        send_body["threadId"] = parecer_request.gmail_thread_id

    service.users().messages().send(userId="me", body=send_body).execute()

    logger.info(
        "Parecer %s enviado para %s",
        parecer_request.id,
        parecer_request.sender_email,
    )

    # Update status
    old_status = parecer_request.status
    parecer_request.status = ParecerStatus.enviado

    db.add(
        ParecerStatusHistory(
            request_id=parecer_request.id,
            from_status=old_status,
            to_status=ParecerStatus.enviado,
            changed_by=changed_by_id,
            notes="Parecer enviado por email",
        )
    )

    await db.commit()
    await db.refresh(parecer_request)
