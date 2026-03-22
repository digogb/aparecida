"""Add sent_to_email to parecer_requests.

Revision ID: 0007
Revises: 0006
"""

from alembic import op
import sqlalchemy as sa

revision: str = "0007"
down_revision: str = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "parecer_requests",
        sa.Column("sent_to_email", sa.String(200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("parecer_requests", "sent_to_email")
