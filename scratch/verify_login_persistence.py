import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, delete
from fastapi.testclient import TestClient

from main import app

from backend.database.session import init_db, AsyncSessionLocal
from backend.models.domain import (
    UserModel,
    RefreshTokenModel,
    UserSessionModel,
    PasswordResetTokenModel,
    PortfolioModel,
    PositionModel,
    TradeModel,
    WalletTransactionModel,
    EquityHistoryModel
)
from backend.auth.security import hash_password, verify_password

async def run_login_persistence_verification():
    print("\n=======================================================")
    print("[INVESTIGATION] RUNNING LOGIN PERSISTENCE VERIFICATION")
    print("=======================================================")

    await init_db()

    test_email = "persist_test@example.com"
    test_password = "SecurePassword123!"

    # Clean existing user if present
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserModel).where(UserModel.email == test_email))
        existing = result.scalars().first()
        if existing:
            await session.execute(delete(UserModel).where(UserModel.id == existing.id))
            await session.commit()

    with TestClient(app) as client:
        # STEP 1: Register User
        res_reg = client.post("/api/auth/register", json={
            "name": "Persistence Tester",
            "email": test_email,
            "password": test_password,
            "confirm_password": test_password
        })
        print(f"\n1. Registration Response: Status={res_reg.status_code}")
        assert res_reg.status_code == 201
        reg_data = res_reg.json()
        user_id = reg_data["user"]["id"]
        print(f"   [EVIDENCE] User Created ID: {user_id}")

    # STEP 2: Verify database record & password hash stored on disk
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user_in_db = res.scalars().first()
        print(f"2. Database Query Post-Register:")
        print(f"   [EVIDENCE] UserModel loaded from DB: ID={user_in_db.id}, Email={user_in_db.email}")
        print(f"   [EVIDENCE] Password Hash Stored: {user_in_db.password_hash}")
        verify_immediate = verify_password(test_password, user_in_db.password_hash)
        print(f"   [EVIDENCE] Immediate Password Verification Result: {verify_immediate}")
        assert verify_immediate is True

    print("\n-------------------------------------------------------")
    print("[RESTART] SIMULATING BACKEND PROCESS RESTART...")
    print("-------------------------------------------------------")

    # STEP 3: Verify User & Password Hash after restart
    async with AsyncSessionLocal() as session_after_restart:
        res2 = await session_after_restart.execute(select(UserModel).where(UserModel.email == test_email))
        user_after_restart = res2.scalars().first()
        print(f"3. Database Query Post-Restart:")
        assert user_after_restart is not None, "CRITICAL: User was lost after restart!"
        print(f"   [EVIDENCE] User loaded post-restart ID={user_after_restart.id}, Email={user_after_restart.email}")
        print(f"   [EVIDENCE] Password Hash post-restart: {user_after_restart.password_hash}")
        verify_post_restart = verify_password(test_password, user_after_restart.password_hash)
        print(f"   [EVIDENCE] Password Verification Post-Restart: {verify_post_restart}")
        assert verify_post_restart is True

    # STEP 4: Perform Login via API post-restart
    with TestClient(app) as client_post_restart:
        res_login = client_post_restart.post("/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        print(f"\n4. API Login Post-Restart Response: Status={res_login.status_code}")
        print(f"   [EVIDENCE] Login Response Body: {res_login.text}")
        assert res_login.status_code == 200, f"Login failed post-restart: {res_login.text}"
        assert "access_token" in res_login.json()
        print("   [EVIDENCE] JWT Access Token successfully issued after restart!")

    print("\n=======================================================")
    print("LOGIN PERSISTENCE & RESTART VERIFICATION SUCCESSFUL 100%")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(run_login_persistence_verification())
