from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.auth.security import get_optional_current_user
from backend.portfolio.optimizer import portfolio_optimizer
from backend.portfolio.risk_parity import risk_parity_allocator
from backend.portfolio.black_litterman import black_litterman_model
from backend.portfolio.kelly_allocator import kelly_allocator
from backend.portfolio.rebalancer import portfolio_rebalancer
from backend.portfolio.stress_testing import stress_testing_engine
from backend.portfolio.scenario_analysis import scenario_analysis_engine

router = APIRouter(prefix="/api/portfolio", tags=["Institutional Portfolio Optimization & Capital Allocation"])

@router.get("/allocations")
async def get_portfolio_allocations(current_user: UserModel = Depends(get_current_user)):
    """Return current strategy capital allocations & exposure breakdown."""
    exp = scenario_analysis_engine.generate_exposure_summary()
    return {
        "user_id": current_user.id,
        "allocations": exp["strategy_exposure"],
        "sector_exposure": exp["sector_exposure"],
        "cash_reserve_pct": exp["cash_reserve_pct"]
    }

@router.post("/optimize")
async def optimize_portfolio_weights(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Optimize strategy weights using Mean-Variance, Minimum Variance, or Maximum Sharpe."""
    sample_strats = [
        {"id": "ai_hybrid", "expected_return": 0.25, "volatility": 0.14},
        {"id": "trend_following", "expected_return": 0.18, "volatility": 0.12},
        {"id": "breakout", "expected_return": 0.28, "volatility": 0.20},
        {"id": "momentum", "expected_return": 0.22, "volatility": 0.15},
        {"id": "scalping", "expected_return": 0.16, "volatility": 0.10}
    ]
    target_vol = float(body.get("target_volatility", 0.15))
    max_w = float(body.get("max_strategy_weight", 0.30))

    return portfolio_optimizer.optimize_portfolio(sample_strats, target_volatility=target_vol, max_strategy_weight=max_w)

@router.post("/rebalance")
async def rebalance_portfolio_allocations(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Trigger portfolio rebalancing to match target strategy weights."""
    target_w = body.get("target_weights", {"ai_hybrid": 0.30, "trend_following": 0.25, "breakout": 0.20, "momentum": 0.25})
    return portfolio_rebalancer.execute_rebalance(current_user.id, target_w)

@router.get("/exposure")
async def get_portfolio_exposure_monitor(current_user: UserModel = Depends(get_current_user)):
    """Return live portfolio exposure summary & correlation matrix."""
    exp = scenario_analysis_engine.generate_exposure_summary()
    corr = scenario_analysis_engine.generate_correlation_matrix(["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"])
    return {
        "user_id": current_user.id,
        "exposure": exp,
        "correlation": corr
    }

@router.post("/stress-test")
async def run_portfolio_stress_tests(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Simulate portfolio impact across 7 historical crisis & shock scenarios."""
    eq = float(body.get("portfolio_equity", 100000.0))
    return stress_testing_engine.run_stress_test_scenarios(portfolio_equity=eq)

@router.post("/scenario-analysis")
async def run_portfolio_scenario_analysis(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Execute scenario analysis and asset correlation matrix generator."""
    symbols = body.get("symbols", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"])
    return scenario_analysis_engine.generate_correlation_matrix(symbols)

@router.get("/risk-parity")
async def get_risk_parity_allocations(current_user: UserModel = Depends(get_current_user)):
    """Return Equal Risk Contribution (ERC) Risk Parity allocations."""
    sample_strats = [
        {"id": "ai_hybrid", "volatility": 0.14},
        {"id": "trend_following", "volatility": 0.12},
        {"id": "breakout", "volatility": 0.20},
        {"id": "momentum", "volatility": 0.15}
    ]
    return risk_parity_allocator.calculate_risk_parity_weights(sample_strats)

@router.get("/black-litterman")
async def get_black_litterman_allocations(current_user: UserModel = Depends(get_current_user)):
    """Return Black-Litterman Bayesian portfolio allocations."""
    market_w = {"ai_hybrid": 0.25, "trend_following": 0.25, "breakout": 0.25, "momentum": 0.25}
    ai_views = [{"strategy_id": "ai_hybrid", "expected_return": 0.08}]
    return black_litterman_model.calculate_bl_weights(market_w, ai_views)

@router.get("/profit-attribution")
@router.get("/attribution")
async def get_profit_attribution_router(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Delegate to high-performance profit attribution calculator."""
    from backend.wallet.sub_wallet_manager import sub_wallet_manager
    from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker
    from backend.shadow_trading.shadow_engine import shadow_engine
    from trader import trader_manager

    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)
    
    # 1. Real-time dynamic prices directly from singleton market_engine
    from market_data import market_engine
    prices = {"USDT": 1.0}
    with market_engine._lock:
        for k, v in market_engine.price_cache.items():
            if v > 0:
                prices[k] = v

    for sym, pos in user_trader.positions.items():
        if sym not in prices or prices[sym] <= 0:
            prices[sym] = pos.get('current_price') or market_engine.fetch_current_price(sym)

    for t in user_trader.trade_history:
        sym = t.get('symbol')
        if sym and (sym not in prices or prices[sym] <= 0):
            prices[sym] = market_engine.fetch_current_price(sym)

    pf = user_trader.get_portfolio_summary(prices)
    spot_realized = pf.get("closed_pnl_usd", 0.0)
    spot_unrealized = pf.get("total_unrealized_pnl_usd", 0.0)
    spot_total = round(spot_realized + spot_unrealized, 2)

    arb_summary = ArbitrageMetricsTracker.get_summary()
    arb_profit = round(getattr(arb_summary, "captured_profit_usd", 0.0), 2)
    arb_trades = getattr(arb_summary, "executable_opportunities", 0)

    shadow_positions = shadow_engine.position_tracker.get_all_positions()
    shadow_analytics = shadow_engine.pnl_engine.compute_pnl_analytics(shadow_positions, shadow_engine.router.executed_fills)
    shadow_net = round(getattr(shadow_analytics, "net_pnl_usd", 0.0), 2)

    wallets_summary = sub_wallet_manager.get_wallets_summary(spot_unrealized=spot_unrealized)
    total_combined = round(spot_total + arb_profit + shadow_net, 2)

    # Dynamic symbol breakdown across all open positions and closed trades
    symbol_breakdown = {}
    for sym, pos in user_trader.positions.items():
        entry_price = float(pos.get('entry_price', 0.0))
        cur_price = prices.get(sym) or pos.get('current_price') or market_engine.fetch_current_price(sym)
        side = pos.get('side', 'LONG')
        amount = float(pos.get('amount', 0.0))
        leverage = float(pos.get('leverage', 1.0))
        margin = float(pos.get('margin_usd', (amount * entry_price) / max(1.0, leverage)))
        if side.upper() == 'LONG':
            u_pnl = (cur_price - entry_price) * amount
        else:
            u_pnl = (entry_price - cur_price) * amount

        u_pnl = round(u_pnl, 2)
        symbol_breakdown[sym] = {
            "trades": 1,
            "realized_pnl": 0.0,
            "unrealized_pnl": u_pnl,
            "pnl": u_pnl,
            "wins": 1 if u_pnl > 0 else 0,
            "losses": 1 if u_pnl < 0 else 0,
            "status": "OPEN",
            "entry_price": round(entry_price, 4),
            "mark_price": round(cur_price, 4),
            "side": side,
            "margin_usd": round(margin, 2)
        }

    for t in user_trader.trade_history:
        if t.get("status") == "OPEN" and not t.get("exit_time"):
            continue  # Already represented from active positions
        sym = t.get('symbol', 'UNKNOWN')
        pnl = float(t.get('pnl_usd', 0.0))
        if sym in symbol_breakdown:
            sb = symbol_breakdown[sym]
            sb["trades"] += 1
            sb["realized_pnl"] = round(sb["realized_pnl"] + pnl, 2)
            sb["pnl"] = round(sb["realized_pnl"] + sb.get("unrealized_pnl", 0.0), 2)
            if pnl > 0:
                sb["wins"] += 1
            elif pnl < 0:
                sb["losses"] += 1
        else:
            symbol_breakdown[sym] = {
                "trades": 1,
                "realized_pnl": round(pnl, 2),
                "unrealized_pnl": 0.0,
                "pnl": round(pnl, 2),
                "wins": 1 if pnl > 0 else 0,
                "losses": 1 if pnl < 0 else 0,
                "status": "CLOSED",
                "entry_price": round(float(t.get('entry_price', 0.0)), 4),
                "mark_price": round(float(t.get('exit_price', t.get('entry_price', 0.0))), 4),
                "side": t.get('side', 'BUY'),
                "margin_usd": round(float(t.get('margin_usd', 0.0)), 2)
            }

    return {
        "status": "success",
        "total_profit_usd": total_combined,
        "daily_pnl_usd": pf.get("daily_pnl_usd", spot_total),
        "daily_pnl_pct": pf.get("daily_pnl_pct", 0.0),
        "total_portfolio_value": wallets_summary.get("total_system_equity_usd", pf.get("total_portfolio_value", 10000.0)),
        "spot_portfolio_value": pf.get("total_portfolio_value", 10000.0),
        "wallets_summary": wallets_summary,
        "attribution": {
            "spot": {
                "name": "Spot AI Paper Trading",
                "profit_usd": spot_total,
                "realized_pnl": round(spot_realized, 2),
                "unrealized_pnl": round(spot_unrealized, 2),
                "trades_count": pf.get("total_closed_trades", len([t for t in user_trader.trade_history if t.get("status") == "CLOSED"])),
                "win_rate": pf.get("win_rate", 0.0),
                "share_pct": 100.0,
                "symbol_breakdown": symbol_breakdown
            },
            "arbitrage": {
                "name": "Cross-Exchange Arbitrage",
                "profit_usd": arb_profit,
                "executions_count": arb_trades,
                "opportunities_detected": getattr(arb_summary, "total_opportunities_detected", 0),
                "venues_count": 5,
                "share_pct": 0.0,
                "routes_list": []
            },
            "shadow": {
                "name": "Shadow Replay Simulation",
                "profit_usd": shadow_net,
                "gross_pnl": round(getattr(shadow_analytics, "gross_pnl_usd", 0.0), 2),
                "slippage_usd": round(getattr(shadow_analytics, "slippage_cost_usd", 0.0), 2),
                "fees_usd": 0.0,
                "trades_count": len(shadow_positions),
                "share_pct": 0.0,
                "trades_list": []
            }
        }
    }
