"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Service health check")
async def healthcheck() -> dict[str, str]:
    """Return minimal service health information."""
    return {"status": "ok"}

