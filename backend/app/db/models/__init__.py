"""Database models."""

from app.db.models.admin import Admin
from app.db.models.domain import Domain
from app.db.models.setting import Setting
from app.db.models.submission import SubmissionLog
from app.db.models.template import Template

__all__ = ["Admin", "Domain", "Setting", "SubmissionLog", "Template"]

