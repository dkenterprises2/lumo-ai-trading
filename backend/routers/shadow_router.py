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
    """Fetch current Shadow Engine status, feed readiness, and safety guard verification."""
    return shadow_engine.get_status()

@router.post("/start")
async def start_shadow_session(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Start shadow trading session with governance pre-approval checks."""
    res = shadow_engine.start_shadow_session()
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/stop")
async def stop_shadow_session(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Stop active shadow session."""
    return shadow_engine.stop_shadow_session()

@router.get("/positions")
async def get_shadow_positions(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch independent shadow positions list."""
    positions = shadow_engine.position_tracker.get_all_positions()
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
    """Initialize historical candle, orderbook & trade tape replay session."""
    sym = (body.symbol or "BTC/USDT").upper()
    speed = body.playback_speed or 5
    session = shadow_engine.replay_engine.start_replay(
        symbol=sym,
        playback_speed=speed,
        duration_hours=body.duration_hours or 24.0
    )
    shadow_engine.status = "RUNNING"

    # If no positions exist, simulate an active shadow fill execution to populate the replay session
    if len(shadow_engine.position_tracker.get_all_positions()) == 0:
        base_p = shadow_engine.orderbook.BASE_PRICES.get(sym, 118450.0)
        sim_fill = ShadowFillEvent(
            order_id=f"REPLAY-ORD-{session.session_id[-4:]}",
            symbol=sym,
            side="BUY",
            requested_qty=0.25 if "BTC" in sym else 1.5,
            filled_qty=0.25 if "BTC" in sym else 1.5,
            remaining_qty=0.0,
            expected_price=base_p,
            execution_price=round(base_p * 0.9995, 2),
            fee_usd=round(base_p * 0.25 * 0.00075, 2),
            slippage_cost_usd=1.25,
            latency_ms=18.4,
            latency_rating="EXCELLENT"
        )
        shadow_engine.position_tracker.update_position_from_fill(sim_fill)
        pos = shadow_engine.position_tracker.get_position(sym)
        if pos:
            pos.mark_price = base_p
            pos.unrealized_pnl_usd = round((pos.mark_price - pos.average_entry_price) * pos.quantity, 2)
        shadow_engine.router.executed_fills.append(sim_fill)

    return session.to_dict()

@router.post("/replay/stop")
async def stop_market_replay(session_id: Optional[str] = Query(None), current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Stop active market replay session."""
    if session_id:
        session = shadow_engine.replay_engine.stop_replay(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Replay session not found")
        shadow_engine.status = "IDLE"
        return session.to_dict()
    else:
        # Stop all active sessions
        for s in shadow_engine.replay_engine.active_sessions.values():
            s.status = "COMPLETED"
        shadow_engine.status = "IDLE"
        return {"status": "success", "message": "All replay sessions stopped"}

@router.get("/replay/status")
async def get_market_replay_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch active market replay sessions status."""
    return [s.to_dict() for s in shadow_engine.replay_engine.active_sessions.values()]
