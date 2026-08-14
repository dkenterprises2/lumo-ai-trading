from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from backend.auth.security import get_current_user
from backend.models.domain import UserModel
from backend.shadow_trading import shadow_engine

router = APIRouter(prefix="/api/shadow", tags=["Shadow Trading & Market Replay Engine Phase 36"])

class ReplayStartRequest(BaseModel):
    symbol: Optional[str] = "BTC/USDT"
    playback_speed: Optional[int] = 5
    duration_hours: Optional[float] = 24.0

@router.get("/status")
async def get_shadow_status(current_user: UserModel = Depends(get_current_user)):
    """Fetch current Shadow Engine status, feed readiness, and safety guard verification."""
    return shadow_engine.get_status()

@router.post("/start")
async def start_shadow_session(current_user: UserModel = Depends(get_current_user)):
    """Start shadow trading session with governance pre-approval checks."""
    res = shadow_engine.start_shadow_session()
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/stop")
async def stop_shadow_session(current_user: UserModel = Depends(get_current_user)):
    """Stop active shadow session."""
    return shadow_engine.stop_shadow_session()

@router.get("/positions")
async def get_shadow_positions(current_user: UserModel = Depends(get_current_user)):
    """Fetch independent shadow positions list."""
    positions = shadow_engine.position_tracker.get_all_positions()
    return [p.to_dict() for p in positions]

@router.get("/orders")
async def get_shadow_orders(current_user: UserModel = Depends(get_current_user)):
    """Fetch executed shadow fills and orders blotter."""
    return [f.to_dict() for f in shadow_engine.router.executed_fills]

@router.get("/metrics")
async def get_shadow_metrics(current_user: UserModel = Depends(get_current_user)):
    """Fetch shadow metrics summary."""
    return shadow_engine.metrics_tracker.get_summary().to_dict()

@router.get("/orderbook/{symbol}")
async def get_shadow_orderbook(symbol: str, current_user: UserModel = Depends(get_current_user)):
    """Fetch live Binance depth snapshot & orderbook ladder."""
    snapshot = shadow_engine.orderbook.get_orderbook(symbol)
    return snapshot.to_dict()

@router.get("/execution-quality")
async def get_shadow_execution_quality(current_user: UserModel = Depends(get_current_user)):
    """Fetch shadow execution quality analytics (gross PnL, net PnL, implementation shortfall, fill score)."""
    positions = shadow_engine.position_tracker.get_all_positions()
    analytics = shadow_engine.pnl_engine.compute_pnl_analytics(positions, shadow_engine.router.executed_fills)
    return analytics.to_dict()

@router.post("/replay/start")
async def start_market_replay(body: ReplayStartRequest, current_user: UserModel = Depends(get_current_user)):
    """Initialize historical candle, orderbook & trade tape replay session."""
    session = shadow_engine.replay_engine.start_replay(
        symbol=body.symbol or "BTC/USDT",
        playback_speed=body.playback_speed or 5,
        duration_hours=body.duration_hours or 24.0
    )
    return session.to_dict()

@router.post("/replay/stop")
async def stop_market_replay(session_id: str = Query(...), current_user: UserModel = Depends(get_current_user)):
    """Stop active market replay session."""
    session = shadow_engine.replay_engine.stop_replay(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Replay session not found")
    return session.to_dict()

@router.get("/replay/status")
async def get_market_replay_status(current_user: UserModel = Depends(get_current_user)):
    """Fetch active market replay sessions status."""
    return [s.to_dict() for s in shadow_engine.replay_engine.active_sessions.values()]
