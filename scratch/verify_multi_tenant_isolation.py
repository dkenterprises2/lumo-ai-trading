import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete

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

@pytest.mark.asyncio
async def test_fresh_user_multi_tenant_isolation():
    await init_db()

    # Clean database tables
    async with AsyncSessionLocal() as session:
        await session.execute(delete(RefreshTokenModel))
        await session.execute(delete(UserSessionModel))
        await session.execute(delete(PasswordResetTokenModel))
        await session.execute(delete(PositionModel))
        await session.execute(delete(TradeModel))
        await session.execute(delete(WalletTransactionModel))
        await session.execute(delete(EquityHistoryModel))
        await session.execute(delete(PortfolioModel))
        await session.execute(delete(UserModel))
        await session.commit()

    with TestClient(app) as client:
        # STEP 1: Register User A
        res_a = client.post("/api/auth/register", json={
            "name": "Trader Alpha",
            "email": "alpha@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        assert res_a.status_code == 201
        token_a = res_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # VERIFY USER A FRESH PORTFOLIO STATE
        res_pf_a = client.get("/api/portfolio", headers=headers_a)
        assert res_pf_a.status_code == 200
        pf_a = res_pf_a.json()
        assert pf_a["usdt_balance"] == 10000.0, f"Expected 10000.0, got {pf_a['usdt_balance']}"
        assert pf_a["total_portfolio_value"] == 10000.0
        assert len(pf_a["active_positions"]) == 0
        assert len(pf_a["trade_history"]) == 0

        # STEP 2: Register User B
        res_b = client.post("/api/auth/register", json={
            "name": "Trader Beta",
            "email": "beta@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        assert res_b.status_code == 201
        token_b = res_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # VERIFY USER B FRESH PORTFOLIO STATE
        res_pf_b = client.get("/api/portfolio", headers=headers_b)
        assert res_pf_b.status_code == 200
        pf_b = res_pf_b.json()
        assert pf_b["usdt_balance"] == 10000.0, f"Expected 10000.0, got {pf_b['usdt_balance']}"
        assert pf_b["total_portfolio_value"] == 10000.0
        assert len(pf_b["active_positions"]) == 0
        assert len(pf_b["trade_history"]) == 0

        # STEP 3: User A opens position on BTCUSDT ($2000 allocation)
        res_ord_a = client.post("/api/trade/order", json={
            "symbol": "BTCUSDT",
            "side": "LONG",
            "allocation_usd": 2000.0,
            "leverage": 2
        }, headers=headers_a)
        assert res_ord_a.status_code == 200

        # VERIFY USER A STATE AFTER ORDER
        res_pf_a2 = client.get("/api/portfolio", headers=headers_a)
        pf_a2 = res_pf_a2.json()
        assert len(pf_a2["active_positions"]) == 1
        assert pf_a2["active_positions"][0]["symbol"] == "BTCUSDT"

        # VERIFY USER B REMAINS COMPLETELY UNTOUCHED (0 positions, $10000 balance)
        res_pf_b2 = client.get("/api/portfolio", headers=headers_b)
        pf_b2 = res_pf_b2.json()
        assert pf_b2["usdt_balance"] == 10000.0
        assert len(pf_b2["active_positions"]) == 0
        assert len(pf_b2["trade_history"]) == 0

        print("\n=======================================================")
        print("BRAND-NEW USER MULTI-TENANT ISOLATION VERIFIED 100%!")
        print("User A Balance:", pf_a2["usdt_balance"], "| Positions:", len(pf_a2["active_positions"]))
        print("User B Balance:", pf_b2["usdt_balance"], "| Positions:", len(pf_b2["active_positions"]))
        print("=======================================================")
