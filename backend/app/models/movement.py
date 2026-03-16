import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MovementType(str, enum.Enum):
    intimacao = "intimacao"
    sentenca = "sentenca"
    despacho = "despacho"
    acordao = "acordao"
    publicacao = "publicacao"
    distribuicao = "distribuicao"
    outros = "outros"


class Process(Base):
    __tablename__ = "processes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    municipio_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("municipios.id"), nullable=True, index=True)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    court: Mapped[str | None] = mapped_column(String(200), nullable=True)
    parties: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lawyers: Mapped[list["ProcessLawyer"]] = relationship("ProcessLawyer", back_populates="process")
    movements: Mapped[list["Movement"]] = relationship("Movement", back_populates="process", order_by="Movement.published_at.desc()")


class ProcessLawyer(Base):
    __tablename__ = "process_lawyers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    process: Mapped["Process"] = relationship("Process", back_populates="lawyers")


class Movement(Base):
    __tablename__ = "movements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False, index=True)
    dje_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    type: Mapped[MovementType] = mapped_column(Enum(MovementType, name="movement_type"), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    process: Mapped["Process"] = relationship("Process", back_populates="movements")

    __table_args__ = (
        Index("ix_movements_process_type", "process_id", "type"),
    )
