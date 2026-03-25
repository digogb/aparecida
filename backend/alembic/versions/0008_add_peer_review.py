"""Add peer_reviews table and peer_review version source.

Revision ID: 0008
Revises: 0007
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new value to version_source enum
    op.execute("ALTER TYPE version_source ADD VALUE IF NOT EXISTS 'peer_review'")

    # Create peer_review_status enum
    op.execute(
        "CREATE TYPE peer_review_status AS ENUM ('pendente', 'concluida', 'cancelada')"
    )

    # Create peer_reviews table
    op.create_table(
        "peer_reviews",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "request_id",
            UUID(as_uuid=True),
            sa.ForeignKey("parecer_requests.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "version_id",
            UUID(as_uuid=True),
            sa.ForeignKey("parecer_versions.id"),
            nullable=False,
        ),
        sa.Column(
            "requested_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "reviewer_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "status",
            sa.Enum("pendente", "concluida", "cancelada", name="peer_review_status"),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("trechos_marcados", JSONB, nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        sa.Column("resposta_geral", sa.Text, nullable=True),
        sa.Column("resposta_trechos", JSONB, nullable=True),
        sa.Column(
            "result_version_id",
            UUID(as_uuid=True),
            sa.ForeignKey("parecer_versions.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("peer_reviews")
    op.execute("DROP TYPE IF EXISTS peer_review_status")
