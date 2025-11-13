"""Common dependency utilities for API routes."""

from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.crud import admin as admin_crud
from app.db.session import get_session
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """Simple key-based access control. Disabled when secret is default/empty."""
    settings = get_settings()
    if not settings.secret_key or settings.secret_key in {"change-me", "super-secret-key"}:
        return ""
    if x_api_key != settings.secret_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return x_api_key or ""


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield database session for request scope."""
    async for session in get_session():
        yield session


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve currently authenticated admin from JWT token."""
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        token_data = TokenPayload.model_validate(payload)
        if token_data.sub is None:
            raise credentials_exception
    except JWTError as exc:  # pragma: no cover - defensive
        raise credentials_exception from exc

    admin = await admin_crud.get_admin_by_username(session, token_data.sub)
    if not admin or not admin.is_active:
        raise credentials_exception
    return admin

