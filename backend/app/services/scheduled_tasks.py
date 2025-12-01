#!/usr/bin/env python3
"""
Scheduled Batch Processing - Daily/Weekly tasks.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db.sync_session import SessionLocal
from backend.app.db.models.task import Task
from backend.app.db.models.business import Business
from backend.app.db.models.client import Client
from backend.app.db.models.form_submission_log import FormSubmissionLog


def process_daily_tasks():
    """Process daily batch tasks."""
    db = SessionLocal()
    try:
        # 1. Retry failed form submissions
        failed_submissions = db.query(FormSubmissionLog).filter(
            FormSubmissionLog.status == "failed",
            FormSubmissionLog.retry_count < 3,
            FormSubmissionLog.created_at > datetime.utcnow() - timedelta(days=7),
        ).all()
        
        for submission in failed_submissions:
            # Create retry task
            task = Task(
                task_type="form_submit",
                status="pending",
                input_data={
                    "submission_id": submission.id,
                    "retry": True,
                },
                priority=5,
            )
            db.add(task)
        
        # 2. Send follow-up emails to clients who haven't opened
        unopened_clients = db.query(Client).filter(
            Client.status == "sent",
            Client.emailSentAt < datetime.utcnow() - timedelta(days=3),
            Client.emailOpenedAt == None,
        ).all()
        
        for client in unopened_clients:
            # Create follow-up email task
            task = Task(
                task_type="email_send",
                status="pending",
                input_data={
                    "client_id": client.id,
                    "type": "follow_up",
                },
                priority=3,
            )
            db.add(task)
        
        # 3. Generate weekly reports
        task = Task(
            task_type="report_generate",
            status="pending",
            input_data={
                "type": "weekly",
                "date": datetime.utcnow().isoformat(),
            },
            priority=2,
        )
        db.add(task)
        
        db.commit()
        return {"success": True, "tasks_created": len(failed_submissions) + len(unopened_clients) + 1}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def process_weekly_tasks():
    """Process weekly batch tasks."""
    db = SessionLocal()
    try:
        # 1. Archive old submissions (older than 90 days)
        old_submissions = db.query(FormSubmissionLog).filter(
            FormSubmissionLog.created_at < datetime.utcnow() - timedelta(days=90),
        ).all()
        
        # In production, move to archive table or delete
        # For now, just mark as archived
        
        # 2. Generate monthly analytics report
        task = Task(
            task_type="report_generate",
            status="pending",
            input_data={
                "type": "monthly",
                "date": datetime.utcnow().isoformat(),
            },
            priority=1,
        )
        db.add(task)
        
        db.commit()
        return {"success": True, "archived": len(old_submissions)}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run scheduled tasks")
    parser.add_argument("--type", choices=["daily", "weekly"], default="daily")
    
    args = parser.parse_args()
    
    if args.type == "daily":
        result = process_daily_tasks()
    else:
        result = process_weekly_tasks()
    
    print(json.dumps(result, indent=2))

