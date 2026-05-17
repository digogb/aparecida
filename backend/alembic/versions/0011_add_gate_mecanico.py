"""add gate_mecanico fields to parecer_versions

Revision ID: 0011
Revises: 0010
Create Date: 2026-05-17

Camada 4 do pipeline v5.0: persiste o resultado do auditor mecânico (IRR-1 + IRR-2)
para cada versão do parecer.
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "0011"
down_revision: str = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NULL = versão antiga, anterior ao gate (compatibilidade)
    op.add_column(
        "parecer_versions",
        sa.Column("gate_mecanico_passed", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "parecer_versions",
        sa.Column("gate_mecanico_log", JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("parecer_versions", "gate_mecanico_log")
    op.drop_column("parecer_versions", "gate_mecanico_passed")
