"""Dependência de autorização por papel (role).

Usado para restringir ações a administradores. A decisão do cliente (03/07/2026)
é que somente `role == admin` (Dr. Ione e Matheus) pode disparar a IA.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from app.config import settings

_bearer = HTTPBearer(auto_error=False)
_JWT_ALG = "HS256"


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """Exige um token JWT válido com `role == admin`. Retorna o payload.

    401 se ausente/inválido; 403 se autenticado mas não-admin.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Nao autenticado")
    try:
        payload = jwt.decode(
            credentials.credentials, settings.JWT_SECRET, algorithms=[_JWT_ALG]
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido")
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Apenas administradores podem usar a IA"
        )
    return payload
