import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from main import app
from backend.database.session import init_db, AsyncSessionLocal
from backend.models.domain import (
    UserModel,
    RefreshTokenModel,
    UserSessionModel,
    PasswordResetTokenModel,
    PortfolioModel,
    PositionModel
)

@pytest.mark.asyncio
async def test_auth_full_suite():
    await init_db()

    # Clean auth and portfolio tables for isolation
    async with AsyncSessionLocal() as session:
        await session.execute(delete(RefreshTokenModel))
        await session.execute(delete(UserSessionModel))
        await session.execute(delete(PasswordResetTokenModel))
        await session.execute(delete(PositionModel))
        await session.execute(delete(PortfolioModel))
        await session.execute(delete(UserModel))
        await session.commit()

    with TestClient(app) as client:


        # 1. Registration - Validation Errors
        res_weak = client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "weak",
            "confirm_password": "weak"
        })
        assert res_weak.status_code == 400

        res_pwd = client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "user1@example.com",
            "password": "Password123!",
            "confirm_password": "MismatchPassword123!"
        })
        assert res_pwd.status_code == 400

        # 2. Registration - Success
        res_reg = client.post("/api/auth/register", json={
            "name": "Trader One",
            "email": "trader1@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!"
        })
        assert res_reg.status_code == 201
        data_reg = res_reg.json()
        assert data_reg["status"] == "success"
        assert "access_token" in data_reg
        assert "refresh_token" in data_reg
        assert data_reg["user"]["email"] == "trader1@example.com"

        user1_token = data_reg["access_token"]
        user1_refresh = data_reg["refresh_token"]

        # 3. Duplicate Email Prevention
        res_dup = client.post("/api/auth/register", json={
            "name": "Trader One Clone",
            "email": "trader1@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!"
        })
        assert res_dup.status_code == 409

        # 4. GET /api/auth/me (Protected Route)
        res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {user1_token}"})
        assert res_me.status_code == 200
        assert res_me.json()["user"]["email"] == "trader1@example.com"

        # 5. Unauthorized GET /api/auth/me (Clear cookie jar first)
        client.cookies.clear()
        res_unauth = client.get("/api/auth/me")
        assert res_unauth.status_code == 401


        # 6. Login - Invalid Credentials
        res_bad_login = client.post("/api/auth/login", json={
            "email": "trader1@example.com",
            "password": "WrongPassword123!",
            "remember_me": False
        })
        assert res_bad_login.status_code == 401

        # 7. Account Lockout on 5 Failed Login Attempts
        for _ in range(4):
            client.post("/api/auth/login", json={
                "email": "trader1@example.com",
                "password": "WrongPassword123!"
            })
        res_locked = client.post("/api/auth/login", json={
            "email": "trader1@example.com",
            "password": "WrongPassword123!"
        })
        assert res_locked.status_code == 423 # Locked

        # Reset failed login count for testing remaining flows
        async with AsyncSessionLocal() as session:
            await session.execute(
                UserModel.__table__.update().where(UserModel.email == "trader1@example.com").values(failed_login_attempts=0, locked_until=None)
            )
            await session.commit()

        # 8. Login - Success
        res_login = client.post("/api/auth/login", json={
            "email": "trader1@example.com",
            "password": "SecurePassword123!",
            "remember_me": True
        })
        assert res_login.status_code == 200
        data_login = res_login.json()
        token2 = data_login["access_token"]
        refresh2 = data_login["refresh_token"]

        # 9. Refresh Token Rotation
        res_refresh = client.post("/api/auth/refresh", json={"refresh_token": refresh2})
        assert res_refresh.status_code == 200
        data_refreshed = res_refresh.json()
        assert "access_token" in data_refreshed
        assert "refresh_token" in data_refreshed

        # Old refresh token should now be revoked
        res_old_refresh = client.post("/api/auth/refresh", json={"refresh_token": refresh2})
        assert res_old_refresh.status_code == 401

        # 10. Profile Update
        res_prof = client.put("/api/auth/profile", json={
            "name": "Trader One Updated",
            "timezone": "America/New_York",
            "trading_mode": "Live"
        }, headers={"Authorization": f"Bearer {token2}"})
        assert res_prof.status_code == 200
        assert res_prof.json()["user"]["name"] == "Trader One Updated"
        assert res_prof.json()["user"]["timezone"] == "America/New_York"

        # 11. Change Password
        res_cp = client.put("/api/auth/change-password", json={
            "current_password": "SecurePassword123!",
            "new_password": "NewSecurePassword456!",
            "confirm_new_password": "NewSecurePassword456!"
        }, headers={"Authorization": f"Bearer {token2}"})
        assert res_cp.status_code == 200

        # Login with new password
        res_login_new = client.post("/api/auth/login", json={
            "email": "trader1@example.com",
            "password": "NewSecurePassword456!"
        })
        assert res_login_new.status_code == 200

        # 12. Forgot & Reset Password
        res_forgot = client.post("/api/auth/forgot-password", json={"email": "trader1@example.com"})
        assert res_forgot.status_code == 200
        reset_token = res_forgot.json()["reset_token"]

        res_reset = client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": "FinalPassword789!",
            "confirm_new_password": "FinalPassword789!"
        })
        assert res_reset.status_code == 200

        # 13. Multi-User Isolation Check (User 2)
        res_reg2 = client.post("/api/auth/register", json={
            "name": "Trader Two",
            "email": "trader2@example.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!"
        })
        assert res_reg2.status_code == 201
        u2_id = res_reg2.json()["user"]["id"]

        async with AsyncSessionLocal() as session:
            res_p1 = await session.execute(select(PortfolioModel).where(PortfolioModel.user_id == data_reg["user"]["id"]))
            res_p2 = await session.execute(select(PortfolioModel).where(PortfolioModel.user_id == u2_id))
            p1 = res_p1.scalars().first()
            p2 = res_p2.scalars().first()
            assert p1 is not None and p2 is not None
            assert p1.user_id != p2.user_id

        # 14. Logout
        res_logout = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token2}"})
        assert res_logout.status_code == 200

