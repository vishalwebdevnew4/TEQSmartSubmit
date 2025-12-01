"""Security helpers for password hashing, verification, and JWT creation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import jwt

# Try to use passlib, fall back to bcrypt directly if there's a compatibility issue
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    USE_PASSLIB = True
except Exception:
    USE_PASSLIB = False


def hash_password(password: str) -> str:
    """Return hashed representation of password."""
    if USE_PASSLIB:
        try:
            return pwd_context.hash(password)
        except Exception:
            # Fall back to bcrypt directly
            pass
    
    # Use bcrypt directly
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValueError("Password is too long (maximum 72 bytes)")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Validate password against stored hash."""
    if USE_PASSLIB:
        try:
            return pwd_context.verify(password, hashed_password)
        except Exception:
            # Fall back to bcrypt directly
            pass
    
    # Use bcrypt directly
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


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

