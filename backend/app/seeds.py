from datetime import date

from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Board, Column, Holiday, Municipio, User, UserRole,
)

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEFAULT_PASSWORD = pwd_ctx.hash("123456")


async def run_seeds(db: AsyncSession) -> None:
    await seed_users(db)
    await seed_municipios(db)
    await seed_board(db)
    await seed_holidays(db)
    await db.commit()


async def seed_users(db: AsyncSession) -> None:
    count = (await db.execute(select(func.count()).select_from(User))).scalar()
    if count and count > 0:
        return

    users = [
        User(name="Francisco Ionde", email="francisco@ionde.adv.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.admin),
        User(name="Matheus Nogueira", email="matheus@ionde.adv.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.advogado),
        User(name="Flavio Henrique", email="flavio@ionde.adv.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.advogado),
        User(name="Valeria Matias", email="valeria@ionde.adv.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.advogado),
        User(name="Secretaria", email="secretaria@ionde.adv.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.secretaria),
    ]
    db.add_all(users)
    await db.flush()


async def seed_municipios(db: AsyncSession) -> None:
    count = (await db.execute(select(func.count()).select_from(Municipio))).scalar()
    if count and count > 0:
        return

    municipios = [
        Municipio(name="São Carlos", state="SP", dominios_email=["saocarlos.sp.gov.br", "pmsaocarlos.sp.gov.br"]),
        Municipio(name="Guarulhos", state="SP", dominios_email=["guarulhos.sp.gov.br", "pmguarulhos.sp.gov.br"]),
        Municipio(name="Campinas", state="SP", dominios_email=["campinas.sp.gov.br", "pmcampinas.sp.gov.br"]),
    ]
    db.add_all(municipios)
    await db.flush()


async def seed_board(db: AsyncSession) -> None:
    count = (await db.execute(select(func.count()).select_from(Board))).scalar()
    if count and count > 0:
        return

    board = Board(name="Principal")
    db.add(board)
    await db.flush()

    columns_data = [
        ("Entrada", 0, 8),
        ("Em andamento", 1, 5),
        ("Aguardando", 2, None),
        ("Concluída", 3, None),
        ("Arquivada", 4, None),
    ]
    for name, pos, wip in columns_data:
        db.add(Column(board_id=board.id, name=name, position=pos, wip_limit=wip))
    await db.flush()


async def seed_holidays(db: AsyncSession) -> None:
    count = (await db.execute(select(func.count()).select_from(Holiday))).scalar()
    if count and count > 0:
        return

    nacionais_2026 = [
        (date(2026, 1, 1), "Confraternização Universal"),
        (date(2026, 2, 16), "Carnaval"),
        (date(2026, 2, 17), "Carnaval"),
        (date(2026, 4, 3), "Sexta-feira Santa"),
        (date(2026, 4, 21), "Tiradentes"),
        (date(2026, 5, 1), "Dia do Trabalho"),
        (date(2026, 6, 4), "Corpus Christi"),
        (date(2026, 9, 7), "Independência do Brasil"),
        (date(2026, 10, 12), "Nossa Senhora Aparecida"),
        (date(2026, 11, 2), "Finados"),
        (date(2026, 11, 15), "Proclamação da República"),
        (date(2026, 11, 20), "Consciência Negra"),
        (date(2026, 12, 25), "Natal"),
    ]

    recesso_2026 = [
        (date(2026, 1, 2), "Recesso Forense"),
        (date(2026, 1, 5), "Recesso Forense"),
        (date(2026, 1, 6), "Recesso Forense"),
        (date(2026, 12, 23), "Recesso Forense"),
        (date(2026, 12, 24), "Recesso Forense"),
        (date(2026, 12, 28), "Recesso Forense"),
        (date(2026, 12, 29), "Recesso Forense"),
        (date(2026, 12, 30), "Recesso Forense"),
        (date(2026, 12, 31), "Recesso Forense"),
    ]

    for d, name in nacionais_2026:
        db.add(Holiday(date=d, name=name, national=True))
    for d, name in recesso_2026:
        db.add(Holiday(date=d, name=name, national=False, comarca="forense"))
    await db.flush()
