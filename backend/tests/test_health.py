"""Basic health endpoint test."""

from fastapi.testclient import TestClient

from app.main import app


def test_healthcheck() -> None:
    """Health endpoint returns ok status."""
    client = TestClient(app)
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

