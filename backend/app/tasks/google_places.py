"""Google Places API background task."""

from backend.app.services.celery_worker import app
from backend.app.services.google_places_service import fetch_business_data
from backend.app.db.sync_session import SessionLocal
from backend.app.db.models.business import Business


@app.task(name="tasks.google_places_fetch", bind=True, max_retries=3)
def google_places_fetch(self, input_value: str, input_type: str, task_id: int):
    """Fetch business data from Google Places API."""
    db = SessionLocal()
    try:
        # Update task status
        from backend.app.db.models.task import Task
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "processing"
            db.commit()
        
        # Fetch business data
        business_data = fetch_business_data(input_value, input_type)
        
        # Save to database
        business = Business(
            name=business_data["name"],
            phone=business_data.get("phone"),
            address=business_data.get("address"),
            website=business_data.get("website"),
            google_places_url=business_data.get("googlePlacesUrl"),
            google_places_id=business_data.get("googlePlacesId"),
            description=business_data.get("description"),
            categories=business_data.get("categories"),
            reviews=business_data.get("reviews"),
            images=business_data.get("images"),
            rating=business_data.get("rating"),
            review_count=business_data.get("reviewCount"),
            raw_data=business_data.get("rawData"),
        )
        db.add(business)
        db.commit()
        
        # Update task
        if task:
            task.status = "completed"
            task.result_data = {"business_id": business.id}
            db.commit()
        
        return {"success": True, "business_id": business.id}
    except Exception as e:
        # Update task
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
        
        # Retry
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()

