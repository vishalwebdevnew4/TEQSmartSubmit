"""Domain management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db_session
from app.crud import domain as domain_crud
from app.db.models.admin import Admin
from app.schemas.domain import DomainCreate, DomainRead, DomainUpdate

router = APIRouter()


@router.get("/", response_model=list[DomainRead], summary="List registered domains")
async def list_domains(
    *,
    session: AsyncSession = Depends(get_db_session),
    _admin: Admin = Depends(get_current_admin),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[DomainRead]:
    """Return domains with optional filters."""
    records = await domain_crud.list_domains(session, skip=skip, limit=limit, is_active=is_active)
    return list(records)


@router.post(
    "/",
    response_model=DomainRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new domain",
)
async def create_domain(
    *,
    payload: DomainCreate,
    session: AsyncSession = Depends(get_db_session),
    _admin: Admin = Depends(get_current_admin),
) -> DomainRead:
    """Create a new domain record."""
    existing = await domain_crud.get_domain_by_url(session, str(payload.url))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Domain already exists",
        )
    try:
        domain = await domain_crud.create_domain(session, payload)
    except IntegrityError as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create domain",
        ) from exc
    return domain


@router.get(
    "/{domain_id}",
    response_model=DomainRead,
    summary="Retrieve a domain by identifier",
)
async def get_domain(
    domain_id: int,
    session: AsyncSession = Depends(get_db_session),
    _admin: Admin = Depends(get_current_admin),
) -> DomainRead:
    """Return a single domain."""
    domain = await domain_crud.get_domain(session, domain_id)
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    return domain


@router.patch(
    "/{domain_id}",
    response_model=DomainRead,
    summary="Update domain settings",
)
async def update_domain(
    *,
    domain_id: int,
    payload: DomainUpdate,
    session: AsyncSession = Depends(get_db_session),
    _admin: Admin = Depends(get_current_admin),
) -> DomainRead:
    """Update an existing domain."""
    domain = await domain_crud.get_domain(session, domain_id)
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    try:
        return await domain_crud.update_domain(session, domain, payload)
    except IntegrityError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conflict while updating domain") from exc


@router.delete(
    "/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a domain from queue",
)
async def delete_domain(
    *,
    domain_id: int,
    session: AsyncSession = Depends(get_db_session),
    _admin: Admin = Depends(get_current_admin),
) -> None:
    """Delete a domain."""
    domain = await domain_crud.get_domain(session, domain_id)
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")
    await domain_crud.delete_domain(session, domain)

