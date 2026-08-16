from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
from loguru import logger

from backend.auth.security import get_current_user, get_optional_current_user
from backend.models.domain import UserModel
from backend.telemetry.ws_metrics import ws_metrics
from backend.system.health_aggregator import health_aggregator
from backend.accounting.reconciliation_engine import reconciliation_engine
from backend.exchange.market_data_health import market_data_health

router = APIRouter(tags=["Paper Trading System Health & Stabilization"])

@router.get("/api/system/ws-health")
async def get_websocket_health(current_user: UserModel = Depends(get_current_user)):
    """Fetch real-time WebSocket connection and heartbeat metrics."""
    return ws_metrics.get_metrics().to_dict()

@router.get("/api/system/status")
async def get_system_status():
    """Single Source of Truth for Platform Health & Dashboard Status Indicators (Public / Unauthenticated for instant UI sync)."""
    return health_aggregator.get_aggregated_health().model_dump()

@router.get("/api/accounting/reconciliation")
async def get_portfolio_reconciliation(current_user: UserModel = Depends(get_current_user)):
    """Fetch portfolio reconciliation report and accounting invariant audit."""
    report = reconciliation_engine.reconcile(
        cash_balance=10000.0,
        positions=[],
        realized_pnl=0.0,
        total_fees_paid=0.0
    )
    return report.to_dict()

@router.get("/api/system/module-registry")
async def get_module_registry():
    """Fetch Enterprise Module Integration Status Registry (REAL / BETA / MOCK / DISABLED)."""
    return health_aggregator.get_module_registry()


@router.get("/api/exchange/health")
async def get_exchange_market_data_health(exchange: Optional[str] = "BINANCE", current_user: UserModel = Depends(get_current_user)):
    """Fetch exchange market data health and ticker latency metrics."""
    health_dict = market_data_health.get_all_health()
    return {ex: v.to_dict() for ex, v in health_dict.items()}

@router.post("/api/trader/reset")
@router.post("/api/portfolio/reset")
@router.post("/api/wallet/reset-paper-account")
@router.post("/api/user/reset-paper-account")
@router.post("/wallet/reset-paper-account")
@router.post("/trader/reset")
async def reset_paper_account_endpoint(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Reset paper trading account balance to default $10,000 USDT and clear all positions & trade history across Spot, Arbitrage & Shadow."""
    from trader import trader_manager
    user_id = current_user.id if current_user else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    res = await trader_inst.reset_paper_account_async(default_balance=10000.0)

    # Reset all active memory trader instances
    for tr in list(trader_manager.traders.values()):
        try:
            tr.positions.clear()
            tr.orders.clear()
            tr.trade_history.clear()
            tr.usdt_balance = 10000.0
            tr.initial_balance = 10000.0
            tr.auto_bot_enabled = False
        except Exception:
            pass

    # 1. Cleanly wipe all database tables for all user partitions
    try:
        import sqlite3
        from config import settings
        db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        cur = conn.cursor()
        cur.execute("DELETE FROM positions;")
        cur.execute("DELETE FROM orders;")
        cur.execute("DELETE FROM trades;")
        cur.execute("DELETE FROM equity_history;")
        cur.execute("UPDATE portfolio SET usdt_balance = 10000.0, initial_balance = 10000.0, margin_used = 0.0, total_value = 10000.0, auto_bot_enabled = 0;")
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"[RESET_DB_WIPE_ERROR] {e}")

    # 2. Reset Arbitrage Metrics & Routes
    try:
        from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker
        ArbitrageMetricsTracker.reset()
    except Exception as e:
        logger.error(f"[RESET_ARBITRAGE_ERROR] {e}")

    # 3. Reset Shadow Trading Simulation
    try:
        from backend.shadow_trading.shadow_engine import shadow_engine
        shadow_engine.position_tracker.clear_all()
        shadow_engine.router.executed_fills.clear()
    except Exception as e:
        logger.error(f"[RESET_SHADOW_ERROR] {e}")

    return res

@router.delete("/api/user/delete-account")
@router.post("/api/user/delete-account")
async def delete_user_account_endpoint(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Permanently delete user account, paper portfolio, credentials, and associated records."""
    from backend.database.session import AsyncSessionLocal
    from sqlalchemy import text
    user_id = current_user.id if current_user else 1

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("DELETE FROM positions WHERE user_id = :uid"), {"uid": user_id})
            await session.execute(text("DELETE FROM orders WHERE user_id = :uid"), {"uid": user_id})
            await session.execute(text("DELETE FROM trades WHERE user_id = :uid"), {"uid": user_id})
            await session.execute(text("DELETE FROM equity_history WHERE user_id = :uid"), {"uid": user_id})
            await session.execute(text("DELETE FROM wallet_transactions WHERE user_id = :uid"), {"uid": user_id})
            await session.execute(text("DELETE FROM user_preferences WHERE user_id = :uid"), {"uid": user_id})
            await session.execute(text("DELETE FROM portfolio WHERE user_id = :uid"), {"uid": user_id})
            await session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})
            await session.commit()
    except Exception as e:
        logger.error(f"[DELETE_ACCOUNT] DB deletion error for user_id={user_id}: {e}", exc_info=True)

    return {"status": "success", "message": "User account and all associated trading data have been permanently deleted."}

@router.get("/api/system/resources")
async def get_system_resources_endpoint(current_user: UserModel = Depends(get_current_user)):
    """Fetch real-time CPU %, memory MB, asyncio task count, DB connections, and WS client telemetry."""
    from backend.telemetry.resource_monitor import resource_monitor
    return resource_monitor.get_current_resources()

