"""add erro to parecer_status enum

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE parecer_status ADD VALUE IF NOT EXISTS 'erro'")


def downgrade() -> None:
    # PostgreSQL não suporta remoção de valores de enum nativamente
    pass
