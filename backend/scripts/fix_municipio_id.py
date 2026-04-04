"""
Corrige municipio_id em pareceres existentes que têm o município identificado
no campo classificacao (JSONB) mas nunca tiveram municipio_id preenchido.

Uso:
    docker compose exec backend python scripts/fix_municipio_id.py
"""

import asyncio
import logging

from sqlalchemy import select

from app.database import async_session as AsyncSessionLocal
from app.models.municipio import Municipio
from app.models.parecer import ParecerRequest

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    async with AsyncSessionLocal() as db:
        # Busca pareceres sem municipio_id mas com classificacao preenchida
        result = await db.execute(
            select(ParecerRequest).where(
                ParecerRequest.municipio_id.is_(None),
                ParecerRequest.classificacao.isnot(None),
            )
        )
        pareceres = result.scalars().all()

        logger.info("Pareceres sem municipio_id com classificacao: %d", len(pareceres))

        # Carrega todos os municípios de uma vez para evitar N+1
        mun_result = await db.execute(select(Municipio))
        municipios = mun_result.scalars().all()

        updated = 0
        not_found = []

        for pr in pareceres:
            nome = (pr.classificacao or {}).get("municipio", "").strip()
            if not nome:
                continue

            # Busca case-insensitive por substring
            nome_lower = nome.lower()
            match = next(
                (m for m in municipios if nome_lower in m.name.lower() or m.name.lower() in nome_lower),
                None,
            )

            if match:
                pr.municipio_id = match.id
                updated += 1
                logger.info("  ✓ %s → %s", nome, match.name)
            else:
                not_found.append(nome)

        await db.commit()

        logger.info("\nAtualizado: %d parecer(es)", updated)
        if not_found:
            logger.info("Município não encontrado para: %s", sorted(set(not_found)))


if __name__ == "__main__":
    asyncio.run(main())
