"""Celery tasks for background processing."""

from backend.app.tasks.google_places import google_places_fetch
from backend.app.tasks.website_generation import website_generate
from backend.app.tasks.deployment import vercel_deploy
from backend.app.tasks.form_submission import form_submit
from backend.app.tasks.email import email_send
from backend.app.tasks.screenshot import screenshot_capture

__all__ = [
    "google_places_fetch",
    "website_generate",
    "vercel_deploy",
    "form_submit",
    "email_send",
    "screenshot_capture",
]

