from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from backend.auth.security import get_optional_current_user
from backend.models.domain import UserModel
from backend.shadow_trading import shadow_engine
from backend.shadow_trading.shadow_fill_simulator import ShadowFillEvent

router = APIRouter(prefix="/api/shadow", tags=["Shadow Trading & Market Replay Engine Phase 36"])

class ReplayStartRequest(BaseModel):
    symbol: Optional[str] = "BTC/USDT"
    playback_speed: Optional[int] = 5
    duration_hours: Optional[float] = 24.0

@router.get("/status")
async def get_shadow_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch current Shadow Engine status for the current user."""
    any_running = any(s.status == "RUNNING" for s in shadow_engine.replay_engine.active_sessions.values())
    is_running = (shadow_engine.status == "RUNNING") and any_running

    status_dict = shadow_engine.get_status()
    status_dict["session_status"] = "RUNNING" if is_running else "IDLE"
    return status_dict

@router.post("/start")
async def start_shadow_session(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Start shadow trading session for current user."""
    shadow_engine.status = "RUNNING"
    return {
        "status": "success",
        "session_status": "RUNNING",
        "trading_mode": "SHADOW",
        "message": "Shadow Trading Session ACTIVATED for your account"
    }

@router.post("/stop")
async def stop_shadow_session(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Stop active shadow session for current user."""
    shadow_engine.status = "IDLE"
    for s in list(shadow_engine.replay_engine.active_sessions.values()):
        s.status = "COMPLETED"
    shadow_engine.replay_engine.active_sessions.clear()

    return {
        "status": "success",
        "session_status": "IDLE",
        "message": "Shadow Trading Session DEACTIVATED for your account"
    }

@router.get("/positions")
async def get_shadow_positions(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch independent shadow positions list across simulated pairs."""
    positions = shadow_engine.position_tracker.get_all_positions()
    
    # If replay is active, tick prices dynamically to simulate live market fluctuations
    if shadow_engine.status == "RUNNING" and shadow_engine.replay_engine.active_sessions:
        import random
        for p in positions:
            mult = 1.0 + random.uniform(-0.0012, 0.0018)
            p.mark_price = round(p.mark_price * mult, 2)
            p.unrealized_pnl_usd = round(p.quantity * (p.mark_price - p.average_entry_price), 2)

    return [p.to_dict() for p in positions]

@router.post("/positions/reset")
async def reset_shadow_positions(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Reset / clear shadow positions."""
    shadow_engine.position_tracker._positions.clear()
    shadow_engine.router.executed_fills.clear()
    return {"status": "success", "message": "Shadow positions cleared"}

@router.get("/orders")
async def get_shadow_orders(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch executed shadow fills and orders blotter."""
    return [f.to_dict() for f in shadow_engine.router.executed_fills]

@router.get("/metrics")
async def get_shadow_metrics(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch shadow metrics summary."""
    return shadow_engine.metrics_tracker.get_summary().to_dict()

@router.get("/orderbook/{symbol:path}")
async def get_shadow_orderbook(symbol: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch live Binance depth snapshot & orderbook ladder."""
    snapshot = shadow_engine.orderbook.get_orderbook(symbol)
    return snapshot.to_dict()

@router.get("/execution-quality")
async def get_shadow_execution_quality(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch shadow execution quality analytics (gross PnL, net PnL, implementation shortfall, fill score)."""
    positions = shadow_engine.position_tracker.get_all_positions()
    analytics = shadow_engine.pnl_engine.compute_pnl_analytics(positions, shadow_engine.router.executed_fills)
    return analytics.to_dict()

@router.post("/replay/start")
async def start_market_replay(body: ReplayStartRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Initialize historical candle, orderbook & trade tape replay session across selected or all pairs."""
    sym = (body.symbol or "ALL").upper()
    speed = body.playback_speed or 5
    shadow_engine.replay_engine.default_playback_speed = speed
    session = shadow_engine.replay_engine.start_replay(
        symbol=sym,
        playback_speed=speed,
        duration_hours=body.duration_hours or 24.0
    )
    shadow_engine.status = "RUNNING"

    # Multi-pair population for comprehensive simulation
    active_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "AVAX/USDT", "DOGE/USDT"]
    for s in active_symbols:
        base_p = shadow_engine.orderbook.BASE_PRICES.get(s, 118450.0)
        qty = 0.25 if "BTC" in s else (1.5 if "ETH" in s else (15.0 if "SOL" in s else 2.5))
        sim_fill = ShadowFillEvent(
            order_id=f"REPLAY-ORD-{s.replace('/', '')[:4]}-{session.session_id[-4:]}",
            symbol=s,
            side="BUY",
            requested_qty=qty,
            filled_qty=qty,
            remaining_qty=0.0,
            expected_price=base_p,
            execution_price=round(base_p * 0.9995, 2),
            fee_usd=round(base_p * qty * 0.00075, 2),
            slippage_cost_usd=1.25,
            latency_ms=18.4,
            latency_rating="EXCELLENT"
        )
        shadow_engine.position_tracker.update_position_from_fill(sim_fill)
        pos = shadow_engine.position_tracker.get_position(s)
        if pos:
            pos.mark_price = round(base_p * 1.0065, 2)
            pos.unrealized_pnl_usd = round(pos.quantity * (pos.mark_price - pos.average_entry_price), 2)
        shadow_engine.router.executed_fills.append(sim_fill)

    return session.to_dict()

@router.post("/replay/stop")
async def stop_market_replay(session_id: Optional[str] = Query(None), current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Stop active market replay session."""
    shadow_engine.status = "IDLE"
    if session_id:
        session = shadow_engine.replay_engine.stop_replay(session_id)
        return session.to_dict() if session else {"status": "success", "message": "Replay stopped"}
    else:
        # Stop and clear all active replay sessions
        for s in list(shadow_engine.replay_engine.active_sessions.values()):
            s.status = "COMPLETED"
        shadow_engine.replay_engine.active_sessions.clear()
        return {"status": "success", "message": "All replay sessions stopped"}

@router.get("/replay/status")
async def get_market_replay_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch active market replay sessions status."""
    return [s.to_dict() for s in shadow_engine.replay_engine.active_sessions.values() if s.status == "RUNNING"]

class ReplaySpeedUpdateRequest(BaseModel):
    playback_speed: Optional[int] = None
    speed: Optional[int] = None

@router.post("/replay/speed")
async def set_market_replay_speed(body: ReplaySpeedUpdateRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Dynamically adjust acceleration speed of active market replay session."""
    target_speed = body.speed if body.speed is not None else (body.playback_speed or 5)
    updated_speed = shadow_engine.replay_engine.set_speed(target_speed)
    return {
        "status": "success",
        "playback_speed": updated_speed,
        "message": f"Market Replay speed updated to {updated_speed}x acceleration."
    }
