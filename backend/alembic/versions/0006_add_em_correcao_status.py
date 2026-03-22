"""add em_correcao to parecer_status enum

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE parecer_status ADD VALUE IF NOT EXISTS 'em_correcao'")


def downgrade() -> None:
    # PostgreSQL não suporta remoção de valores de enum nativamente
    pass
