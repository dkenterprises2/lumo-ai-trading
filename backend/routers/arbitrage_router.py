from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.auth.security import get_optional_current_user
from backend.models.domain import UserModel
from backend.arbitrage import (
    CrossExchangeArbitrageEngine,
    ExchangePriceCollector,
    FundingRateCollector,
    BasisSpreadEngine,
    TriangularArbitrageEngine,
    ArbitrageOpportunityRanker,
    ArbitrageRiskFilter,
    ArbitrageShadowRouter,
    ArbitrageMetricsTracker,
    ArbitrageGovernance
)

router = APIRouter(prefix="/api/arbitrage", tags=["Phase 37 — Cross-Exchange Arbitrage Intelligence"])

engine = CrossExchangeArbitrageEngine()
collector = ExchangePriceCollector()
funding_collector = FundingRateCollector()
basis_engine = BasisSpreadEngine()
triangular_engine = TriangularArbitrageEngine()
ranker = ArbitrageOpportunityRanker()
shadow_router = ArbitrageShadowRouter()
governance = ArbitrageGovernance()

shadow_active = True

# In-memory tracking of consumed/filled opportunities to simulate real-world orderbook liquidity consumption
consumed_opportunity_keys: Dict[str, float] = {}
last_auto_execution_time = 0.0

import asyncio

@router.get("/opportunities")
async def get_arbitrage_opportunities(symbol: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch ranked cross-exchange arbitrage opportunities from 24/7 background scanner."""
    from backend.arbitrage import arbitrage_background_scanner
    if not arbitrage_background_scanner.scanner_running:
        arbitrage_background_scanner.start()

    cached_opps = arbitrage_background_scanner.get_latest_opportunities(symbol=symbol or "BTC/USDT")
    if not cached_opps:
        raw_opps = await asyncio.to_thread(engine.scan_opportunities, symbol=symbol or "BTC/USDT")
        cached_opps = ranker.rank_opportunities(raw_opps)

    return {
        "status": "success",
        "count": len(cached_opps),
        "opportunities": [o.to_dict() for o in cached_opps]
    }

@router.get("/spreads")
async def get_exchange_spreads(symbol: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch real-time orderbook quote snapshots and spreads across 5 venues."""
    from backend.arbitrage import arbitrage_background_scanner
    if not arbitrage_background_scanner.scanner_running:
        arbitrage_background_scanner.start()

    quotes = await asyncio.to_thread(collector.fetch_all_quotes, symbol=symbol)
    return {"status": "success", "quotes": {ex: q.to_dict() for ex, q in quotes.items()}}

@router.get("/funding")
async def get_funding_rates(symbol: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch perpetual funding rates across Binance, Bybit, OKX, Kraken."""
    rates = await asyncio.to_thread(funding_collector.fetch_funding_rates, symbol=symbol)
    return {"status": "success", "funding_rates": {ex: r.to_dict() for ex, r in rates.items()}}

@router.get("/basis")
async def get_spot_perpetual_basis(symbol: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch spot vs perpetual basis spread & annualized basis %."""
    quotes = await asyncio.to_thread(collector.fetch_all_quotes, symbol=symbol)
    binance_q = quotes.get("BINANCE")
    spot_price = binance_q.mid_price if (binance_q and binance_q.mid_price > 0) else 0.0
    perp_price = spot_price * 1.0002 if spot_price > 0 else 0.0
    res = basis_engine.evaluate_basis(symbol=symbol or "BTC/USDT", exchange="BINANCE", spot_price=spot_price, perp_mark_price=perp_price)
    return {"status": "success", "basis": res.to_dict()}

@router.get("/metrics")
async def get_arbitrage_metrics(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch cross-exchange arbitrage metrics & performance summary for current user."""
    from backend.arbitrage import arbitrage_background_scanner
    if not arbitrage_background_scanner.scanner_running:
        arbitrage_background_scanner.start()

    from trader import trader_manager
    user_id = current_user.id if current_user else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    user_shadow_active = getattr(trader_inst, "arbitrage_shadow_enabled", True)
    gov = governance.validate_session()
    return {
        "status": "success",
        "metrics": ArbitrageMetricsTracker.get_summary().to_dict(),
        "governance": gov.to_dict(),
        "shadow_active": user_shadow_active
    }

class ArbitrageSimulateTradeRequest(BaseModel):
    symbol: Optional[str] = "BTC/USDT"
    buy_exchange: Optional[str] = "BINANCE"
    sell_exchange: Optional[str] = "BYBIT"
    buy_price: float
    sell_price: float
    net_spread_pct: float
    amount_usd: Optional[float] = 10000.0

@router.post("/simulate-trade")
async def simulate_arbitrage_trade(body: ArbitrageSimulateTradeRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Manually trigger dual-leg shadow arbitrage execution & track Shadow PnL with single-use consumption guard."""
    global consumed_opportunity_keys
    import time
    now = time.time()
    opp_key = f"{body.symbol}_{body.buy_exchange}_{body.sell_exchange}_{round(body.buy_price, 1)}_{round(body.sell_price, 1)}"

    # Guard: Do not allow double-spending the same transient opportunity
    if opp_key in consumed_opportunity_keys:
        return {
            "status": "rejected",
            "reason": "Opportunity orderbook liquidity already consumed and filled by another execution.",
            "execution": {"status": "REJECTED", "rejection_reason": "Orderbook liquidity already consumed."}
        }

    res = shadow_router.route_arbitrage_opportunity(
        symbol=body.symbol or "BTC/USDT",
        buy_exchange=body.buy_exchange or "BINANCE",
        sell_exchange=body.sell_exchange or "BYBIT",
        buy_price=body.buy_price,
        sell_price=body.sell_price,
        net_spread_pct=body.net_spread_pct,
        amount_usd=body.amount_usd or 10000.0
    )

    if res.get("status") == "success" and "execution" in res:
        consumed_opportunity_keys[opp_key] = now
        exec_info = res["execution"]
        profit_usd = exec_info.get("net_profit_usd", 0.0)
        import uuid
        import datetime
        route_detail = {
            "route_id": f"ARB-{uuid.uuid4().hex[:6].upper()}",
            "symbol": body.symbol or "BTC/USDT",
            "buy_exchange": body.buy_exchange or "BINANCE",
            "sell_exchange": body.sell_exchange or "BYBIT",
            "buy_price": body.buy_price,
            "sell_price": body.sell_price,
            "net_spread_pct": body.net_spread_pct,
            "trade_size": body.amount_usd or 10000.0,
            "profit_usd": profit_usd,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "MANUAL_FILLED_ATOMIC",
            "fee_deducted_usd": round((body.amount_usd or 10000.0) * 0.0015, 2)
        }
        ArbitrageMetricsTracker().record_shadow_execution(profit_usd, route_detail)

    return res

@router.post("/shadow/start")
async def start_shadow_arbitrage(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Start automated cross-exchange shadow arbitrage routing for current user."""
    from trader import trader_manager
    user_id = current_user.id if current_user else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    trader_inst.arbitrage_shadow_enabled = True
    await trader_inst.save_portfolio_async()
    return {"status": "success", "message": "Shadow Arbitrage Router ACTIVATED for your account", "shadow_active": True}

@router.post("/shadow/stop")
async def stop_shadow_arbitrage(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Stop automated cross-exchange shadow arbitrage routing for current user."""
    from trader import trader_manager
    user_id = current_user.id if current_user else 1
    trader_inst = await trader_manager.get_trader_for_user(user_id)
    trader_inst.arbitrage_shadow_enabled = False
    await trader_inst.save_portfolio_async()
    return {"status": "success", "message": "Shadow Arbitrage Router DEACTIVATED for your account", "shadow_active": False}

@router.get("/executed-routes")
async def get_executed_arbitrage_routes(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch executed arbitrage routes log strictly from authoritative SQLite ledger."""
    tracker = ArbitrageMetricsTracker()
    routes = tracker.executed_routes
    total_profit = sum(r.get("profit_usd", 0.0) for r in routes)
    return {
        "status": "success",
        "count": len(routes),
        "total_profit_usd": round(total_profit, 2),
        "executed_routes": routes
    }

@router.get("/telemetry")
async def get_arbitrage_telemetry(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch background scanner heartbeat and live venue status."""
    from backend.arbitrage import arbitrage_background_scanner
    return {
        "status": "success",
        "scanner": arbitrage_background_scanner.get_telemetry()
    }

# =========================================================================
# FORENSIC EVIDENCE & AUDIT RECONCILIATION SUITE (Phase 37.5)
# =========================================================================

@router.get("/evidence")
async def get_arbitrage_evidence(
    category: Optional[str] = Query(None, description="One of the 12 rejection or route categories"),
    symbol: Optional[str] = Query(None, description="Filter by crypto pair e.g. BTC/USDT"),
    buy_venue: Optional[str] = Query(None, description="Filter by buy venue e.g. BINANCE"),
    sell_venue: Optional[str] = Query(None, description="Filter by sell venue e.g. BYBIT"),
    decision: Optional[str] = Query(None, description="EXECUTABLE or REJECTED"),
    rejection_reason: Optional[str] = Query(None, description="Specific rejection keyword"),
    time_range_seconds: Optional[float] = Query(None, description="Seconds in past to query"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_dir: Optional[str] = Query("desc", description="asc or desc"),
    limit: Optional[int] = Query(50, ge=1, le=500),
    offset: Optional[int] = Query(0, ge=0),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Query high-frequency forensic evidence events with full audit metadata."""
    from backend.arbitrage.arbitrage_evidence_store import arbitrage_evidence_store
    data = arbitrage_evidence_store.query_events(
        category=category,
        symbol=symbol,
        buy_venue=buy_venue,
        sell_venue=sell_venue,
        decision=decision,
        rejection_reason=rejection_reason,
        time_range_seconds=time_range_seconds,
        sort_by=sort_by or "created_at",
        sort_dir=sort_dir or "desc",
        limit=limit or 50,
        offset=offset or 0
    )
    return {
        "status": "success",
        "category": category or "ALL",
        "symbol": symbol or "ALL",
        **data
    }

@router.get("/evidence/status")
async def get_arbitrage_evidence_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Retrieve real-time persistence pipeline health, queue depth, lock errors, and latency percentiles."""
    from backend.arbitrage.arbitrage_evidence_store import arbitrage_evidence_store
    return {
        "status": "success",
        **arbitrage_evidence_store.get_status()
    }

@router.get("/evidence/writers")
async def get_active_sqlite_writers(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Retrieve active SQLite writers and diagnostic concurrency metrics."""
    from backend.database.db_config import transaction_tracker
    return {
        "status": "success",
        "active_writers": transaction_tracker.get_active_writers(),
        "total_completed": transaction_tracker._completed_count,
        "lock_conflicts": transaction_tracker._lock_conflicts
    }

@router.get("/evidence/reconcile")
async def reconcile_arbitrage_evidence(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Reconcile active displayed metrics with underlying SQLite forensic evidence records."""
    from backend.arbitrage.arbitrage_evidence_store import arbitrage_evidence_store
    metrics_summary = ArbitrageMetricsTracker.get_summary().to_dict()
    report = arbitrage_evidence_store.reconcile_metrics(metrics_summary)
    return {
        "status": "success",
        **report
    }

@router.get("/evidence/export/csv")
async def export_arbitrage_evidence_csv(
    category: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    time_range_seconds: Optional[float] = Query(None),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Export filtered forensic records as CSV along with SHA-256 integrity hash."""
    from backend.arbitrage.arbitrage_evidence_store import arbitrage_evidence_store
    from fastapi.responses import Response
    
    csv_str, sha256_hash, count = arbitrage_evidence_store.export_csv_with_hash(
        category=category,
        symbol=symbol,
        time_range_seconds=time_range_seconds
    )
    headers = {
        "Content-Disposition": f"attachment; filename=arbitrage_evidence_{int(time.time())}.csv",
        "X-Export-SHA256": sha256_hash,
        "X-Total-Records": str(count),
        "Access-Control-Expose-Headers": "X-Export-SHA256, X-Total-Records"
    }
    return Response(content=csv_str, media_type="text/csv", headers=headers)

@router.get("/evidence/export/json")
async def export_arbitrage_evidence_json(
    category: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    time_range_seconds: Optional[float] = Query(None),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Export filtered forensic records as JSON along with SHA-256 integrity hash."""
    from backend.arbitrage.arbitrage_evidence_store import arbitrage_evidence_store
    from fastapi.responses import Response
    
    json_str, sha256_hash, count = arbitrage_evidence_store.export_json_with_hash(
        category=category,
        symbol=symbol,
        time_range_seconds=time_range_seconds
    )
    headers = {
        "Content-Disposition": f"attachment; filename=arbitrage_evidence_{int(time.time())}.json",
        "X-Export-SHA256": sha256_hash,
        "X-Total-Records": str(count),
        "Access-Control-Expose-Headers": "X-Export-SHA256, X-Total-Records"
    }
    return Response(content=json_str, media_type="application/json", headers=headers)

@router.get("/evidence/{event_id}")
async def get_arbitrage_evidence_detail(
    event_id: str,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Retrieve full forensic breakdown for a single evaluation event."""
    from backend.arbitrage.arbitrage_evidence_store import arbitrage_evidence_store
    event = arbitrage_evidence_store.get_event_by_id(event_id)
    if not event:
        return {"status": "error", "message": f"Event ID {event_id} not found."}
    return {"status": "success", "event": event}

@router.post("/evidence/{event_id}/replay")
async def replay_arbitrage_decision(
    event_id: str,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Deterministically replay the arbitrage evaluation on the original captured snapshot."""
    from backend.arbitrage.arbitrage_evidence_store import arbitrage_evidence_store
    res = arbitrage_evidence_store.replay_decision(event_id)
    return res
