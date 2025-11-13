"""Token-related schemas."""

from datetime import datetime

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

    sub: str | None = None
    exp: datetime | None = None


class LoginRequest(BaseModel):
    """Credentials payload."""

    username: str
    password: str

