"""pipeline v4.1 — novos campos para rastreabilidade de IA

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # parecer_requests: classificação P1 e contador de revisões
    op.add_column("parecer_requests", sa.Column("classificacao", postgresql.JSONB(), nullable=True))
    op.add_column("parecer_requests", sa.Column("revisoes", sa.Integer(), nullable=False, server_default="0"))

    # parecer_versions: rastreabilidade de prompt e dados de qualidade
    op.add_column("parecer_versions", sa.Column("prompt_version", sa.String(10), nullable=True))
    op.add_column("parecer_versions", sa.Column("citacoes_verificar", postgresql.JSONB(), nullable=True))
    op.add_column("parecer_versions", sa.Column("ressalvas", postgresql.JSONB(), nullable=True))
    op.add_column("parecer_versions", sa.Column("notas_revisor", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("parecer_versions", "notas_revisor")
    op.drop_column("parecer_versions", "ressalvas")
    op.drop_column("parecer_versions", "citacoes_verificar")
    op.drop_column("parecer_versions", "prompt_version")
    op.drop_column("parecer_requests", "revisoes")
    op.drop_column("parecer_requests", "classificacao")
