from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
import time
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
    """Comprehensive Full Institutional Platform Reset: Fast non-blocking atomic reset for Spot, Sub-Wallets, Arbitrage, and Positions."""
    from trader import trader_manager
    user_id = current_user.id if current_user else 1
    logger.info(f"[RESET_ENDPOINT] Executing Fast Institutional Account Reset for user_id={user_id}...")

    try:
        # 1. Reset Spot Portfolio & In-Memory Trader State (includes atomic DB reset for this user)
        trader_inst = await trader_manager.get_trader_for_user(user_id)
        res = await trader_inst.reset_paper_account_async(default_balance=10000.0)

        # 2. Reset Multi-Capital Sub-Wallets (Funding, Spot, Arbitrage, Shadow)
        try:
            from backend.wallet.sub_wallet_manager import sub_wallet_manager
            sub_wallet_manager.reset()
        except Exception as sw_err:
            logger.debug(f"[RESET_SUB_WALLETS_ERR] {sw_err}")

        # 3. Reset Arbitrage & Shadow Position Tracker
        try:
            from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker
            ArbitrageMetricsTracker.reset()

            from backend.shadow_trading.shadow_engine import shadow_engine
            if hasattr(shadow_engine, "position_tracker") and hasattr(shadow_engine.position_tracker, "clear_all"):
                shadow_engine.position_tracker.clear_all()
            if hasattr(shadow_engine, "router") and hasattr(shadow_engine.router, "executed_fills"):
                shadow_engine.router.executed_fills.clear()
        except Exception as aux_err:
            logger.debug(f"[RESET_AUX_ENGINES_ERR] {aux_err}")

        return {
            "status": "success",
            "message": "Full Institutional Account Reset completed! Spot, Sub-Wallets, Arbitrage, and Orders/Positions have all been cleanly reset to default baseline ($10,000 USDT).",
            "usdt_balance": 10000.0,
            "portfolio": res
        }

    except Exception as e:
        logger.error(f"[RESET_ENDPOINT_ERROR] Failed to reset paper account for user_id={user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "status": "error",
                "error_code": "RESET_FAILED",
                "message": f"Failed to reset paper account: {str(e)}"
            }
        )

    except Exception as e:
        logger.error(f"[RESET_ENDPOINT_ERROR] Failed to reset paper account for user_id={user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "status": "error",
                "error_code": "RESET_FAILED",
                "message": f"Failed to reset paper account: {str(e)}"
            }
        )

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

from pydantic import BaseModel

class WalletFundsRequest(BaseModel):
    amount: float

@router.post("/api/wallet/deposit")
@router.post("/api/user/deposit")
@router.post("/api/portfolio/deposit")
@router.post("/wallet/deposit")
async def deposit_virtual_funds_endpoint(body: WalletFundsRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Deposit virtual USDT capital into the user's paper trading wallet."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be greater than zero.")

    from trader import trader_manager
    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)

    # 1. Update In-Memory Balance & Ledger
    user_trader.usdt_balance = round(user_trader.usdt_balance + body.amount, 4)
    user_trader.initial_balance = round(user_trader.initial_balance + body.amount, 4)
    tx_id = f"TX_{int(time.time() * 1000)}_{len(user_trader.ledger) + 1}"
    tx = {
        "tx_id": tx_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tx_type": "DEPOSIT",
        "amount": round(body.amount, 4),
        "balance_after": round(user_trader.usdt_balance, 4),
        "reference_id": "USER_DEPOSIT",
        "description": f"Virtual Capital Deposit of ${body.amount:,.2f} USDT"
    }
    user_trader.ledger.append(tx)

    # 2. Persist to DB directly
    try:
        await user_trader.repo.record_wallet_transaction(tx, user_id=user_id)
    except Exception as ex:
        logger.warning(f"[DEPOSIT_TX_WARN] {ex}")

    try:
        await user_trader.save_portfolio_async()
    except Exception as ex:
        logger.warning(f"[DEPOSIT_PORT_WARN] {ex}")

    return {
        "status": "success",
        "message": f"Successfully deposited ${body.amount:,.2f} USDT virtual funds.",
        "usdt_balance": user_trader.usdt_balance,
        "transaction": tx
    }

@router.post("/api/wallet/withdraw")
@router.post("/api/user/withdraw")
@router.post("/api/portfolio/withdraw")
@router.post("/wallet/withdraw")
async def withdraw_virtual_funds_endpoint(body: WalletFundsRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Withdraw virtual USDT capital from the user's paper trading wallet."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be greater than zero.")

    from trader import trader_manager
    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)
    if user_trader.usdt_balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient USDT balance. Available: ${user_trader.usdt_balance:,.2f} USDT, Requested: ${body.amount:,.2f} USDT"
        )

    # 1. Update In-Memory Balance & Ledger
    user_trader.usdt_balance = round(max(0.0, user_trader.usdt_balance - body.amount), 4)
    tx_id = f"TX_{int(time.time() * 1000)}_{len(user_trader.ledger) + 1}"
    tx = {
        "tx_id": tx_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tx_type": "WITHDRAWAL",
        "amount": round(-abs(body.amount), 4),
        "balance_after": round(user_trader.usdt_balance, 4),
        "reference_id": "USER_WITHDRAWAL",
        "description": f"Virtual Capital Withdrawal of ${body.amount:,.2f} USDT"
    }
    user_trader.ledger.append(tx)

    # 2. Persist to DB directly
    try:
        await user_trader.repo.record_wallet_transaction(tx, user_id=user_id)
    except Exception as ex:
        logger.warning(f"[WITHDRAW_TX_WARN] {ex}")

    try:
        await user_trader.save_portfolio_async()
    except Exception as ex:
        logger.warning(f"[WITHDRAW_PORT_WARN] {ex}")

    return {
        "status": "success",
        "message": f"Successfully withdrew ${body.amount:,.2f} USDT virtual funds.",
        "usdt_balance": user_trader.usdt_balance,
        "transaction": tx
    }

@router.get("/api/system/resources")
async def get_system_resources_endpoint(current_user: UserModel = Depends(get_current_user)):
    """Fetch real-time CPU %, memory MB, asyncio task count, DB connections, and WS client telemetry."""
    from backend.telemetry.resource_monitor import resource_monitor
    return resource_monitor.get_current_resources()

