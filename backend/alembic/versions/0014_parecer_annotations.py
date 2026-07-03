"""anotações inline (marca + questionamento) — substitui peer review

Revision ID: 0014
Revises: 0013
Create Date: 2026-07-03

Nova tabela `parecer_annotations`: um advogado marca um trecho e escreve um
questionamento; qualquer advogado vê o realce (cor por autor) e o hint ao abrir o
parecer. Pertence ao request (persiste entre versões) e NÃO entra no content_tiptap.

As tabelas `peer_reviews`/`notifications` seguem no banco (dormentes) — o fluxo antigo
foi removido do frontend; dropar depois se desejado.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0014"
down_revision: str = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parecer_annotations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("request_id", UUID(as_uuid=True), sa.ForeignKey("parecer_requests.id"), nullable=False),
        sa.Column("author_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("trecho_texto", sa.Text(), nullable=False),
        sa.Column("questionamento", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_parecer_annotations_request_id", "parecer_annotations", ["request_id"])
    op.create_index("ix_parecer_annotations_author_id", "parecer_annotations", ["author_id"])


def downgrade() -> None:
    op.drop_index("ix_parecer_annotations_author_id", table_name="parecer_annotations")
    op.drop_index("ix_parecer_annotations_request_id", table_name="parecer_annotations")
    op.drop_table("parecer_annotations")
