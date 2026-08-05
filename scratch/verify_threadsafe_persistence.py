import os
import sys
import time
import asyncio
import threading
import logging
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app, trader_manager
from backend.database.session import init_db, AsyncSessionLocal
from backend.models.domain import UserModel, PortfolioModel, PositionModel, TradeModel
from sqlalchemy import select
from trader import PaperTrader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_THREADSAFE_PERSISTENCE")

@pytest.mark.asyncio
async def test_threadsafe_persistence_and_restore():
    logger.info("==========================================================================")
    logger.info("[VERIFICATION] THREAD-SAFE PERSISTENCE & DATABASE RESTORE TEST")
    logger.info("==========================================================================")

    await init_db()
    test_email = f"threadsafe_{int(time.time())}@example.com"

    with TestClient(app) as client:
        # 1. Register User
        res_reg = client.post("/api/auth/register", json={
            "name": "Threadsafe User",
            "email": test_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        assert res_reg.status_code == 201
        token = res_reg.json()["access_token"]
        user_id = res_reg.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Toggle Auto-Bot Enabled
        res_toggle = client.post("/api/bot/toggle?enable=true", headers=headers)
        assert res_toggle.status_code == 200

        # 3. Retrieve User's PaperTrader engine
        user_trader = await trader_manager.get_trader_for_user(user_id)
        assert user_trader.main_loop is not None, "CRITICAL: main_loop was not captured!"
        logger.info(f"Captured main_loop on user_trader for user_id={user_id}: {user_trader.main_loop}")

        # 4. Invoke open_position() from a SEPARATE THREAD (Simulating background_scanner_loop thread)
        thread_result = {}

        def run_open_position_in_worker_thread():
            logger.info(f"[WORKER_THREAD] Running open_position from Thread ID {threading.get_ident()}...")
            res = user_trader.open_position(
                symbol="ETH/USDT",
                side="LONG",
                price=3200.0,
                allocation_usd=1600.0,
                stop_loss_price=3120.0,
                take_profit_price=3360.0,
                leverage=1,
                reason="Threadsafe Cross-Thread Persistence Test"
            )
            thread_result["open_position_res"] = res

        worker_thread = threading.Thread(target=run_open_position_in_worker_thread)
        worker_thread.start()
        worker_thread.join()

        logger.info(f"[WORKER_THREAD] Worker thread finished. open_position() result: {thread_result.get('open_position_res')}")
        assert thread_result.get("open_position_res", {}).get("status") == "success"

        # 5. Flush Persistence & Verify DB Commit
        await user_trader.flush_persistence()
        await asyncio.sleep(0.1)

        async with AsyncSessionLocal() as session:
            # Verify PositionModel row in DB
            res_pos = await session.execute(select(PositionModel).where(PositionModel.user_id == user_id, PositionModel.symbol == "ETH/USDT"))
            db_pos = res_pos.scalars().first()
            assert db_pos is not None, "CRITICAL: PositionModel row was NOT committed to DB!"
            logger.info(f"[VERIFIED DB POSITION] ID={db_pos.id}, Symbol={db_pos.symbol}, Side={db_pos.side}, Margin=${db_pos.margin_usd:.2f}")

            # Verify PortfolioModel row in DB
            res_pf = await session.execute(select(PortfolioModel).where(PortfolioModel.user_id == user_id))
            db_pf = res_pf.scalars().first()
            assert db_pf is not None, "CRITICAL: PortfolioModel row missing!"
            assert db_pf.usdt_balance == 8400.0, f"Expected balance $8400.0, got ${db_pf.usdt_balance}"
            assert db_pf.margin_used == 1600.0, f"Expected margin $1600.0, got ${db_pf.margin_used}"
            logger.info(f"[VERIFIED DB PORTFOLIO] Balance=${db_pf.usdt_balance:.2f}, MarginUsed=${db_pf.margin_used:.2f}")

            # Verify TradeModel row in DB
            all_trades_res = await session.execute(select(TradeModel))
            all_db_trades = all_trades_res.scalars().all()
            logger.info(f"[DEBUG ALL TRADES] Count={len(all_db_trades)}: {[(t.id, t.user_id, t.symbol) for t in all_db_trades]}")

            db_trades = await user_trader.repo.load_trade_history(user_id=user_id)
            assert len(db_trades) >= 1, f"CRITICAL: TradeModel row was NOT committed for user_id={user_id}! All trades: {[(t.id, t.user_id) for t in all_db_trades]}"
            db_tr = db_trades[0]
            logger.info(f"[VERIFIED DB TRADE] ID={db_tr['id']}, Symbol={db_tr['symbol']}, Status={db_tr['status']}")



    # 6. SIMULATE BACKEND RESTART & VERIFY RESTORATION
    logger.info("--------------------------------------------------------------------------")
    logger.info("[RESTART] SIMULATING BACKEND RESTART & RESTORING STATE FROM DATABASE...")
    logger.info("--------------------------------------------------------------------------")

    restored_trader = PaperTrader(user_id=user_id)
    await restored_trader.initialize_and_restore_state()

    assert restored_trader.state.value == "READY"
    assert "ETH/USDT" in restored_trader.positions, "CRITICAL: Position was NOT restored from DB after restart!"
    assert restored_trader.usdt_balance == 8400.0, f"Expected restored balance $8400.0, got ${restored_trader.usdt_balance}"
    assert len(restored_trader.trade_history) >= 1, "CRITICAL: Trade history was NOT restored from DB!"

    logger.info(f"[VERIFIED RESTORED TRADER] State={restored_trader.state.value}, Balance=${restored_trader.usdt_balance:.2f}, ActivePositions={list(restored_trader.positions.keys())}")
    logger.info("==========================================================================")
    logger.info("THREAD-SAFE PERSISTENCE & RESTORE VERIFICATION PASSED 100%")
    logger.info("==========================================================================")
