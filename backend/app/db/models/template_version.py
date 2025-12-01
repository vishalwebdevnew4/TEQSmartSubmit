"""Template version model for versioning and rollback."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TemplateVersion(Base):
    """Versioned template content."""

    __tablename__ = "template_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)  # Full template content
    color_palette: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    typography: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ai_copy_style: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # formal, friendly, marketing, minimalist
    screenshot_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    template: Mapped["Template"] = relationship("Template", back_populates="versions")
    deployments: Mapped[List["DeploymentLog"]] = relationship("DeploymentLog", back_populates="template_version")

