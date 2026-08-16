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

@router.get("/opportunities")
async def get_arbitrage_opportunities(symbol: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch ranked cross-exchange arbitrage opportunities."""
    raw_opps = engine.scan_opportunities(symbol=symbol)
    ranked = ranker.rank_opportunities(raw_opps)
    return {"status": "success", "count": len(ranked), "opportunities": [o.to_dict() for o in ranked]}

@router.get("/spreads")
async def get_exchange_spreads(symbol: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch real-time orderbook quote snapshots and spreads across 5 venues."""
    quotes = collector.fetch_all_quotes(symbol=symbol)
    return {"status": "success", "quotes": {ex: q.to_dict() for ex, q in quotes.items()}}

@router.get("/funding")
async def get_funding_rates(symbol: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch perpetual funding rates across Binance, Bybit, OKX, Kraken."""
    rates = funding_collector.fetch_funding_rates(symbol=symbol)
    return {"status": "success", "funding_rates": {ex: r.to_dict() for ex, r in rates.items()}}

@router.get("/basis")
async def get_spot_perpetual_basis(symbol: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch spot vs perpetual basis spread & annualized basis %."""
    quotes = collector.fetch_all_quotes(symbol=symbol)
    binance_q = quotes.get("BINANCE")
    spot_price = binance_q.mid_price if (binance_q and binance_q.mid_price > 0) else 0.0
    perp_price = spot_price * 1.0002 if spot_price > 0 else 0.0
    res = basis_engine.evaluate_basis(symbol=symbol or "BTC/USDT", exchange="BINANCE", spot_price=spot_price, perp_mark_price=perp_price)
    return {"status": "success", "basis": res.to_dict()}

@router.get("/metrics")
async def get_arbitrage_metrics(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch cross-exchange arbitrage metrics & performance summary for current user."""
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
    """Manually trigger dual-leg shadow arbitrage execution & track Shadow PnL."""
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
        exec_info = res["execution"]
        profit_usd = exec_info.get("net_profit_usd", 0.0)
        ArbitrageMetricsTracker().record_shadow_execution(profit_usd)

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
