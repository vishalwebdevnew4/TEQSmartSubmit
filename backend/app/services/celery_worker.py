#!/usr/bin/env python3
"""
Celery Worker Configuration - Background task processing.
"""

import os
from celery import Celery
from kombu import Queue

# Create Celery app
app = Celery(
    "teqsmartsubmit",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

# Configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "tasks.google_places_fetch": {"queue": "google_places"},
        "tasks.website_generate": {"queue": "website_generation"},
        "tasks.vercel_deploy": {"queue": "deployment"},
        "tasks.form_submit": {"queue": "form_submission"},
        "tasks.email_send": {"queue": "email"},
        "tasks.screenshot": {"queue": "screenshot"},
    },
    task_queues=(
        Queue("default"),
        Queue("google_places"),
        Queue("website_generation"),
        Queue("deployment"),
        Queue("form_submission"),
        Queue("email"),
        Queue("screenshot"),
    ),
)

# Import tasks
from backend.app.tasks import (
    google_places_fetch,
    website_generate,
    vercel_deploy,
    form_submit,
    email_send,
    screenshot_capture,
)

if __name__ == "__main__":
    app.start()

