"""Authentication and admin management endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.crud import admin as admin_crud
from app.schemas.admin import AdminCreate, AdminRead
from app.schemas.token import LoginRequest, TokenWithUser

router = APIRouter()


def validate_registration_token(header_token: str | None) -> None:
    """Ensure provided token matches configured admin registration token."""
    settings = get_settings()
    configured = settings.admin_registration_token
    if not configured:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin registration is disabled",
        )
    if header_token != configured:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin registration token")


@router.post(
    "/register",
    response_model=AdminRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new admin user",
)
async def register_admin(
    *,
    payload: AdminCreate,
    session: AsyncSession = Depends(get_db_session),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> AdminRead:
    """Register a new admin user, guarded by the registration token header."""
    validate_registration_token(admin_token)
    existing = await admin_crud.get_admin_by_username(session, payload.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    try:
        admin = await admin_crud.create_admin(session, payload)
    except IntegrityError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to create admin user") from exc
    return admin


@router.post(
    "/login",
    response_model=TokenWithUser,
    summary="Authenticate admin user and issue access token",
)
async def login_admin(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenWithUser:
    """Verify credentials and return JWT token."""
    admin = await admin_crud.get_admin_by_username(session, payload.username)
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    settings = get_settings()
    access_token = create_access_token(
        subject=admin.username,
        secret_key=settings.secret_key,
        expires_minutes=settings.access_token_expires_minutes,
        algorithm=settings.jwt_algorithm,
    )

    admin.last_login_at = datetime.now(timezone.utc)
    session.add(admin)
    await session.commit()
    await session.refresh(admin)

    return TokenWithUser(access_token=access_token, user=AdminRead.model_validate(admin))

