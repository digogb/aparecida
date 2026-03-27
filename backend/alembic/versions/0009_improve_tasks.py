"""Improve tasks: add start_date, estimated_hours, tags, checklist; task_comments table.

Revision ID: 0009
Revises: 0008
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to tasks table
    op.add_column("tasks", sa.Column("start_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("estimated_hours", sa.Float(), nullable=True))
    op.add_column("tasks", sa.Column("tags", JSONB, nullable=True, server_default="[]"))
    op.add_column("tasks", sa.Column("checklist", JSONB, nullable=True, server_default="[]"))

    # Create task_comments table
    op.create_table(
        "task_comments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("task_comments")
    op.drop_column("tasks", "checklist")
    op.drop_column("tasks", "tags")
    op.drop_column("tasks", "estimated_hours")
    op.drop_column("tasks", "start_date")
