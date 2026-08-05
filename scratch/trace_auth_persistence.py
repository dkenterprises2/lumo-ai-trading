import sys
import os
sys.path.insert(0, os.path.abspath("."))

import sqlite3
from fastapi.testclient import TestClient
from main import app
from config import settings
from backend.auth.security import verify_password, decode_token

print("====================================================")
print("STEP 2: DATABASE CONSISTENCY AUDIT")
print("====================================================")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"Absolute Database Path: {os.path.abspath('lumo_trading.db')}")
print(f"File Exists: {os.path.exists('lumo_trading.db')}")
print(f"File Size: {os.path.getsize('lumo_trading.db')} bytes")

client = TestClient(app)

print("\n====================================================")
print("STEP 1, 3, 4, 5, 6: AUTH LIFECYCLE & DB ROW INSPECTION")
print("====================================================")

email = "persistence_test_user@example.com"
password = "Password123!"

conn = sqlite3.connect('lumo_trading.db')
cursor = conn.cursor()

# Cleanup previous test run if exists
cursor.execute("DELETE FROM users WHERE email=?", (email,))
conn.commit()

# PHASE 1: REGISTER
print("\n--- PHASE 1: REGISTER ---")
reg_res = client.post("/api/auth/register", json={
    "name": "Persistence Test User",
    "email": email,
    "password": password,
    "confirm_password": password
})
print(f"Register Status Code: {reg_res.status_code}")
print(f"Register Response: {reg_res.json()}")

user_after_reg = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until FROM users WHERE email=?", (email,)).fetchone()
print(f"DB Row After Register: {user_after_reg}")

# PHASE 2: FIRST LOGIN
print("\n--- PHASE 2: FIRST LOGIN ---")
login_res = client.post("/api/auth/login", json={
    "email": email,
    "password": password
})
print(f"Login Status Code: {login_res.status_code}")
print(f"Login Response: {login_res.json()}")

token_1 = login_res.json().get("access_token")
refresh_1 = login_res.json().get("refresh_token")

user_after_login1 = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until FROM users WHERE email=?", (email,)).fetchone()
print(f"DB Row After First Login: {user_after_login1}")

# PHASE 3: AUTHENTICATED REQUEST (/api/auth/me)
print("\n--- PHASE 3: AUTHENTICATED REQUEST (/api/auth/me) ---")
me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_1}"})
print(f"/api/auth/me Status Code: {me_res.status_code}")
print(f"/api/auth/me Response: {me_res.json()}")

# PHASE 4: LOGOUT
print("\n--- PHASE 4: LOGOUT ---")
logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token_1}"}, json={"refresh_token": refresh_1})
print(f"Logout Status Code: {logout_res.status_code}")
print(f"Logout Response: {logout_res.json()}")

user_after_logout = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until FROM users WHERE email=?", (email,)).fetchone()
print(f"DB Row After Logout: {user_after_logout}")

pwd_verify_after_logout = verify_password(password, user_after_logout[3])
print(f"verify_password('{password}', db_hash) after Logout Result: {pwd_verify_after_logout}")

# PHASE 5: SECOND LOGIN ATTEMPT
print("\n--- PHASE 5: SECOND LOGIN ATTEMPT ---")
login2_res = client.post("/api/auth/login", json={
    "email": email,
    "password": password
})
print(f"Second Login Status Code: {login2_res.status_code}")
print(f"Second Login Response: {login2_res.json()}")

user_after_login2 = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until FROM users WHERE email=?", (email,)).fetchone()
print(f"DB Row After Second Login: {user_after_login2}")
