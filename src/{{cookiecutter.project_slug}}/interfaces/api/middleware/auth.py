from __future__ import annotations
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional

from {{cookiecutter.project_slug}}.config.settings import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    sub: str
    exp: int
    iat: int
    type: str = "access"
    scopes: list[str] = []


class CurrentUser(BaseModel):
    id: str
    email: str
    scopes: list[str] = []
    is_active: bool = True


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        token_data = TokenData(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Fetch user from database
    return CurrentUser(
        id=token_data.sub,
        email="user@example.com",  # Placeholder
        scopes=token_data.scopes,
    )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def require_scopes(*required_scopes: str):
    async def scope_checker(current_user: CurrentUser = Depends(get_current_active_user)) -> CurrentUser:
        if not all(scope in current_user.scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return scope_checker;


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    from datetime import datetime, timedelta
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm);