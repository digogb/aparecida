"""Promove o Matheus a admin no banco já populado (prod/HML).

Necessário porque `seed_users` só roda com a tabela `users` VAZIA — em bancos já
populados a mudança de role no seeds.py não tem efeito. Idempotente.

Uso (dentro do container):
    docker compose -f docker-compose.prod.yml exec -T -e PYTHONPATH=/app backend \
        python /app/scripts/promote_matheus_admin.py
"""

import asyncio

from sqlalchemy import func, select

from app.database import async_session
from app.models.user import User, UserRole

MATHEUS_EMAIL = "matheuspl20@hotmail.com"  # login é case-insensitive


async def main() -> None:
    async with async_session() as db:
        res = await db.execute(
            select(User).where(func.lower(User.email) == MATHEUS_EMAIL)
        )
        user = res.scalar_one_or_none()
        if user is None:
            print(f"Usuário {MATHEUS_EMAIL} não encontrado — nada a fazer.")
            return
        antes = user.role.value
        if user.role == UserRole.admin:
            print(f"{user.email} já é admin — nada a fazer.")
            return
        user.role = UserRole.admin
        await db.commit()
        print(f"{user.email}: {antes} -> {user.role.value}")


if __name__ == "__main__":
    asyncio.run(main())
