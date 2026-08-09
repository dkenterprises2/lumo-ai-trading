from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
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
