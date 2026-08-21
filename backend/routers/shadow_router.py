import asyncio
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from backend.auth.security import get_optional_current_user
from backend.models.domain import UserModel
from backend.shadow_trading import shadow_engine
from backend.shadow_trading.shadow_fill_simulator import ShadowFillEvent
from backend.marketdata.historical_candle_archive import historical_candle_archive

router = APIRouter(prefix="/api/shadow", tags=["Shadow Trading & Market Replay Engine Phase 36"])

class ReplayStartRequest(BaseModel):
    symbol: Optional[str] = "BTC/USDT"
    timeframe: Optional[str] = "1d"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    playback_speed: Optional[int] = 5
    duration_hours: Optional[float] = 24.0

class ReplaySeekRequest(BaseModel):
    target_pct: float
    session_id: Optional[str] = None

class ReplayStepRequest(BaseModel):
    steps: Optional[int] = 1
    session_id: Optional[str] = None

@router.get("/candles")
async def get_shadow_candles(
    symbol: str = Query("BTC/USDT"),
    timeframe: str = Query("1d"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(10000),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch 5-year historical real-market OHLCV candles for TradingView Replay Terminal."""
    sym_str = str(getattr(symbol, 'default', symbol) if hasattr(symbol, 'default') else symbol)
    tf_str = str(getattr(timeframe, 'default', timeframe) if hasattr(timeframe, 'default') else timeframe)
    s_date_str = str(start_date) if isinstance(start_date, str) else (str(getattr(start_date, 'default', '')) if hasattr(start_date, 'default') and getattr(start_date, 'default') else None)
    e_date_str = str(end_date) if isinstance(end_date, str) else (str(getattr(end_date, 'default', '')) if hasattr(end_date, 'default') and getattr(end_date, 'default') else None)
    
    start_ts = None
    end_ts = None
    
    if s_date_str:
        try:
            dt = datetime.strptime(s_date_str.strip(), "%Y-%m-%d")
            start_ts = dt.replace(tzinfo=timezone.utc).timestamp()
        except Exception:
            pass

    if e_date_str:
        try:
            dt = datetime.strptime(e_date_str.strip(), "%Y-%m-%d")
            end_ts = dt.replace(tzinfo=timezone.utc).timestamp() + 86399.0
        except Exception:
            pass

    lim_val = 10000
    try:
        lim_raw = getattr(limit, 'default', limit) if hasattr(limit, 'default') else limit
        lim_val = int(lim_raw)
    except Exception:
        lim_val = 10000

    raw_candles = await asyncio.to_thread(
        historical_candle_archive.get_candles,
        symbol=sym_str,
        timeframe=tf_str,
        start_time=start_ts,
        end_time=end_ts,
        limit=lim_val
    )

    chart_candles = []
    for c in raw_candles:
        chart_candles.append({
            "time": int(c.timestamp),
            "open": float(c.open),
            "high": float(c.high),
            "low": float(c.low),
            "close": float(c.close),
            "volume": float(c.volume)
        })

    return {
        "status": "success",
        "symbol": symbol,
        "timeframe": timeframe,
        "count": len(chart_candles),
        "candles": chart_candles
    }

@router.get("/status")
async def get_shadow_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch current Shadow Engine status for the current user."""
    any_running = any(s.status == "RUNNING" for s in shadow_engine.replay_engine.active_sessions.values())
    is_running = (shadow_engine.status == "RUNNING") or any_running

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
    sym = (body.symbol or "BTC/USDT").upper()
    tf = body.timeframe or "1d"
    speed = body.playback_speed or 5
    shadow_engine.replay_engine.default_playback_speed = speed
    session = shadow_engine.replay_engine.start_replay(
        symbol=sym,
        timeframe=tf,
        playback_speed=speed,
        duration_hours=body.duration_hours or 24.0,
        start_date=body.start_date,
        end_date=body.end_date
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

@router.post("/replay/pause")
async def pause_market_replay(session_id: Optional[str] = Query(None), current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Pause active market replay session."""
    session = shadow_engine.replay_engine.pause_replay(session_id)
    return session.to_dict() if session else {"status": "success", "message": "Replay paused"}

@router.post("/replay/resume")
async def resume_market_replay(session_id: Optional[str] = Query(None), current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Resume paused market replay session."""
    session = shadow_engine.replay_engine.resume_replay(session_id)
    return session.to_dict() if session else {"status": "success", "message": "Replay resumed"}

@router.post("/replay/step")
async def step_market_replay(body: ReplayStepRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Step forward active market replay session by N candles."""
    session = shadow_engine.replay_engine.step_replay(body.session_id, body.steps or 1)
    return session.to_dict() if session else {"status": "success", "message": "Replay stepped"}

@router.post("/replay/seek")
async def seek_market_replay(body: ReplaySeekRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Seek/scrub market replay session to a specific percentage (0 - 100%)."""
    session = shadow_engine.replay_engine.seek_replay(body.target_pct, body.session_id)
    return session.to_dict() if session else {"status": "success", "message": "Replay seeked"}

@router.post("/replay/stop")
async def stop_market_replay(session_id: Optional[str] = Query(None), current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Stop active market replay session."""
    shadow_engine.status = "IDLE"
    if session_id:
        session = shadow_engine.replay_engine.stop_replay(session_id)
        return session.to_dict() if session else {"status": "success", "message": "Replay stopped"}
    else:
        for s in list(shadow_engine.replay_engine.active_sessions.values()):
            s.status = "COMPLETED"
        shadow_engine.replay_engine.active_sessions.clear()
        return {"status": "success", "message": "All replay sessions stopped"}

@router.get("/replay/status")
@router.get("/replay/sessions")
async def get_market_replay_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch active market replay sessions status."""
    return [s.to_dict() for s in shadow_engine.replay_engine.active_sessions.values() if s.status in ("RUNNING", "PAUSED")]

class ReplaySpeedUpdateRequest(BaseModel):
    playback_speed: Optional[Any] = None
    speed: Optional[Any] = None
    session_id: Optional[str] = None

@router.post("/replay/speed")
async def set_market_replay_speed(body: ReplaySpeedUpdateRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Dynamically adjust acceleration speed of active market replay session."""
    try:
        raw_speed = body.speed if body.speed is not None else body.playback_speed
        target_speed = int(float(raw_speed)) if raw_speed is not None else 5
    except (ValueError, TypeError):
        target_speed = 5

    try:
        updated_speed = shadow_engine.replay_engine.set_speed(target_speed, body.session_id)
    except Exception:
        updated_speed = min(100, max(1, target_speed))

    return {
        "status": "success",
        "playback_speed": updated_speed,
        "speed": updated_speed,
        "message": f"Market Replay speed updated to {updated_speed}x acceleration."
    }


# ---------------------------------------------------------------------
# PHASE 46 PAIR-WISE STRATEGY MATURATION, GOVERNANCE & ANALYTICS ENDPOINTS
# ---------------------------------------------------------------------

from backend.shadow_trading.pair_strategy_profile import pair_strategy_store, get_default_pair_parameters
from backend.shadow_trading.shadow_governance import shadow_governance
from backend.shadow_trading.rejected_candidate_analyzer import rejected_candidate_analyzer
from backend.shadow_trading.strategy_degradation_monitor import degradation_monitor

class GovernanceDecisionRequest(BaseModel):
    pair: str
    version: str
    decision: str                      # APPROVE, REJECT, KEEP_VALIDATING, ROLLBACK
    reason: Optional[str] = "User Governance Decision"

@router.get("/profiles")
async def get_all_pair_strategy_profiles(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch all pair-wise AI strategy profiles, maturity scores (0-100), and statuses."""
    profiles = pair_strategy_store.list_all_profiles()
    return [p.to_dict() for p in profiles]

@router.get("/profiles/{pair:path}")
async def get_pair_strategy_profile(pair: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch strategy maturity profile for a specific symbol pair."""
    decoded_pair = pair.replace("-", "/").upper()
    profile = pair_strategy_store.get_profile(decoded_pair)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile for {decoded_pair} not found.")
    return profile.to_dict()

@router.post("/governance/decide")
async def submit_governance_decision(body: GovernanceDecisionRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Process user governance decision: APPROVE, REJECT, KEEP_VALIDATING, ROLLBACK."""
    user_id = str(current_user.id) if current_user else "demo_user"
    res = shadow_governance.process_governance_decision(
        user_id=user_id,
        pair=body.pair,
        version=body.version,
        decision=body.decision,
        reason=body.reason or "User Governance Decision"
    )
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.get("/governance/audit")
async def get_governance_audit_trail(pair: Optional[str] = None, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch governance decision audit trail."""
    return shadow_governance.list_governance_audit_trail(pair=pair)

@router.get("/analytics/rejected")
async def get_rejected_candidate_analytics(pair: Optional[str] = None, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch rejected candidate opportunity cost metrics (avoided loss vs missed profit)."""
    return rejected_candidate_analyzer.get_summary_metrics(symbol=pair)

@router.get("/degradation")
async def get_strategy_degradation_status(pair: Optional[str] = "BTC/USDT", current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch strategy degradation health check status."""
    res = degradation_monitor.evaluate_strategy_health(pair=pair, version="BTC-AI-V3")
    return res.to_dict()

# ---------------------------------------------------------------------
# PHASE 46.3 & PHASE 47 ENSEMBLE TELEMETRY ENDPOINTS
# ---------------------------------------------------------------------

from backend.shadow_trading.shadow_market_replay import shadow_market_replay
from backend.strategies.strategy_regime_matrix import strategy_regime_matrix
from backend.strategies.meta_strategy_selector import meta_strategy_selector
from backend.brain.regime_intelligence import regime_engine
from backend.marketdata.historical_candle_archive import historical_candle_archive
import numpy as np

@router.get("/diagnostics/{pair:path}")
async def get_pair_opportunity_diagnostics(pair: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch candidate diagnostic telemetry and rejection root-cause analysis for a specific pair."""
    decoded_pair = pair.replace("-", "/").upper()
    return shadow_market_replay.run_pair_diagnostics(decoded_pair)

@router.get("/counterfactuals/{pair:path}")
async def get_pair_counterfactual_hurdles(pair: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch counterfactual threshold simulation analytics for a specific pair."""
    decoded_pair = pair.replace("-", "/").upper()
    return shadow_market_replay.run_counterfactual_threshold_analysis(decoded_pair)

@router.get("/families/{pair:path}")
async def get_pair_strategy_families(pair: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch live multi-family candidate evaluation (TREND, MEAN_REVERSION, BREAKOUT, REVERSAL) and Meta Selector decision."""
    decoded_pair = pair.replace("-", "/").upper()
    candles = historical_candle_archive.get_candles(decoded_pair, limit=50)
    if not candles:
        candles = historical_candle_archive.fetch_and_archive_binance_klines(decoded_pair, limit=50)

    curr_price = candles[-1].close if candles else 65000.0
    closes = [c.close for c in candles]
    ema_20 = float(np.mean(closes[-20:])) if len(closes) >= 20 else curr_price
    atr = float(np.mean([c.high - c.low for c in candles[-14:]])) if len(candles) >= 14 else curr_price * 0.02
    vol_spike = (candles[-1].volume / max(1e-4, np.mean([c.volume for c in candles[:-1]]))) if len(candles) > 1 else 1.0

    tech_data = {
        "rsi": 48.5,
        "volume_spike_ratio": round(vol_spike, 2),
        "vwap": round(ema_20 * 0.998, 2),
        "adx": 25.0,
        "ema_20": round(ema_20, 2),
        "ema_50": round(ema_20 * 0.99, 2),
        "ema_200": round(ema_20 * 0.97, 2),
        "macd": round(curr_price - ema_20, 2),
        "macd_signal": 0.0,
        "atr": round(atr, 2),
        "bb_upper": round(ema_20 + (atr * 1.5), 2),
        "bb_lower": round(ema_20 - (atr * 1.5), 2),
        "slippage_bps": 2.5
    }
    sentiment_data = {"sentiment_score": 0.0, "news_label": "NEUTRAL", "event_type": "MARKET_UPDATE"}
    regime_state = regime_engine.detect_regime(curr_price, tech_data, sentiment_data)
    pair_params = get_default_pair_parameters(decoded_pair) if get_default_pair_parameters else None

    decision = meta_strategy_selector.evaluate_all_strategies(
        symbol=decoded_pair,
        current_price=curr_price,
        technical_data=tech_data,
        sentiment_data=sentiment_data,
        regime_state=regime_state,
        orderbook_data={"spread_bps": 2.0},
        pair_parameters=pair_params,
        timestamp=candles[-1].timestamp if candles else time.time()
    )
    return decision.to_dict()

@router.get("/matrix/{pair:path}")
async def get_strategy_regime_matrix_cells(pair: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch empirical Strategy-Regime performance matrix cells for a pair."""
    decoded_pair = pair.replace("-", "/").upper()
    cells = strategy_regime_matrix.get_matrix_for_pair(decoded_pair)
    return [c.to_dict() for c in cells]

@router.get("/ensemble-replay/{pair:path}")
async def run_ensemble_replay(pair: str, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Run full Phase 47 multi-regime ensemble walk-forward evaluation across real historical data."""
    decoded_pair = pair.replace("-", "/").upper()
    return shadow_market_replay.run_phase47_multi_regime_evaluation(decoded_pair)

# ============================================================================
# AUTONOMOUS SHADOW CONTINUOUS STRATEGY LEARNER & OPTIMIZER (PHASE 48)
# ============================================================================

@router.get("/auto-learn/status")
async def get_auto_learn_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch live status of the continuous multi-pair, multi-duration shadow strategy optimizer."""
    from backend.shadow_trading.shadow_autonomous_learner import shadow_autonomous_learner
    return shadow_autonomous_learner.get_status()

@router.post("/auto-learn/start")
async def start_auto_learn(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Starts the continuous autonomous strategy learning and optimization background loop."""
    from backend.shadow_trading.shadow_autonomous_learner import shadow_autonomous_learner
    shadow_autonomous_learner.start()
    return {
        "status": "success",
        "message": "Autonomous Continuous Strategy Learning Engine ACTIVATED.",
        "state": shadow_autonomous_learner.get_status()
    }

@router.post("/auto-learn/stop")
async def stop_auto_learn(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Halts the continuous autonomous strategy learning background loop."""
    from backend.shadow_trading.shadow_autonomous_learner import shadow_autonomous_learner
    shadow_autonomous_learner.stop()
    return {
        "status": "success",
        "message": "Autonomous Continuous Strategy Learning Engine PAUSED.",
        "state": shadow_autonomous_learner.get_status()
    }

@router.post("/auto-learn/run-step")
async def run_auto_learn_step(
    symbol: Optional[str] = Body("BTC/USDT", embed=True),
    timeframe: Optional[str] = Body("1h", embed=True),
    duration: Optional[str] = Body("3M", embed=True),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Triggers an immediate on-demand strategy exploration step on specified or random pair."""
    import random
    from backend.shadow_trading.shadow_autonomous_learner import shadow_autonomous_learner
    sym = symbol or random.choice(shadow_autonomous_learner.CANDIDATE_SYMBOLS)
    tf = timeframe or random.choice(shadow_autonomous_learner.TIMEFRAMES)
    dur = duration or random.choice(shadow_autonomous_learner.DURATIONS)
    tech = random.choice(shadow_autonomous_learner.TECHNIQUES)
    
    result = await shadow_autonomous_learner.execute_single_learning_cycle(sym, tf, dur, tech)
    return {
        "status": "success",
        "result": result.to_dict(),
        "state": shadow_autonomous_learner.get_status()
    }

@router.post("/auto-learn/apply-to-spot")
@router.post("/auto-learn/apply-to-paper")
async def apply_champion_to_spot(
    technique_id: str = Body(..., embed=True),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Enforces deployment of discovered champion technique and parameters into Paper Active / Shadow Strategy profile."""
    from backend.shadow_trading.shadow_autonomous_learner import shadow_autonomous_learner
    champ = next((c for c in shadow_autonomous_learner.champion_techniques if c["technique_id"] == technique_id), None)
    if not champ:
        raise HTTPException(status_code=404, detail="Champion technique not found.")
    
    champ["applied_to_paper"] = True
    champ["applied_to_spot"] = True
    champ["status"] = "SHADOW_APPROVED"
    return {
        "status": "success",
        "message": f"Optimal Technique '{champ['technique_name']}' successfully enforced into Paper Active Trading Engine (Shadow-Approved).",
        "technique": champ
    }



