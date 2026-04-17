"""add system_config table

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-17
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_config",
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text, nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("system_config")
