import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ParecerStatus(str, enum.Enum):
    pendente = "pendente"
    classificado = "classificado"
    gerado = "gerado"
    em_revisao = "em_revisao"
    devolvido = "devolvido"
    aprovado = "aprovado"
    enviado = "enviado"


class ParecerTema(str, enum.Enum):
    administrativo = "administrativo"
    tributario = "tributario"
    financeiro = "financeiro"
    previdenciario = "previdenciario"
    licitacao = "licitacao"


class ParecerModelo(str, enum.Enum):
    generico = "generico"
    licitacao = "licitacao"


class VersionSource(str, enum.Enum):
    ia_gerado = "ia_gerado"
    ia_reprocessado = "ia_reprocessado"
    manual_edit = "manual_edit"


class ExtractionMethod(str, enum.Enum):
    pdfplumber = "pdfplumber"
    python_docx = "python_docx"
    tesseract_ocr = "tesseract_ocr"
    fallback_libreoffice = "fallback_libreoffice"


class ExtractionStatus(str, enum.Enum):
    success = "success"
    failed = "failed"
    partial = "partial"


class ParecerRequest(Base):
    __tablename__ = "parecer_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    municipio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("municipios.id"), nullable=True, index=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    gmail_thread_id: Mapped[str | None] = mapped_column(String(200), nullable=True, unique=True)
    gmail_message_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sender_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_method: Mapped[ExtractionMethod | None] = mapped_column(Enum(ExtractionMethod, name="extraction_method"), nullable=True)
    extraction_status: Mapped[ExtractionStatus | None] = mapped_column(Enum(ExtractionStatus, name="extraction_status"), nullable=True)
    status: Mapped[ParecerStatus] = mapped_column(Enum(ParecerStatus, name="parecer_status"), nullable=False, default=ParecerStatus.pendente)
    tema: Mapped[ParecerTema | None] = mapped_column(Enum(ParecerTema, name="parecer_tema"), nullable=True)
    modelo: Mapped[ParecerModelo | None] = mapped_column(Enum(ParecerModelo, name="parecer_modelo"), nullable=True)
    numero_parecer: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    classificacao: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    revisoes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    versions: Mapped[list["ParecerVersion"]] = relationship("ParecerVersion", back_populates="request", order_by="ParecerVersion.version_number")
    attachments: Mapped[list["Attachment"]] = relationship("Attachment", back_populates="request")
    status_history: Mapped[list["ParecerStatusHistory"]] = relationship("ParecerStatusHistory", back_populates="request", order_by="ParecerStatusHistory.created_at")


class ParecerVersion(Base):
    __tablename__ = "parecer_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parecer_requests.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[VersionSource] = mapped_column(Enum(VersionSource, name="version_source"), nullable=False)
    content_tiptap: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    content_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    reprocess_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(10), nullable=True)
    citacoes_verificar: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ressalvas: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    notas_revisor: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    request: Mapped["ParecerRequest"] = relationship("ParecerRequest", back_populates="versions")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parecer_requests.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_method: Mapped[ExtractionMethod | None] = mapped_column(Enum(ExtractionMethod, name="extraction_method"), nullable=True)
    extraction_status: Mapped[ExtractionStatus | None] = mapped_column(Enum(ExtractionStatus, name="extraction_status"), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped["ParecerRequest"] = relationship("ParecerRequest", back_populates="attachments")


class ParecerStatusHistory(Base):
    __tablename__ = "parecer_status_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("parecer_requests.id"), nullable=False, index=True)
    from_status: Mapped[ParecerStatus | None] = mapped_column(Enum(ParecerStatus, name="parecer_status"), nullable=True)
    to_status: Mapped[ParecerStatus] = mapped_column(Enum(ParecerStatus, name="parecer_status"), nullable=False)
    changed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    request: Mapped["ParecerRequest"] = relationship("ParecerRequest", back_populates="status_history")
