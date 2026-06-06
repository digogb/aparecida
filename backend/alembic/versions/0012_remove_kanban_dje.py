"""remove Kanban e DJE/movimentações (entrega cliente)

Revision ID: 0012
Revises: 0011
Create Date: 2026-06-06

Remove as funcionalidades dormentes Kanban (tarefas) e DJE/movimentações, que não
fazem parte do escopo contratado. Dropa as tabelas e os tipos ENUM associados.
A tabela `notifications` e o módulo de peer review são mantidos.

Migração de mão única: o downgrade não recria as tabelas (feature removida da entrega).
"""

from alembic import op

revision: str = "0012"
down_revision: str = "0011"
branch_labels = None
depends_on = None


# Ordem filhos → pais; CASCADE cobre FKs/índices remanescentes.
_TABLES = [
    "task_comments",
    "task_history",
    "tasks",
    "columns",
    "boards",
    "movements",
    "process_lawyers",
    "processes",
    "holidays",
]

_ENUMS = [
    "movement_type",
    "task_category",
    "task_priority",
]


def upgrade() -> None:
    for table in _TABLES:
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
    for enum in _ENUMS:
        op.execute(f'DROP TYPE IF EXISTS {enum}')


def downgrade() -> None:
    raise NotImplementedError(
        "Remoção de Kanban/DJE é definitiva nesta entrega; downgrade não suportado."
    )
