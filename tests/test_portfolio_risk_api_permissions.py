import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_unauthenticated_risk_api_access_blocked():
    response = client.get("/api/risk/portfolio")
    # Unauthenticated access must return 401 Unauthorized
    assert response.status_code == 401
