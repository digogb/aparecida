"""
Insere todos os 184 municípios do Ceará no banco, de forma idempotente.
Domínios de e-mail ficam vazios — podem ser preenchidos manualmente depois.

Uso:
    docker compose exec backend sh -c "PYTHONPATH=/app python /app/scripts/seed_municipios_ce.py"
"""

import asyncio
import logging

from sqlalchemy import select

from app.database import async_session
from app.models.municipio import Municipio

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

MUNICIPIOS_CE = [
    "Abaiara", "Acarape", "Acaraú", "Acopiara", "Aiuaba", "Alcântaras",
    "Altaneira", "Alto Santo", "Amontada", "Antonina do Norte", "Apuiarés",
    "Aquiraz", "Aracati", "Aracoiaba", "Ararendá", "Araripe", "Aratuba",
    "Arneiroz", "Assaré", "Aurora", "Baixio", "Banabuiú", "Barbalha",
    "Barreira", "Barro", "Barroquinha", "Baturité", "Beberibe", "Bela Cruz",
    "Boa Viagem", "Brejo Santo", "Camocim", "Campos Sales", "Canindé",
    "Capistrano", "Caridade", "Cariré", "Caririaçu", "Cariús", "Carnaubal",
    "Cascavel", "Catarina", "Catunda", "Caucaia", "Cedro", "Chaval",
    "Choró", "Chorozinho", "Coreaú", "Crateús", "Crato", "Croatá",
    "Cruz", "Deputado Irapuan Pinheiro", "Ererê", "Eusébio", "Farias Brito",
    "Forquilha", "Fortaleza", "Fortim", "Frecheirinha", "General Sampaio",
    "Graça", "Granja", "Granjeiro", "Groaíras", "Guaiúba", "Guaraciaba do Norte",
    "Guaramiranga", "Hidrolândia", "Horizonte", "Ibaretama", "Ibiapina",
    "Ibicuitinga", "Icapuí", "Icó", "Iguatu", "Independência", "Ipaporanga",
    "Ipaumirim", "Ipu", "Ipueiras", "Iracema", "Irauçuba", "Itaiçaba",
    "Itaitinga", "Itapagé", "Itapipoca", "Itapiúna", "Itarema", "Itatira",
    "Jaguaretama", "Jaguaribara", "Jaguaribe", "Jaguaruana", "Jardim",
    "Jati", "Jijoca de Jericoacoara", "Juazeiro do Norte", "Jucás",
    "Lavras da Mangabeira", "Limoeiro do Norte", "Madalena", "Maracanaú",
    "Maranguape", "Marco", "Martinópole", "Massapê", "Mauriti", "Meruoca",
    "Milagres", "Milhã", "Miraíma", "Missão Velha", "Mombaça", "Monsenhor Tabosa",
    "Morada Nova", "Moraújo", "Morrinhos", "Mucambo", "Mulungu", "Nova Olinda",
    "Nova Russas", "Novo Oriente", "Ocara", "Orós", "Pacajus", "Pacatuba",
    "Pacoti", "Pacujá", "Palhano", "Palmácia", "Paracuru", "Paraipaba",
    "Parambu", "Paramoti", "Pedra Branca", "Penaforte", "Pentecoste",
    "Pereiro", "Pindoretama", "Piquet Carneiro", "Pires Ferreira", "Poranga",
    "Porteiras", "Potengi", "Potiretama", "Quiterianópolis", "Quixadá",
    "Quixelô", "Quixeramobim", "Quixeré", "Redenção", "Reriutaba",
    "Russas", "Saboeiro", "Salitre", "Santa Quitéria", "Santana do Acaraú",
    "Santana do Cariri", "São Benedito", "São Gonçalo do Amarante",
    "São João do Jaguaribe", "São Luís do Curu", "Senador Pompeu",
    "Senador Sá", "Sobral", "Solonópole", "Tabuleiro do Norte", "Tamboril",
    "Tarrafas", "Tauá", "Tejuçuoca", "Tianguá", "Trairi", "Tururu",
    "Ubajara", "Umari", "Umirim", "Uruburetama", "Uruoca", "Varjota",
    "Várzea Alegre", "Viçosa do Ceará",
]


async def main() -> None:
    async with async_session() as db:
        # Carrega nomes já existentes para CE
        existing_q = await db.execute(
            select(Municipio.name).where(Municipio.state == "CE")
        )
        existing = {row[0] for row in existing_q.all()}

        to_insert = [
            Municipio(name=nome, state="CE", dominios_email=[])
            for nome in MUNICIPIOS_CE
            if nome not in existing
        ]

        if not to_insert:
            logger.info("Todos os municípios do CE já estão cadastrados.")
            return

        db.add_all(to_insert)
        await db.commit()
        logger.info("Inseridos %d município(s) do Ceará.", len(to_insert))
        for m in to_insert:
            logger.info("  + %s", m.name)

    # Roda o fix de municipio_id logo em seguida
    logger.info("\nAtualizando pareceres com município identificado pela IA...")
    from app.models.parecer import ParecerRequest

    async with async_session() as db:
        result = await db.execute(
            select(ParecerRequest).where(
                ParecerRequest.municipio_id.is_(None),
                ParecerRequest.classificacao.isnot(None),
            )
        )
        pareceres = result.scalars().all()

        mun_result = await db.execute(select(Municipio))
        municipios = mun_result.scalars().all()

        updated = 0
        not_found = []

        for pr in pareceres:
            nome = (pr.classificacao or {}).get("municipio", "").strip()
            if not nome:
                continue
            nome_lower = nome.lower()
            match = next(
                (m for m in municipios if nome_lower in m.name.lower() or m.name.lower() in nome_lower),
                None,
            )
            if match:
                pr.municipio_id = match.id
                updated += 1
                logger.info("  ✓ Parecer atualizado: %s → %s", nome, match.name)
            else:
                not_found.append(nome)

        await db.commit()
        logger.info("Pareceres atualizados: %d", updated)
        if not_found:
            logger.info("Município ainda não encontrado: %s", sorted(set(not_found)))


if __name__ == "__main__":
    asyncio.run(main())
