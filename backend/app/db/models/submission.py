"""Submission log model."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SubmissionStatus:
    """Enumeration of submission statuses."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    SKIPPED = "skipped"


class SubmissionLog(Base):
    """History of automation submission attempts."""

    __tablename__ = "submission_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=SubmissionStatus.PENDING)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    domain_id: Mapped[Optional[int]] = mapped_column(ForeignKey("domains.id", ondelete="SET NULL"), nullable=True)
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("templates.id", ondelete="SET NULL"), nullable=True)
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)

    domain: Mapped[Optional["Domain"]] = relationship("Domain", back_populates="submissions")
    template: Mapped[Optional["Template"]] = relationship("Template", back_populates="submission_logs")
    admin: Mapped[Optional["Admin"]] = relationship("Admin", back_populates="submissions")

