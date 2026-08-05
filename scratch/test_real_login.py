import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

res = client.post("/api/auth/login", json={
    "email": "annuysfavv@gmail.com",
    "password": "Annu@199500"
})

print(f"Login Status: {res.status_code}")
print(f"Login Response: {res.json()}")
