"""Security helpers for password hashing, verification, and JWT creation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return hashed representation of password."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Validate password against stored hash."""
    return pwd_context.verify(password, hashed_password)


def create_access_token(
    *,
    subject: str,
    secret_key: str,
    expires_minutes: int,
    algorithm: str,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a signed JWT for the provided subject."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, secret_key, algorithm=algorithm)

