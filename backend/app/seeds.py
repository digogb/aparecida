from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Municipio, User, UserRole

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEFAULT_PASSWORD = pwd_ctx.hash("123456")


async def run_seeds(db: AsyncSession) -> None:
    await seed_users(db)
    await seed_municipios(db)
    await db.commit()


async def seed_users(db: AsyncSession) -> None:
    count = (await db.execute(select(func.count()).select_from(User))).scalar()
    if count and count > 0:
        return

    users = [
        User(name="Francisco Ione", email="dr.ione@uol.com.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.admin),
        User(name="Matheus Nogueira", email="Matheuspl20@hotmail.com", hashed_password=DEFAULT_PASSWORD, role=UserRole.advogado),
        User(name="Flavio Henrique", email="flavio@ione.adv.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.advogado),
        User(name="Valeria Matias", email="valeria@ione.adv.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.advogado),
        User(name="Secretaria", email="secretaria@ione.adv.br", hashed_password=DEFAULT_PASSWORD, role=UserRole.secretaria),
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
