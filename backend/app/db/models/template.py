"""Template model storing field mappings."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Template(Base):
    """Form template configuration."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(256))
    field_mappings: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    domain_id: Mapped[Optional[int]] = mapped_column(ForeignKey("domains.id", ondelete="SET NULL"), nullable=True)

    domain: Mapped[Optional["Domain"]] = relationship("Domain", back_populates="templates")
    submission_logs: Mapped[List["SubmissionLog"]] = relationship("SubmissionLog", back_populates="template")
