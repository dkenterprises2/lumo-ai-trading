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
async def test_regression_bugs_1_2_3():
    await init_db()

    # Clean database
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
        # STEP 1: Register User
        res_reg = client.post("/api/auth/register", json={
            "name": "Audit Tester",
            "email": "audittester@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        assert res_reg.status_code == 201
        token = res_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # STEP 2: Open 3 paper trades
        res_t1 = client.post("/api/trade/order", json={
            "symbol": "BTCUSDT", "side": "LONG", "allocation_usd": 1500.0, "leverage": 2
        }, headers=headers)
        assert res_t1.status_code == 200

        res_t2 = client.post("/api/trade/order", json={
            "symbol": "ETHUSDT", "side": "SHORT", "allocation_usd": 2000.0, "leverage": 3
        }, headers=headers)
        assert res_t2.status_code == 200

        res_t3 = client.post("/api/trade/order", json={
            "symbol": "SOLUSDT", "side": "LONG", "allocation_usd": 1000.0, "leverage": 1
        }, headers=headers)
        assert res_t3.status_code == 200

        # STEP 3: Verify initial 3 positions
        res_pf1 = client.get("/api/portfolio", headers=headers)
        assert res_pf1.status_code == 200
        pf1 = res_pf1.json()
        assert len(pf1["active_positions"]) == 3
        pos_symbols_1 = [p["symbol"] for p in pf1["active_positions"]]
        assert "BTCUSDT" in pos_symbols_1
        assert "ETHUSDT" in pos_symbols_1
        assert "SOLUSDT" in pos_symbols_1

        # STEP 4: Simulate Logout
        res_logout = client.post("/api/auth/logout", headers=headers)
        assert res_logout.status_code == 200

        # STEP 5: Login again (Bug 2 check)
        res_login = client.post("/api/auth/login", json={
            "email": "audittester@example.com",
            "password": "Password123!"
        })
        assert res_login.status_code == 200, f"Login failed: {res_login.text}"
        new_token = res_login.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        # STEP 6: Simulate Backend Restart by creating fresh TestClient
        with TestClient(app) as client_restart:
            res_pf_restart = client_restart.get("/api/portfolio", headers=new_headers)
            assert res_pf_restart.status_code == 200
            pf_restart = res_pf_restart.json()

            # BUG 3 Verification: All 3 open positions MUST persist after restart & re-login!
            assert len(pf_restart["active_positions"]) == 3, f"Expected 3 positions, found {len(pf_restart['active_positions'])}"
            restart_symbols = [p["symbol"] for p in pf_restart["active_positions"]]
            assert "BTCUSDT" in restart_symbols
            assert "ETHUSDT" in restart_symbols
            assert "SOLUSDT" in restart_symbols
            assert len(pf_restart["trade_history"]) == 3

            # STEP 7: Close 1 position (BTCUSDT) and restart again
            res_close = client_restart.post("/api/trade/position-action", json={
                "symbol": "BTCUSDT", "action": "CLOSE"
            }, headers=new_headers)
            assert res_close.status_code == 200

        # Fresh restart after close
        with TestClient(app) as client_final:
            res_pf_final = client_final.get("/api/portfolio", headers=new_headers)
            assert res_pf_final.status_code == 200
            pf_final = res_pf_final.json()
            assert len(pf_final["active_positions"]) == 2
            final_symbols = [p["symbol"] for p in pf_final["active_positions"]]
            assert "BTCUSDT" not in final_symbols
            assert "ETHUSDT" in final_symbols
            assert "SOLUSDT" in final_symbols

            closed_trades = [t for t in pf_final["trade_history"] if t.get("status") == "CLOSED"]
            assert len(closed_trades) == 1
            assert closed_trades[0]["symbol"] == "BTCUSDT"

            print("\n==========================================")
            print("REGRESSION TEST SUITE PASSED SUCCESSFULLY!")
            print("==========================================")
