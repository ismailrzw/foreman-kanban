"""
Health check endpoint tests.
Verifies that the /api/health endpoint returns status 200 and healthy JSON response.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify that GET /api/health returns HTTP 200 and status healthy."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "foreman-backend"
