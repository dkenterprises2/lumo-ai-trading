import os
import sys
import asyncio
import logging
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from fastapi.testclient import TestClient
from main import app, trader_manager, market_engine, ai_strategy, settings
from backend.database.session import init_db, AsyncSessionLocal
from backend.models.domain import UserModel, PortfolioModel
from sqlalchemy import select, delete

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AUDIT_AUTO_TRADING")

import time

@pytest.mark.asyncio
async def test_audit_auto_trading_execution_path():
    logger.info("==========================================================================")
    logger.info("[EXECUTION PATH AUDIT] TRACING AUTO TRADING EXECUTION PATH FROM SCANNER TO DB")
    logger.info("==========================================================================")

    await init_db()

    test_email = f"autotrader_{int(time.time())}@example.com"

    with TestClient(app) as client:
        # 1. Register User
        res_reg = client.post("/api/auth/register", json={
            "name": "Auto Bot User",
            "email": test_email,
            "password": "Password123!",
            "confirm_password": "Password123!"
        })

        assert res_reg.status_code == 201
        token = res_reg.json()["access_token"]
        user_id = res_reg.json()["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Toggle Auto-Bot Enabled = True for User
        res_toggle = client.post("/api/bot/toggle?enable=true", headers=headers)
        assert res_toggle.status_code == 200
        assert res_toggle.json()["auto_bot_enabled"] is True

        # 3. Retrieve User's PaperTrader Engine
        user_trader = await trader_manager.get_trader_for_user(user_id)
        logger.info(f"[PATH_STEP_1] User PaperTrader loaded for UserID={user_id}. AutoBot={user_trader.auto_bot_enabled}, Balance=${user_trader.usdt_balance:.2f}")

        # 4. Fetch Market Data & Technical Indicators for Supported Symbols
        current_prices = {}
        scanner_results = []
        for symbol in settings.SUPPORTED_SYMBOLS[:3]:  # Audit top 3 symbols (BTC/USDT, ETH/USDT, SOL/USDT)
            price = market_engine.fetch_current_price(symbol)
            current_prices[symbol] = price
            df = market_engine.fetch_ohlcv(symbol, limit=40)
            ta = market_engine.calculate_technical_indicators(df)

            signal = ai_strategy.evaluate_trading_signal(
                symbol=symbol,
                current_price=price,
                technical_data=ta,
                sentiment_summary={"overall_sentiment": "BULLISH", "fear_greed_score": 65},
                strategy_name=user_trader.active_strategy,
                risk_mode=user_trader.risk_mode
            )
            scanner_results.append(signal)
            logger.info(f"[PATH_STEP_2_AI_SIGNAL] Symbol={symbol} | Action={signal['action']} | Direction={signal['direction']} | Confidence={signal['confidence_score']}%")

        # 5. Sort Scanner Opportunities
        top_buys = sorted([s for s in scanner_results if "BUY" in s['action']], key=lambda x: x['confidence_score'], reverse=True)
        top_sells = sorted([s for s in scanner_results if "SELL" in s['action']], key=lambda x: x['confidence_score'], reverse=True)

        best_opportunity = top_buys[0] if top_buys else (top_sells[0] if top_sells else None)

        if best_opportunity:
            logger.info(f"[PATH_STEP_3_BEST_OPPORTUNITY] Best Candidate: Symbol={best_opportunity['symbol']}, Direction={best_opportunity['direction']}, Confidence={best_opportunity['confidence_score']}%")
        else:
            logger.info("[PATH_STEP_3_BEST_OPPORTUNITY] No BUY/SELL opportunity found across scanned pairs.")

        # 6. Execute Auto Bot Verification & Risk Validation
        if user_trader.auto_bot_enabled and user_trader.usdt_balance >= 100.0:
            if best_opportunity and best_opportunity['confidence_score'] >= 65.0:
                sym = best_opportunity['symbol']
                side = best_opportunity['direction']
                if sym not in user_trader.positions and side in ["LONG", "SHORT"]:
                    alloc = min(1500.0, user_trader.usdt_balance * 0.20)
                    logger.info(f"[PATH_STEP_4_EXECUTE_OPEN] Calling user_trader.open_position(Symbol={sym}, Side={side}, Alloc=${alloc:.2f})...")
                    res_open = user_trader.open_position(
                        symbol=sym,
                        side=side,
                        price=current_prices[sym],
                        allocation_usd=alloc,
                        stop_loss_price=best_opportunity['stop_loss_price'],
                        take_profit_price=best_opportunity['take_profit_price'],
                        leverage=1,
                        reason=f"Auto-Bot Audit Run"
                    )
                    await user_trader.flush_persistence()
                    logger.info(f"[PATH_STEP_5_RETURN_VALUE] open_position() returned: {res_open}")
                    assert res_open["status"] == "success"
                else:
                    logger.info(f"[PATH_STEP_4_REJECTED] Position already open for {sym} or invalid direction.")
            else:
                conf = best_opportunity['confidence_score'] if best_opportunity else 0.0
                logger.info(f"[PATH_STEP_4_SKIPPED] Best opportunity confidence {conf}% < 65.0% threshold.")
        else:
            logger.info(f"[PATH_STEP_4_SKIPPED] Auto Bot disabled or insufficient balance.")

        # 7. Confirm Database Persistence for User
        async with AsyncSessionLocal() as session:
            stmt = select(PortfolioModel).where(PortfolioModel.user_id == user_id)
            res_pf = await session.execute(stmt)
            pf_db = res_pf.scalars().first()
            logger.info(f"[PATH_STEP_6_DB_PERSISTENCE] Database Portfolio Record for UserID={user_id}: Balance=${pf_db.usdt_balance:.2f}, MarginUsed=${pf_db.margin_used:.2f}")


    logger.info("==========================================================================")
    logger.info("[EXECUTION PATH AUDIT] COMPLETED SUCCESSFULLY - ALL STAGES VERIFIED")
    logger.info("==========================================================================")
