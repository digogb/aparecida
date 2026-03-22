"""Simplify parecer_tema enum to administrativo + licitacao only.

Revision ID: 0005
Revises: 0004_add_restaurado_version_source
"""

from alembic import op

revision: str = "0005"
down_revision: str = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE parecer_requests ALTER COLUMN tema TYPE text")
    op.execute("DROP TYPE parecer_tema")
    op.execute("CREATE TYPE parecer_tema AS ENUM ('administrativo', 'licitacao')")
    op.execute("""
        ALTER TABLE parecer_requests
        ALTER COLUMN tema TYPE parecer_tema USING tema::parecer_tema
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE parecer_requests ALTER COLUMN tema TYPE text")
    op.execute("DROP TYPE parecer_tema")
    op.execute(
        "CREATE TYPE parecer_tema AS ENUM "
        "('administrativo', 'tributario', 'financeiro', 'previdenciario', 'licitacao')"
    )
    op.execute("""
        ALTER TABLE parecer_requests
        ALTER COLUMN tema TYPE parecer_tema USING tema::parecer_tema
    """)
