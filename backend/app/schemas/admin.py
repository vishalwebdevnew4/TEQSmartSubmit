"""Admin user schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class AdminBase(BaseModel):
    """Shared admin attributes."""

    username: str = Field(..., min_length=3, max_length=64)


class AdminCreate(AdminBase):
    """Payload for creating an admin account."""

    password: str = Field(..., min_length=8, max_length=128)


class AdminRead(AdminBase):
    """Admin record returned to clients."""

    id: int
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True

