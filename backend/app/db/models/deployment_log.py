"""Deployment log model for Vercel deployments."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DeploymentLog(Base):
    """Vercel deployment tracking."""

    __tablename__ = "deployment_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    template_version_id: Mapped[int | None] = mapped_column(ForeignKey("template_versions.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # pending, deploying, success, failed
    vercel_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    vercel_deployment_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    github_repo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    screenshot_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    deployed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    business: Mapped["Business"] = relationship("Business", back_populates="deployments")
    template_version: Mapped["TemplateVersion | None"] = relationship("TemplateVersion", back_populates="deployments")

