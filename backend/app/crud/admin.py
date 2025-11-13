"""Admin CRUD helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.models.admin import Admin
from app.schemas.admin import AdminCreate


async def get_admin_by_username(session: AsyncSession, username: str) -> Admin | None:
    """Retrieve admin by username."""
    stmt = select(Admin).where(Admin.username == username)
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_admin(session: AsyncSession, payload: AdminCreate) -> Admin:
    """Persist a new admin user."""
    admin = Admin(username=payload.username, password_hash=hash_password(payload.password))
    session.add(admin)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise
    await session.refresh(admin)
    return admin

