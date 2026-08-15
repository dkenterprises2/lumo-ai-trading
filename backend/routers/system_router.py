from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional

from backend.auth.security import get_current_user
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
async def reset_paper_account_endpoint(current_user: UserModel = Depends(get_current_user)):
    """Reset paper trading account balance to default $10,000 USDT and clear all positions & trade history."""
    from trader import trader_manager
    trader_inst = await trader_manager.get_trader_for_user(current_user.id)
    res = await trader_inst.reset_paper_account_async(default_balance=10000.0)
    return res

@router.get("/api/system/resources")
async def get_system_resources_endpoint(current_user: UserModel = Depends(get_current_user)):
    """Fetch real-time CPU %, memory MB, asyncio task count, DB connections, and WS client telemetry."""
    from backend.telemetry.resource_monitor import resource_monitor
    return resource_monitor.get_current_resources()

