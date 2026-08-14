from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from backend.auth.security import get_current_user
from backend.models.domain import UserModel
from trader import trader_manager
from backend.portfolio_risk import portfolio_risk_orchestrator

router = APIRouter(prefix="/api/risk", tags=["Portfolio Risk Engine Phase 34"])

class KillSwitchActionRequest(BaseModel):
    reason: Optional[str] = "Manual user activation"
    authorized_by: Optional[str] = "Trader User"

class RiskProfileUpdateRequest(BaseModel):
    profile_name: str  # CONSERVATIVE, BALANCED, AGGRESSIVE, CUSTOM

class TradeSimulationRequest(BaseModel):
    symbol: str
    side: str
    allocation_usd: float
    leverage: Optional[int] = 1
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None

@router.get("/portfolio")
async def get_portfolio_risk_summary(current_user: UserModel = Depends(get_current_user)):
    """Fetch complete Phase 34 Portfolio Risk State for current authenticated user."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    return p_state.to_dict()

@router.get("/portfolio/heat")
async def get_portfolio_heat(current_user: UserModel = Depends(get_current_user)):
    """Fetch Portfolio Heat breakdown."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    return p_state.metadata.get("heat", {})

@router.get("/portfolio/correlation")
async def get_portfolio_correlation(current_user: UserModel = Depends(get_current_user)):
    """Fetch position correlation matrix and cluster exposures."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    return p_state.metadata.get("correlation", {})

@router.get("/portfolio/concentration")
async def get_portfolio_concentration(current_user: UserModel = Depends(get_current_user)):
    """Fetch single-symbol, top-N, and cluster concentration analysis."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    return p_state.metadata.get("concentration", {})

@router.get("/drawdown")
async def get_drawdown_risk(current_user: UserModel = Depends(get_current_user)):
    """Fetch peak-to-trough drawdown risk scaling metrics."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    return p_state.metadata.get("drawdown", {})

@router.get("/leverage")
async def get_leverage_recommendation(current_user: UserModel = Depends(get_current_user)):
    """Fetch dynamic leverage recommendation."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    return {
        "leverage_used": p_state.leverage_used,
        "recommended_max_leverage": p_state.recommended_max_leverage
    }

@router.get("/risk-budget")
async def get_risk_budget(current_user: UserModel = Depends(get_current_user)):
    """Fetch daily and weekly risk budget remaining."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    return p_state.metadata.get("budget", {})

@router.get("/dynamic-trade-limit")
async def get_dynamic_trade_limit(current_user: UserModel = Depends(get_current_user)):
    """Fetch dynamic effective trade limit logic and slot availability."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    trade_limit = p_state.metadata.get("trade_limit", {})
    if not trade_limit or not trade_limit.get("configured_max_positions") or trade_limit.get("configured_max_positions") <= 0:
        cfg_max = getattr(user_trader.risk_manager.config, "max_concurrent_trades", getattr(user_trader, "max_open_positions", 10))
        trade_limit["configured_max_positions"] = cfg_max if (cfg_max and cfg_max > 0) else 10
        trade_limit["dynamic_risk_limit"] = trade_limit.get("dynamic_risk_limit") or 10
        trade_limit["effective_max_positions"] = trade_limit.get("effective_max_positions") or 10
        trade_limit["available_trade_slots"] = max(0, trade_limit["effective_max_positions"] - p_state.open_positions)
    return trade_limit

@router.get("/profile")
async def get_risk_profile(current_user: UserModel = Depends(get_current_user)):
    """Fetch user risk profile parameters."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    risk_mode = getattr(user_trader, "risk_mode", "BALANCED")
    prof = portfolio_risk_orchestrator.risk_engine.profile_manager.get_profile(risk_mode)
    max_trades = getattr(user_trader.risk_manager.config, "max_concurrent_trades", getattr(user_trader, "max_open_positions", 10))
    d_prof = prof.to_dict()
    d_prof["max_concurrent_trades"] = max_trades if (max_trades and max_trades > 0) else 10
    return d_prof


@router.put("/profile")
async def update_risk_profile(body: RiskProfileUpdateRequest, current_user: UserModel = Depends(get_current_user)):
    """Update active user risk profile preset (CONSERVATIVE, BALANCED, AGGRESSIVE)."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    name = body.profile_name.upper()
    if name not in ["CONSERVATIVE", "BALANCED", "AGGRESSIVE", "CUSTOM"]:
        raise HTTPException(status_code=400, detail="Invalid risk profile name.")

    user_trader.risk_mode = name
    user_trader._sync_save_portfolio()
    prof = portfolio_risk_orchestrator.risk_engine.profile_manager.get_profile(name)
    return {
        "status": "success",
        "message": f"Updated user risk profile to {name}",
        "profile": prof.to_dict()
    }

@router.get("/recommendations")
async def get_risk_recommendations(current_user: UserModel = Depends(get_current_user)):
    """Fetch structured AI Risk Recommendations."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    p_state = portfolio_risk_orchestrator.get_portfolio_risk_state(user_trader)
    recs = portfolio_risk_orchestrator.risk_engine.recommendation_engine.generate_recommendations(
        portfolio_state=p_state.to_dict(),
        concentration_analysis=p_state.metadata.get("concentration", {}),
        correlation_analysis=p_state.metadata.get("correlation", {})
    )
    return [r.to_dict() for r in recs]

@router.get("/kill-switch")
async def get_kill_switch_status(current_user: UserModel = Depends(get_current_user)):
    """Fetch current Portfolio Kill Switch status and audit events."""
    status = portfolio_risk_orchestrator.risk_engine.kill_switch.get_status()
    return status.to_dict()

@router.post("/kill-switch/activate")
async def activate_kill_switch(body: KillSwitchActionRequest, current_user: UserModel = Depends(get_current_user)):
    """Manually activate Portfolio Emergency Kill Switch (HALTED state)."""
    status = portfolio_risk_orchestrator.risk_engine.kill_switch.activate(
        reason=body.reason or "Manual activation by user",
        triggered_by=current_user.name
    )
    return status.to_dict()

@router.post("/kill-switch/recover")
async def recover_kill_switch(body: KillSwitchActionRequest, current_user: UserModel = Depends(get_current_user)):
    """Manually recover Portfolio Kill Switch back to NORMAL state."""
    status = portfolio_risk_orchestrator.risk_engine.kill_switch.recover(
        authorized_by=current_user.name,
        notes=body.reason or "Manual user recovery authorization"
    )
    return status.to_dict()

@router.post("/simulate")
async def simulate_trade_risk(body: TradeSimulationRequest, current_user: UserModel = Depends(get_current_user)):
    """Simulate trade execution through Phase 34 Risk Gate without placing real order."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    res = portfolio_risk_orchestrator.evaluate_order_gate(
        user_trader=user_trader,
        symbol=body.symbol,
        side=body.side,
        allocation_usd=body.allocation_usd,
        leverage=body.leverage or 1,
        stop_loss_price=body.stop_loss_price,
        take_profit_price=body.take_profit_price
    )
    return res
