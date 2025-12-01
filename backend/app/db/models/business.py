"""Business model for storing Google Places data."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Business(Base):
    """Business information from Google Places API."""

    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    google_places_url: Mapped[Optional[str]] = mapped_column(String(512), unique=True, nullable=True)
    google_places_id: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categories: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    reviews: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    images: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)

    admin: Mapped[Optional["Admin"]] = relationship("Admin", back_populates="businesses")
    templates: Mapped[List["Template"]] = relationship("Template", back_populates="business")
    clients: Mapped[List["Client"]] = relationship("Client", back_populates="business")
    deployments: Mapped[List["DeploymentLog"]] = relationship("DeploymentLog", back_populates="business")
    form_submissions: Mapped[List["FormSubmissionLog"]] = relationship("FormSubmissionLog", back_populates="business")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="business")

