"""dedup por gmail_message_id; thread vira agrupador (requests "irmãos")

Revision ID: 0013
Revises: 0012
Create Date: 2026-07-01

Antes, `ParecerRequest.gmail_thread_id` era UNIQUE, então qualquer resposta nova numa
thread já importada era descartada pelo poller/ingest — mesmo trazendo documentos novos.
Agora o dedup passa a ser por `gmail_message_id` (UNIQUE): cada mensagem relevante vira um
request próprio, e a thread passa a ser só um agrupador (índice não-único) para exibir a
rodada N/M no frontend.

Validado em prod (2026-07-01): 0 duplicatas de gmail_message_id, 0 threads com >1 request,
então o índice UNIQUE de gmail_message_id sobe limpo. Ainda assim, faz um pré-check defensivo.
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: str = "0012"
branch_labels = None
depends_on = None

_TABLE = "parecer_requests"
_THREAD_UNIQUE_DEFAULT = "parecer_requests_gmail_thread_id_key"
_IX_THREAD = "ix_parecer_requests_gmail_thread_id"
_IX_MESSAGE = "ix_parecer_requests_gmail_message_id"


def _thread_unique_constraint_name(bind) -> str | None:
    """Descobre o nome real do UNIQUE de gmail_thread_id (não há naming_convention,
    então o nome é o default do Postgres — mas introspecta para robustez)."""
    inspector = sa.inspect(bind)
    for uc in inspector.get_unique_constraints(_TABLE):
        if uc.get("column_names") == ["gmail_thread_id"]:
            return uc["name"]
    return None


def upgrade() -> None:
    bind = op.get_bind()

    # Pré-check defensivo: mensagens duplicadas quebrariam o índice UNIQUE.
    dup = bind.execute(
        sa.text(
            """
            SELECT gmail_message_id, COUNT(*) AS n
            FROM parecer_requests
            WHERE gmail_message_id IS NOT NULL
            GROUP BY gmail_message_id
            HAVING COUNT(*) > 1
            """
        )
    ).fetchall()
    if dup:
        ids = ", ".join(f"{row[0]} (x{row[1]})" for row in dup)
        raise RuntimeError(
            f"Não é possível criar índice UNIQUE em gmail_message_id: duplicatas encontradas: {ids}. "
            "Resolva manualmente antes de aplicar 0013."
        )

    name = _thread_unique_constraint_name(bind)
    if name:
        op.drop_constraint(name, _TABLE, type_="unique")

    op.create_index(_IX_THREAD, _TABLE, ["gmail_thread_id"])
    op.create_index(_IX_MESSAGE, _TABLE, ["gmail_message_id"], unique=True)


def downgrade() -> None:
    op.drop_index(_IX_MESSAGE, table_name=_TABLE)
    op.drop_index(_IX_THREAD, table_name=_TABLE)
    op.create_unique_constraint(_THREAD_UNIQUE_DEFAULT, _TABLE, ["gmail_thread_id"])
