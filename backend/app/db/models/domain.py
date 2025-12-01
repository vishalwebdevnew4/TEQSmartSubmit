"""Domain persistence model."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Domain(Base):
    """Domain queued for automation runs."""

    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    contact_page_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    contact_check_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    contact_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    contact_check_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    submissions: Mapped[List["SubmissionLog"]] = relationship(
        "SubmissionLog", back_populates="domain", cascade="all, delete-orphan"
    )
    templates: Mapped[List["Template"]] = relationship("Template", back_populates="domain")

