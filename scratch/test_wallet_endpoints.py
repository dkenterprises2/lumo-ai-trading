import sys
import os
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from main import app
from backend.auth.security import create_access_token

client = TestClient(app)

# Use test user ID 1
token = create_access_token({"sub": "1", "email": "usera@example.com"})
headers = {"Authorization": f"Bearer {token}"}

print("=== TESTING DEPOSIT VIRTUAL FUNDS ===")
dep_res = client.post("/api/wallet/deposit", json={"amount": 5000.0}, headers=headers)
print(f"Deposit Status: {dep_res.status_code}")
print(f"Deposit Response: {dep_res.json()}")

print("\n=== TESTING WITHDRAW VIRTUAL FUNDS ===")
with_res = client.post("/api/wallet/withdraw", json={"amount": 2000.0}, headers=headers)
print(f"Withdraw Status: {with_res.status_code}")
print(f"Withdraw Response: {with_res.json()}")

print("\n=== TESTING OVER-WITHDRAWAL (INSUFFICIENT BALANCE) ===")
over_res = client.post("/api/wallet/withdraw", json={"amount": 999999.0}, headers=headers)
print(f"Over-Withdraw Status: {over_res.status_code}")
print(f"Over-Withdraw Response: {over_res.json()}")
