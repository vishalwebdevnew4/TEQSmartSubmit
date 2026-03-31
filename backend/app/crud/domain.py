"""Domain CRUD helpers."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainUpdate


async def list_domains(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> Sequence[Domain]:
    """Return domains with optional filtering."""
    stmt = select(Domain).order_by(Domain.created_at.desc()).offset(skip).limit(limit)
    if is_active is not None:
        stmt = stmt.where(Domain.is_active.is_(is_active))
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def get_domain(session: AsyncSession, domain_id: int) -> Optional[Domain]:
    """Fetch a domain by primary key."""
    return await session.get(Domain, domain_id)


async def get_domain_by_url(session: AsyncSession, url: str) -> Optional[Domain]:
    """Fetch a domain by URL."""
    stmt = select(Domain).where(Domain.url == url)
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_domain(session: AsyncSession, payload: DomainCreate) -> Domain:
    """Persist a new domain record."""
    domain = Domain(
        url=str(payload.url),
        category=payload.category,
        is_active=payload.is_active,
    )
    session.add(domain)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise
    await session.refresh(domain)
    return domain


async def update_domain(session: AsyncSession, domain: Domain, payload: DomainUpdate) -> Domain:
    """Update an existing domain."""
    data = payload.model_dump(exclude_unset=True)
    if "url" in data and data["url"] is not None:
        domain.url = str(data.pop("url"))
    for field, value in data.items():
        setattr(domain, field, value)
    session.add(domain)
    await session.commit()
    await session.refresh(domain)
    return domain


async def delete_domain(session: AsyncSession, domain: Domain) -> None:
    """Delete a domain entry."""
    await session.delete(domain)
    await session.commit()

