"""Form submission log model."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FormSubmissionLog(Base):
    """Detailed form submission logs with CAPTCHA and retry info."""

    __tablename__ = "form_submission_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[Optional[int]] = mapped_column(ForeignKey("businesses.id", ondelete="SET NULL"), nullable=True)
    domain_url: Mapped[str] = mapped_column(String(512), nullable=False)
    contact_page_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # success, failed, pending, retrying
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    captcha_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # recaptcha, hcaptcha, 2captcha, none
    captcha_solved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    proxy_used: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    business: Mapped[Optional["Business"]] = relationship("Business", back_populates="form_submissions")

