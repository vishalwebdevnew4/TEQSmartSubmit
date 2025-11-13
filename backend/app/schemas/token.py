"""Token-related schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.admin import AdminRead


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenWithUser(Token):
    """Token response including current admin profile."""

    user: AdminRead


class TokenPayload(BaseModel):
    """Decoded token payload."""

    sub: Optional[str] = None
    exp: Optional[datetime] = None


class LoginRequest(BaseModel):
    """Credentials payload."""

    username: str
    password: str

