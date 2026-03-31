"""Aggregate API routers."""

from fastapi import APIRouter

from app.api.endpoints import auth, domains, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

