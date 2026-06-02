import asyncio
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    ChangePasswordIn,
    ForgotPasswordIn,
    LoginIn,
    ResetPasswordIn,
    TokenOut,
    UserOut,
)
from app.services.email_sender import send_plain_email

logger = logging.getLogger(__name__)

PREFIX = "/api"
TAGS = ["auth"]

router = APIRouter()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours
RESET_TOKEN_EXPIRE_MINUTES = 60  # link de redefinição vale 1h
MIN_PASSWORD_LENGTH = 8


def create_access_token(user_id: str, email: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "email": email, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decodifica o JWT do header e retorna o usuário ativo. 401 se inválido."""
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado")
    return user


def _reset_signing_key(user: User) -> str:
    """Chave de assinatura por-usuário: inclui o hash atual da senha, então o token de
    reset deixa de valer automaticamente assim que a senha muda (uso único, sem tabela)."""
    return f"{settings.JWT_SECRET}:{user.hashed_password}"


def create_reset_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user.id), "purpose": "pwd_reset", "exp": expire}
    return jwt.encode(payload, _reset_signing_key(user), algorithm=JWT_ALGORITHM)


async def _user_from_reset_token(token: str, db: AsyncSession) -> User:
    """Valida um token de reset e retorna o usuário, ou 400 se inválido/expirado/usado."""
    invalid = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Link inválido ou expirado")
    try:
        user_id = jwt.get_unverified_claims(token).get("sub")
    except JWTError:
        raise invalid
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise invalid
    try:
        payload = jwt.decode(token, _reset_signing_key(user), algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise invalid
    if payload.get("purpose") != "pwd_reset":
        raise invalid
    return user


@router.post("/auth/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)) -> TokenOut:
    result = await db.execute(select(User).where(User.email == body.email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user or not pwd_ctx.verify(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")
    token = create_access_token(str(user.id), user.email, user.role.value)
    return TokenOut(access_token=token)


@router.post("/auth/refresh", response_model=TokenOut)
async def refresh_token(user: User = Depends(get_current_user)) -> TokenOut:
    token = create_access_token(str(user.id), user.email, user.role.value)
    return TokenOut(access_token=token)


@router.get("/auth/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


def _validate_new_password(new_password: str) -> None:
    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A nova senha deve ter ao menos {MIN_PASSWORD_LENGTH} caracteres",
        )


@router.post("/auth/change-password")
async def change_password(
    body: ChangePasswordIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Troca a própria senha (logado). Senha atual errada → 400 (NÃO 401, que deslogaria)."""
    _validate_new_password(body.new_password)
    if not pwd_ctx.verify(body.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta")
    user.hashed_password = pwd_ctx.hash(body.new_password)
    await db.commit()
    return {"ok": True}


@router.post("/auth/forgot-password")
async def forgot_password(body: ForgotPasswordIn, db: AsyncSession = Depends(get_db)) -> dict:
    """Envia link de redefinição por email. Sempre responde 200 (não revela se o email existe)."""
    result = await db.execute(select(User).where(User.email == body.email, User.is_active == True))
    user = result.scalar_one_or_none()
    if user:
        token = create_reset_token(user)
        link = f"{settings.APP_BASE_URL.rstrip('/')}/login?reset_token={token}"
        nome = user.name.split()[0] if user.name else ""
        corpo = (
            f"Olá {nome},\n\n"
            f"Recebemos um pedido para redefinir a senha da sua conta no sistema Ione Advogados.\n\n"
            f"Para criar uma nova senha, acesse o link abaixo (válido por 1 hora):\n\n"
            f"{link}\n\n"
            f"Se você não solicitou isso, ignore este email — sua senha continua a mesma.\n\n"
            f"Atenciosamente,\nSistema Ione Advogados"
        )
        try:
            await asyncio.to_thread(
                send_plain_email, user.email, "Redefinição de senha — Ione Advogados", corpo
            )
        except Exception:
            logger.exception("Falha ao enviar email de redefinição para %s", user.email)
    return {"ok": True}


@router.post("/auth/reset-password")
async def reset_password(body: ResetPasswordIn, db: AsyncSession = Depends(get_db)) -> dict:
    """Define nova senha a partir de um token de redefinição válido."""
    _validate_new_password(body.new_password)
    user = await _user_from_reset_token(body.token, db)
    user.hashed_password = pwd_ctx.hash(body.new_password)
    await db.commit()
    return {"ok": True}
