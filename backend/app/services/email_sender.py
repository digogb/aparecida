"""
Email sender: sends parecer DOCX+PDF as a Gmail reply on the original thread.

Suporta dois modos de autenticação:
- OAuth2 refresh token (para teste / Gmail pessoal) — preferido
- Service Account com domain-wide delegation (para produção com Google Workspace)
"""
from __future__ import annotations

import base64
import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.parecer import ParecerRequest, ParecerStatus, ParecerStatusHistory

logger = logging.getLogger(__name__)

_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
]


def _build_gmail_service():
    """Build Gmail API service — OAuth2 (refresh token) ou Service Account."""

    # Modo 1: OAuth2 com refresh token (teste / Gmail pessoal)
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

    # Modo 2: Service Account (produção / Google Workspace)
    creds_path = Path(settings.GMAIL_CREDENTIALS_PATH)
    if creds_path.exists():
        from google.oauth2 import service_account

        creds = service_account.Credentials.from_service_account_file(
            str(creds_path),
            scopes=_GMAIL_SCOPES,
        )
        if settings.GMAIL_SENDER_EMAIL:
            creds = creds.with_subject(settings.GMAIL_SENDER_EMAIL)
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    raise ValueError(
        "Gmail nao configurado. Defina GMAIL_REFRESH_TOKEN (OAuth2) "
        "ou GMAIL_CREDENTIALS_PATH (Service Account) no .env"
    )


def _build_email_body(req: ParecerRequest) -> str:
    """Build formal reply body text."""
    subject = req.subject or "Consulta Jurídica"
    numero = req.numero_parecer or "S/N"
    classificacao = req.classificacao or {}
    municipio = classificacao.get("municipio", "")
    consulente = classificacao.get("consulente", "")

    # Saudação: usar nome do consulente se disponível, senão município
    if consulente:
        saudacao = f"Prezado(a) {consulente}"
    elif municipio:
        saudacao = f"Prezado(a) Senhor(a) — Município de {municipio}"
    else:
        saudacao = "Prezado(a) Senhor(a)"

    return (
        f"{saudacao},\n\n"
        f"Segue em anexo o Parecer Jurídico nº {numero}, "
        f'referente à consulta "{subject}".\n\n'
        f"O documento encontra-se em formato DOCX e PDF para sua conveniência. "
        f"Caso necessite de alguma correção ou esclarecimento adicional, "
        f"solicitamos que responda a este e-mail.\n\n"
        f"Permanecemos à disposição.\n\n"
        f"Atenciosamente,\n\n"
        f"Ione Advogados & Associados\n"
        f"Assessoria Jurídica em Direito Público Municipal\n"
        f"─────────────────────────────────\n"
        f"Rua Gen. Caiado de Castro 462, Luciano Cavalcante\n"
        f"Fortaleza/CE — CEP 60.810-280\n"
        f"Tel: (85) 3021-7701 | (85) 99981-4392 | (85) 99223-6716\n"
        f"E-mail: dr.ione@uol.com.br"
    )


async def send_parecer(
    parecer_request: ParecerRequest,
    docx_bytes: bytes,
    pdf_bytes: bytes,
    db: AsyncSession,
    changed_by_id: str | None = None,
) -> None:
    """Send the parecer (DOCX + PDF) as a reply in the original Gmail thread.

    Updates parecer_request.status to 'enviado' and records
    the transition in parecer_status_history.
    """
    if not parecer_request.sender_email:
        raise ValueError("ParecerRequest sem sender_email — nao e possivel enviar.")

    service = _build_gmail_service()

    # Build MIME message
    msg = MIMEMultipart()
    if settings.GMAIL_SENDER_EMAIL:
        msg["From"] = settings.GMAIL_SENDER_EMAIL
    # Em teste, redireciona todos os emails para o destinatário de teste
    recipient = settings.GMAIL_TEST_RECIPIENT or parecer_request.sender_email
    msg["To"] = recipient
    msg["Subject"] = f"Re: {parecer_request.subject or 'Parecer Jurídico'}"

    # References / In-Reply-To for threading
    if parecer_request.gmail_message_id:
        msg["In-Reply-To"] = parecer_request.gmail_message_id
        msg["References"] = parecer_request.gmail_message_id

    # Body
    body_text = _build_email_body(parecer_request)
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    # DOCX attachment
    base_filename = f"Parecer_{parecer_request.numero_parecer or 'SN'}"
    docx_att = MIMEApplication(
        docx_bytes,
        _subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    docx_att.add_header("Content-Disposition", "attachment", filename=f"{base_filename}.docx")
    msg.attach(docx_att)

    # PDF attachment
    pdf_att = MIMEApplication(pdf_bytes, _subtype="pdf")
    pdf_att.add_header("Content-Disposition", "attachment", filename=f"{base_filename}.pdf")
    msg.attach(pdf_att)

    # Encode and send
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")

    send_body: dict = {"raw": raw}
    if parecer_request.gmail_thread_id:
        send_body["threadId"] = parecer_request.gmail_thread_id

    try:
        service.users().messages().send(userId="me", body=send_body).execute()
    except Exception:
        if "threadId" in send_body:
            logger.warning(
                "Envio com threadId falhou — reenviando sem thread para %s",
                parecer_request.id,
            )
            del send_body["threadId"]
            service.users().messages().send(userId="me", body=send_body).execute()
        else:
            raise

    logger.info(
        "Parecer %s enviado para %s%s",
        parecer_request.id,
        recipient,
        " (teste)" if settings.GMAIL_TEST_RECIPIENT else "",
    )

    # Update status
    old_status = parecer_request.status
    parecer_request.status = ParecerStatus.enviado
    parecer_request.sent_to_email = recipient

    db.add(
        ParecerStatusHistory(
            request_id=parecer_request.id,
            from_status=old_status,
            to_status=ParecerStatus.enviado,
            changed_by=changed_by_id,
            notes=f"Parecer enviado por email para {recipient}",
        )
    )

    await db.commit()
    await db.refresh(parecer_request)
