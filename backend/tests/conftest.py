"""
Fixtures e helpers compartilhados entre todos os testes.
"""
from __future__ import annotations

import email.mime.base
import email.mime.multipart
import email.mime.text
import uuid
from datetime import datetime, timedelta, timezone
from email import encoders
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.database import get_db
from app.main import app
from app.models.parecer import (
    ExtractionStatus,
    ParecerStatus,
    ParecerTema,
    ParecerVersion,
    VersionSource,
)

# JWT secret padrão de config.py (dev)
_JWT_SECRET = "troque-isso-em-producao"
_JWT_ALG = "HS256"


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def make_token(
    user_id: str | None = None,
    email: str = "advogado@escritorio.com",
    role: str = "advogado",
    expires_delta: timedelta = timedelta(hours=8),
) -> str:
    uid = user_id or str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": uid, "email": email, "role": role, "exp": expire}
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALG)


def make_expired_token() -> str:
    return make_token(expires_delta=timedelta(hours=-1))


def make_tampered_token() -> str:
    token = make_token()
    return token[:-10] + "AAAAAAAAAA"


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Mock DB
# ---------------------------------------------------------------------------

def mock_db() -> AsyncMock:
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.flush = AsyncMock()
    db.delete = AsyncMock()
    return db


def override_db(db: AsyncMock):
    async def _dep():
        yield db
    return _dep


# ---------------------------------------------------------------------------
# Mock ORM objects
# ---------------------------------------------------------------------------

def mock_parecer(**overrides) -> MagicMock:
    """MagicMock que se comporta como ParecerRequest."""
    defaults = dict(
        id=uuid.uuid4(),
        municipio_id=None,
        assigned_to=None,
        gmail_thread_id=f"thread_{uuid.uuid4().hex[:8]}",
        gmail_message_id=f"msg_{uuid.uuid4().hex[:8]}",
        subject="Consulta sobre licitação",
        sender_email="prefeitura@municipio.sp.gov.br",
        status=ParecerStatus.pendente,
        tema=None,
        modelo=None,
        numero_parecer=None,
        extraction_status=ExtractionStatus.success,
        extracted_text="Texto extraído do email.",
        raw_payload={},
        classificacao=None,
        municipio_nome=None,
        revisoes=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        attachments=[],
        versions=[],
        status_history=[],
    )
    defaults.update(overrides)
    m = MagicMock()
    for k, v in defaults.items():
        setattr(m, k, v)
    return m


def mock_version(request_id=None, version_number=1, **overrides) -> MagicMock:
    """MagicMock que se comporta como ParecerVersion."""
    defaults = dict(
        id=uuid.uuid4(),
        request_id=request_id or uuid.uuid4(),
        version_number=version_number,
        source=VersionSource.ia_gerado,
        content_html="<h2>EMENTA</h2><p>Teste</p>",
        content_tiptap={"type": "doc", "content": []},
        prompt_version="v1",
        citacoes_verificar=[],
        ressalvas=[],
        notas_revisor=[],
        reprocess_instructions=None,
        created_by=None,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    m = MagicMock()
    for k, v in defaults.items():
        setattr(m, k, v)
    return m


def mock_user(**overrides) -> MagicMock:
    """MagicMock que se comporta como User."""
    from app.models.user import UserRole
    defaults = dict(
        id=uuid.uuid4(),
        name="Dr. Advogado Teste",
        email="advogado@escritorio.com",
        hashed_password="$2b$12$fake_hash",
        role=UserRole.advogado,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    m = MagicMock()
    for k, v in defaults.items():
        setattr(m, k, v)
    return m


# ---------------------------------------------------------------------------
# .eml builders
# ---------------------------------------------------------------------------

def build_eml(
    subject: str = "Consulta jurídica sobre licitação",
    from_addr: str = "prefeitura@municipio.sp.gov.br",
    body: str = "Solicitamos parecer sobre pregão eletrônico 01/2026.",
    message_id: str | None = None,
    in_reply_to: str | None = None,
) -> bytes:
    msg = email.mime.multipart.MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = "escritorio@advocacia.com"
    msg["Message-ID"] = message_id or f"<{uuid.uuid4()}@municipio.sp.gov.br>"
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    msg.attach(email.mime.text.MIMEText(body, "plain", "utf-8"))
    return msg.as_bytes()


def build_eml_with_attachment(
    attachment_filename: str,
    attachment_content: bytes = b"conteudo do arquivo",
    **kwargs,
) -> bytes:
    msg = email.mime.multipart.MIMEMultipart()
    msg["Subject"] = kwargs.get("subject", "Consulta jurídica")
    msg["From"] = kwargs.get("from_addr", "prefeitura@municipio.sp.gov.br")
    msg["Message-ID"] = kwargs.get("message_id", f"<{uuid.uuid4()}@test>")
    msg.attach(email.mime.text.MIMEText("Segue em anexo.", "plain"))

    part = email.mime.base.MIMEBase("application", "octet-stream")
    part.set_payload(attachment_content)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{attachment_filename}"')
    msg.attach(part)
    return msg.as_bytes()


# ---------------------------------------------------------------------------
# Shared client fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
