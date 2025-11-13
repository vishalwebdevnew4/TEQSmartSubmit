"""Domain-related schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class DomainBase(BaseModel):
    """Base domain attributes."""

    url: HttpUrl
    category: Optional[str] = None


class DomainCreate(DomainBase):
    """Payload for creating a domain."""

    is_active: bool = True


class DomainUpdate(BaseModel):
    """Payload for updating a domain."""

    url: Optional[HttpUrl] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    last_checked_at: Optional[datetime] = None


class DomainRead(DomainBase):
    """Domain representation returned to clients."""

    id: int
    is_active: bool
    created_at: datetime = Field(..., description="UTC timestamp the domain was added")
    last_checked_at: Optional[datetime] = Field(default=None, description="UTC timestamp of last automation attempt")

    class Config:
        from_attributes = True

