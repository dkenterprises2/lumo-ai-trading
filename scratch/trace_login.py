import sys
import os
sys.path.insert(0, os.path.abspath("."))
import sqlite3
from fastapi.testclient import TestClient
from main import app
from backend.auth.security import verify_password, decode_token


client = TestClient(app)

print("--- STEP 1: FRONTEND / HTTP CLIENT REGISTRATION ---")
email = "test_login_trace@example.com"
password = "Password123!"

reg_res = client.post("/api/auth/register", json={
    "name": "Login Trace User",
    "email": email,
    "password": password,
    "confirm_password": password
})
print(f"Register HTTP Method: POST")
print(f"Register URL: /api/auth/register")
print(f"Register Status Code: {reg_res.status_code}")
print(f"Register Response Body: {reg_res.json()}")

print("\n--- STEP 2 & 3: DATABASE VERIFICATION ---")
conn = sqlite3.connect('lumo_trading.db')
cursor = conn.cursor()
db_user = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until FROM users WHERE email=?", (email,)).fetchone()

print(f"Database Query: SELECT * FROM users WHERE email='{email}'")
print(f"User Found in DB: {db_user is not None}")
if db_user:
    user_id, name, db_email, pwd_hash, is_active, failed_attempts, locked_until = db_user
    print(f"  User ID: {user_id}")
    print(f"  Stored Email: {db_email}")
    print(f"  Stored Password Hash: {pwd_hash}")
    print(f"  Is Active: {is_active}")
    print(f"  Failed Login Attempts: {failed_attempts}")
    print(f"  Account Locked Until: {locked_until}")

    print("\n--- STEP 4: PASSWORD VERIFICATION CHECK ---")
    verification_result = verify_password(password, pwd_hash)
    print(f"Bcrypt verify_password('{password}', stored_hash) Result: {verification_result}")

print("\n--- STEP 5: LOGIN REQUEST EXECUTION ---")
login_res = client.post("/api/auth/login", json={
    "email": email,
    "password": password,
    "remember_me": False
})
print(f"Login HTTP Method: POST")
print(f"Login URL: /api/auth/login")
print(f"Login Status Code: {login_res.status_code}")
print(f"Login Response Body: {login_res.json()}")

if login_res.status_code == 200:
    access_token = login_res.json().get("access_token")
    payload = decode_token(access_token)
    print(f"JWT Access Token Generated: {access_token[:20]}...")
    print(f"JWT Decoded Payload: {payload}")
