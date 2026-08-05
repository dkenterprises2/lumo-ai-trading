import sys
import os
sys.path.insert(0, os.path.abspath("."))

import sqlite3
from fastapi.testclient import TestClient
from main import app
from backend.auth.security import verify_password

client = TestClient(app)

email = "annuysfavv@gmail.com"
password = "Password123!"

conn = sqlite3.connect('lumo_trading.db')
cursor = conn.cursor()

# 1. Check if user exists
user = cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email=?", (email,)).fetchone()
print(f"User in DB before test: {user}")

if not user:
    print("\n=== REGISTERING ANNUYSFAVV@GMAIL.COM ===")
    reg_res = client.post("/api/auth/register", json={
        "name": "Annuys Favv",
        "email": email,
        "password": password,
        "confirm_password": password
    })
    print(f"Register Status: {reg_res.status_code}")
    print(f"Register Response: {reg_res.json()}")

user_after_reg = cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email=?", (email,)).fetchone()
print(f"\nUser in DB after registration: {user_after_reg}")

print("\n=== LOGIN WITH ANNUYSFAVV@GMAIL.COM ===")
login_res = client.post("/api/auth/login", json={
    "email": email,
    "password": password
})
print(f"Login Status: {login_res.status_code}")
print(f"Login Response: {login_res.json()}")

token = login_res.json().get("access_token")

print("\n=== LOGOUT ===")
logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
print(f"Logout Status: {logout_res.status_code}")

print("\n=== SECOND LOGIN WITH ANNUYSFAVV@GMAIL.COM ===")
login2_res = client.post("/api/auth/login", json={
    "email": email,
    "password": password
})
print(f"Second Login Status: {login2_res.status_code}")
print(f"Second Login Response: {login2_res.json()}")
