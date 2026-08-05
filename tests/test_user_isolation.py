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
    PositionModel,
    TradeModel,
    WalletTransactionModel,
    EquityHistoryModel
)

@pytest.mark.asyncio
async def test_multi_user_data_isolation():
    await init_db()

    # Clean database tables for isolation verification
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
        # 1. Unauthenticated requests MUST return 401 Unauthorized
        client.cookies.clear()
        res_unauth_pf = client.get("/api/portfolio")
        assert res_unauth_pf.status_code == 401

        res_unauth_ord = client.post("/api/trade/order", json={
            "symbol": "BTCUSDT",
            "side": "LONG",
            "allocation_usd": 1000.0
        })
        assert res_unauth_ord.status_code == 401

        # 2. Register User A
        res_reg_a = client.post("/api/auth/register", json={
            "name": "Trader A",
            "email": "usera@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        assert res_reg_a.status_code == 201
        user_a_token = res_reg_a.json()["access_token"]
        user_a_id = res_reg_a.json()["user"]["id"]

        # 3. Register User B
        res_reg_b = client.post("/api/auth/register", json={
            "name": "Trader B",
            "email": "userb@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        assert res_reg_b.status_code == 201
        user_b_token = res_reg_b.json()["access_token"]
        user_b_id = res_reg_b.json()["user"]["id"]

        assert user_a_id != user_b_id

        # 4. User A opens a LONG position on BTCUSDT
        headers_a = {"Authorization": f"Bearer {user_a_token}"}
        res_ord_a = client.post("/api/trade/order", json={
            "symbol": "BTCUSDT",
            "side": "LONG",
            "allocation_usd": 2000.0,
            "leverage": 2
        }, headers=headers_a)
        assert res_ord_a.status_code == 200
        assert res_ord_a.json()["status"] == "success"

        # 5. User B opens a SHORT position on ETHUSDT
        headers_b = {"Authorization": f"Bearer {user_b_token}"}
        res_ord_b = client.post("/api/trade/order", json={
            "symbol": "ETHUSDT",
            "side": "SHORT",
            "allocation_usd": 3000.0,
            "leverage": 3
        }, headers=headers_b)
        assert res_ord_b.status_code == 200
        assert res_ord_b.json()["status"] == "success"

        # 6. Verify User A's portfolio has ONLY BTCUSDT
        res_pf_a = client.get("/api/portfolio", headers=headers_a)
        assert res_pf_a.status_code == 200
        pf_a_data = res_pf_a.json()
        active_symbols_a = [p["symbol"] for p in pf_a_data["active_positions"]]
        assert "BTCUSDT" in active_symbols_a
        assert "ETHUSDT" not in active_symbols_a

        # 7. Verify User B's portfolio has ONLY ETHUSDT
        res_pf_b = client.get("/api/portfolio", headers=headers_b)
        assert res_pf_b.status_code == 200
        pf_b_data = res_pf_b.json()
        active_symbols_b = [p["symbol"] for p in pf_b_data["active_positions"]]
        assert "ETHUSDT" in active_symbols_b
        assert "BTCUSDT" not in active_symbols_b

        # 8. User A closes BTCUSDT position
        res_close_a = client.post("/api/trade/position-action", json={
            "symbol": "BTCUSDT",
            "action": "CLOSE"
        }, headers=headers_a)
        assert res_close_a.status_code == 200

        # 9. Verify User A has 0 open positions and 1 closed trade history
        res_pf_a_after = client.get("/api/portfolio", headers=headers_a)
        assert len(res_pf_a_after.json()["active_positions"]) == 0
        closed_trades_a = [t for t in res_pf_a_after.json()["trade_history"] if t.get("status") == "CLOSED"]
        assert len(closed_trades_a) == 1
        assert closed_trades_a[0]["symbol"] == "BTCUSDT"

        # 10. Verify User B STILL has 1 open position (ETHUSDT) and 0 closed trade history
        res_pf_b_after = client.get("/api/portfolio", headers=headers_b)
        assert len(res_pf_b_after.json()["active_positions"]) == 1
        assert res_pf_b_after.json()["active_positions"][0]["symbol"] == "ETHUSDT"
        closed_trades_b = [t for t in res_pf_b_after.json()["trade_history"] if t.get("status") == "CLOSED"]
        assert len(closed_trades_b) == 0

