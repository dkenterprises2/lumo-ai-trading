import sys
import os
sys.path.insert(0, os.path.abspath("."))

import sqlite3
from fastapi.testclient import TestClient
from main import app
from config import settings
from backend.auth.security import verify_password, decode_token, create_access_token, create_refresh_token

print("====================================================")
print("STEP 4 — FILE & CONFIGURATION AUDIT")
print("====================================================")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"Database File Absolute Path: {os.path.abspath('lumo_trading.db')}")
print(f"Database File Exists: {os.path.exists('lumo_trading.db')}")
print(f"Database File Size: {os.path.getsize('lumo_trading.db')} bytes")
print(f"SECRET_KEY (Length): {len(settings.SECRET_KEY)}")
print(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")

print("\n====================================================")
print("STEP 3 — DATABASE VERIFICATION (DIRECT SQL)")
print("====================================================")
conn = sqlite3.connect('lumo_trading.db')
cursor = conn.cursor()

user_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
print(f"SELECT COUNT(*) FROM users; -> {user_count}")

latest_user = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until, created_at FROM users ORDER BY id DESC LIMIT 1").fetchone()
print(f"Latest Registered User: {latest_user}")

test_email = "prod_audit_user@example.com"
test_password = "Password123!"

# Check if user already exists
existing = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until FROM users WHERE email=?", (test_email,)).fetchone()
print(f"User matching '{test_email}': {existing}")

print("\n====================================================")
print("STEP 1 & 2 & 5 — END-TO-END REGISTRATION & LOGIN TRACE")
print("====================================================")

client = TestClient(app)

print("\n[PHASE 1: REGISTRATION]")
reg_payload = {
    "name": "Audit User",
    "email": test_email,
    "password": test_password,
    "confirm_password": test_password
}
reg_res = client.post("/api/auth/register", json=reg_payload)
print(f"Endpoint Reached: POST /api/auth/register")
print(f"Response Status: {reg_res.status_code}")
print(f"Response Headers: {dict(reg_res.headers)}")
print(f"Response Body: {reg_res.json()}")
print(f"Cookies Set: {dict(reg_res.cookies)}")

print("\n[PHASE 2: DB VERIFICATION AFTER REGISTRATION]")
user_row = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until FROM users WHERE email=?", (test_email,)).fetchone()
print(f"User Row in DB: {user_row}")

if user_row:
    user_id = user_row[0]
    pwd_hash = user_row[3]

    refresh_tokens = cursor.execute("SELECT id, user_id, token, expires_at, is_revoked FROM refresh_tokens WHERE user_id=?", (user_id,)).fetchall()
    print(f"Refresh Tokens for User {user_id}: {refresh_tokens}")

    verify_res = verify_password(test_password, pwd_hash)
    print(f"verify_password('{test_password}', '{pwd_hash[:20]}...') Result: {verify_res}")

print("\n[PHASE 3: LOGIN EXECUTION]")
login_payload = {
    "email": test_email,
    "password": test_password,
    "remember_me": False
}
login_res = client.post("/api/auth/login", json=login_payload)
print(f"Endpoint Reached: POST /api/auth/login")
print(f"Response Status: {login_res.status_code}")
print(f"Response Headers: {dict(login_res.headers)}")
print(f"Response Body: {login_res.json()}")
print(f"Cookies Set: {dict(login_res.cookies)}")

if login_res.status_code == 200:
    access_token = login_res.json().get("access_token")
    decoded = decode_token(access_token)
    print(f"JWT Access Token: {access_token[:25]}...")
    print(f"JWT Decoded: {decoded}")
