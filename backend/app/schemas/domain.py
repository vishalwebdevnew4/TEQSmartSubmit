"""Domain-related schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class DomainBase(BaseModel):
    """Base domain attributes."""

    url: HttpUrl
    category: str | None = None


class DomainCreate(DomainBase):
    """Payload for creating a domain."""

    is_active: bool = True


class DomainUpdate(BaseModel):
    """Payload for updating a domain."""

    url: HttpUrl | None = None
    category: str | None = None
    is_active: bool | None = None
    last_checked_at: datetime | None = None


class DomainRead(DomainBase):
    """Domain representation returned to clients."""

    id: int
    is_active: bool
    created_at: datetime = Field(..., description="UTC timestamp the domain was added")
    last_checked_at: datetime | None = Field(default=None, description="UTC timestamp of last automation attempt")

    class Config:
        from_attributes = True

