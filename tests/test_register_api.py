import time
import pytest
from fastapi.testclient import TestClient
from main import app

def test_register_user_api():
    client = TestClient(app)
    test_email = f"test_{int(time.time())}@example.com"
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": test_email,
            "password": "Test@1234",
            "confirm_password": "Test@1234"
        }
    )

    assert response.status_code in [200, 201]
    data = response.json()
    assert data["status"] == "success"
    assert "user" in data
    assert data["user"]["email"] == test_email
