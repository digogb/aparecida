"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums — DO block ignora duplicate_object silenciosamente
    enums = [
        "CREATE TYPE user_role AS ENUM ('advogado', 'secretaria', 'admin')",
        "CREATE TYPE parecer_status AS ENUM ('pendente', 'classificado', 'gerado', 'em_revisao', 'devolvido', 'aprovado', 'enviado')",
        "CREATE TYPE parecer_tema AS ENUM ('administrativo', 'tributario', 'financeiro', 'previdenciario', 'licitacao')",
        "CREATE TYPE parecer_modelo AS ENUM ('generico', 'licitacao')",
        "CREATE TYPE version_source AS ENUM ('ia_gerado', 'ia_reprocessado', 'manual_edit')",
        "CREATE TYPE extraction_method AS ENUM ('pdfplumber', 'python_docx', 'tesseract_ocr', 'fallback_libreoffice')",
        "CREATE TYPE extraction_status AS ENUM ('success', 'failed', 'partial')",
        "CREATE TYPE movement_type AS ENUM ('intimacao', 'sentenca', 'despacho', 'acordao', 'publicacao', 'distribuicao', 'outros')",
        "CREATE TYPE task_category AS ENUM ('judicial', 'administrativa', 'parecer', 'publicacao_dje', 'prazo')",
        "CREATE TYPE task_priority AS ENUM ('high', 'medium', 'low')",
        "CREATE TYPE notification_channel AS ENUM ('in_app', 'email')",
        "CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'read')",
    ]
    for stmt in enums:
        op.execute(sa.text(f"DO $$ BEGIN {stmt}; EXCEPTION WHEN duplicate_object THEN NULL; END $$"))

    # Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("role", postgresql.ENUM("advogado", "secretaria", "admin", name="user_role", create_type=False), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # Municipios
    op.create_table(
        "municipios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("dominios_email", postgresql.ARRAY(sa.String), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Parecer Requests
    op.create_table(
        "parecer_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("municipio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("municipios.id"), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("gmail_thread_id", sa.String(200), nullable=True, unique=True),
        sa.Column("gmail_message_id", sa.String(200), nullable=True),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("sender_email", sa.String(200), nullable=True),
        sa.Column("extracted_text", sa.Text, nullable=True),
        sa.Column("extraction_method", postgresql.ENUM("pdfplumber", "python_docx", "tesseract_ocr", "fallback_libreoffice", name="extraction_method", create_type=False), nullable=True),
        sa.Column("extraction_status", postgresql.ENUM("success", "failed", "partial", name="extraction_status", create_type=False), nullable=True),
        sa.Column("status", postgresql.ENUM("pendente", "classificado", "gerado", "em_revisao", "devolvido", "aprovado", "enviado", name="parecer_status", create_type=False), nullable=False, server_default="pendente"),
        sa.Column("tema", postgresql.ENUM("administrativo", "tributario", "financeiro", "previdenciario", "licitacao", name="parecer_tema", create_type=False), nullable=True),
        sa.Column("modelo", postgresql.ENUM("generico", "licitacao", name="parecer_modelo", create_type=False), nullable=True),
        sa.Column("numero_parecer", sa.String(50), nullable=True, unique=True),
        sa.Column("raw_payload", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_parecer_requests_municipio_id", "parecer_requests", ["municipio_id"])
    op.create_index("ix_parecer_requests_assigned_to", "parecer_requests", ["assigned_to"])

    # Parecer Versions
    op.create_table(
        "parecer_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("parecer_requests.id"), nullable=False),
        sa.Column("version_number", sa.Integer, nullable=False),
        sa.Column("source", postgresql.ENUM("ia_gerado", "ia_reprocessado", "manual_edit", name="version_source", create_type=False), nullable=False),
        sa.Column("content_tiptap", postgresql.JSONB, nullable=True),
        sa.Column("content_html", sa.Text, nullable=True),
        sa.Column("reprocess_instructions", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_parecer_versions_request_id", "parecer_versions", ["request_id"])

    # Attachments
    op.create_table(
        "attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("parecer_requests.id"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column("size_bytes", sa.Integer, nullable=True),
        sa.Column("extracted_text", sa.Text, nullable=True),
        sa.Column("extraction_method", postgresql.ENUM("pdfplumber", "python_docx", "tesseract_ocr", "fallback_libreoffice", name="extraction_method", create_type=False), nullable=True),
        sa.Column("extraction_status", postgresql.ENUM("success", "failed", "partial", name="extraction_status", create_type=False), nullable=True),
        sa.Column("storage_path", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_attachments_request_id", "attachments", ["request_id"])

    # Parecer Status History
    op.create_table(
        "parecer_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("parecer_requests.id"), nullable=False),
        sa.Column("from_status", postgresql.ENUM("pendente", "classificado", "gerado", "em_revisao", "devolvido", "aprovado", "enviado", name="parecer_status", create_type=False), nullable=True),
        sa.Column("to_status", postgresql.ENUM("pendente", "classificado", "gerado", "em_revisao", "devolvido", "aprovado", "enviado", name="parecer_status", create_type=False), nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_parecer_status_history_request_id", "parecer_status_history", ["request_id"])

    # Processes
    op.create_table(
        "processes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("number", sa.String(50), nullable=False, unique=True),
        sa.Column("municipio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("municipios.id"), nullable=True),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("court", sa.String(200), nullable=True),
        sa.Column("parties", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_processes_number", "processes", ["number"])
    op.create_index("ix_processes_municipio_id", "processes", ["municipio_id"])

    # Process Lawyers
    op.create_table(
        "process_lawyers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("processes.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_process_lawyers_process_id", "process_lawyers", ["process_id"])
    op.create_index("ix_process_lawyers_user_id", "process_lawyers", ["user_id"])

    # Movements
    op.create_table(
        "movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("processes.id"), nullable=False),
        sa.Column("dje_id", sa.String(100), nullable=True, unique=True),
        sa.Column("type", postgresql.ENUM("intimacao", "sentenca", "despacho", "acordao", "publicacao", "distribuicao", "outros", name="movement_type", create_type=False), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_movements_process_id", "movements", ["process_id"])
    op.create_index("ix_movements_process_type", "movements", ["process_id", "type"])

    # Boards
    op.create_table(
        "boards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Columns
    op.create_table(
        "columns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("board_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("boards.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("wip_limit", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_columns_board_id", "columns", ["board_id"])

    # Tasks
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("column_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("columns.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", postgresql.ENUM("judicial", "administrativa", "parecer", "publicacao_dje", "prazo", name="task_category", create_type=False), nullable=True),
        sa.Column("priority", postgresql.ENUM("high", "medium", "low", name="task_priority", create_type=False), nullable=False, server_default="medium"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
        sa.Column("source_ref", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tasks_column_id", "tasks", ["column_id"])
    op.create_index("ix_tasks_assigned_to", "tasks", ["assigned_to"])

    # Task History
    op.create_table(
        "task_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("from_column_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("columns.id"), nullable=True),
        sa.Column("to_column_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("columns.id"), nullable=True),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_task_history_task_id", "task_history", ["task_id"])

    # Notifications
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("channel", postgresql.ENUM("in_app", "email", name="notification_channel", create_type=False), nullable=False),
        sa.Column("status", postgresql.ENUM("pending", "sent", "read", name="notification_status", create_type=False), nullable=False, server_default="pending"),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    # Holidays
    op.create_table(
        "holidays",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("national", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("comarca", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_holidays_date", "holidays", ["date"])


def downgrade() -> None:
    op.drop_table("holidays")
    op.drop_table("notifications")
    op.drop_table("task_history")
    op.drop_table("tasks")
    op.drop_table("columns")
    op.drop_table("boards")
    op.drop_table("movements")
    op.drop_table("process_lawyers")
    op.drop_table("processes")
    op.drop_table("parecer_status_history")
    op.drop_table("attachments")
    op.drop_table("parecer_versions")
    op.drop_table("parecer_requests")
    op.drop_table("municipios")
    op.drop_table("users")

    for enum_name in [
        "user_role", "parecer_status", "parecer_tema", "parecer_modelo",
        "version_source", "extraction_method", "extraction_status",
        "movement_type", "task_category", "task_priority",
        "notification_channel", "notification_status",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
