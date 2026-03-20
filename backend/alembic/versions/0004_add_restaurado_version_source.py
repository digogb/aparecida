"""add restaurado to version_source enum

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE version_source ADD VALUE IF NOT EXISTS 'restaurado'")


def downgrade() -> None:
    pass
