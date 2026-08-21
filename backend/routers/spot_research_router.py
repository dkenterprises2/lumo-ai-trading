"""
FastAPI Router for Lumo Spot Module: New & Meme Coin Research, Discovery, Paper Validation,
and Autonomous Intelligent Learning Bot with Isolated Sub-Wallet.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, Body
from typing import Dict, Any, List, Optional
import time
import uuid
import json
from pydantic import BaseModel

from backend.auth.security import get_optional_current_user
from backend.models.domain import UserModel
from backend.spot_research.coin_discovery_engine import coin_discovery_engine, DiscoveredCoin
from backend.spot_research.coin_classifier import coin_classifier
from backend.spot_research.coin_risk_engine import coin_risk_engine
from backend.spot_research.coin_ai_researcher import coin_ai_researcher, CoinAIResearchDossier
from backend.spot_research.paper_validation_engine import paper_validation_engine
from backend.spot_research.spot_research_evidence_store import spot_research_evidence_store, SpotResearchForensicEvent
from backend.spot_research.spot_autonomous_bot import spot_autonomous_bot, SpotBotConfig

router = APIRouter(prefix="/api/spot", tags=["Spot New & Meme Coin Research"])

# Ensure autonomous bot is initialized and running
@router.on_event("startup")
def startup_spot_bot():
    if spot_autonomous_bot.config.is_enabled:
        spot_autonomous_bot.start()

@router.get("/discovered-coins")
async def get_discovered_coins(
    category: Optional[str] = Query(None, description="Filter: NEW, MEME, TOP_OPPORTUNITIES, HIGH_RISK"),
    force_refresh: bool = Query(False, description="Force re-fetch from Binance & DexScreener"),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch discovered coins aggregated with live classification, risk scores, and AI recommendations."""
    raw_coins = coin_discovery_engine.discover_all_coins(force_refresh=force_refresh)
    results = []

    for coin in raw_coins:
        classification = coin_classifier.classify(coin)
        risk_report = coin_risk_engine.evaluate_risk(coin)
        dossier = coin_ai_researcher.generate_research_dossier(coin, classification, risk_report)

        # Store forensic evidence
        ev = SpotResearchForensicEvent(
            event_id=f"EV-{uuid.uuid4().hex[:8].upper()}",
            symbol=coin.symbol,
            exchange=coin.exchange,
            category=classification.category,
            price_usd=coin.current_price,
            volume_24h_usd=coin.volume_24h_usd,
            liquidity_usd=coin.liquidity_usd,
            spread_bps=coin.spread_bps,
            opportunity_score=dossier.opportunity_score,
            risk_score=dossier.risk_score,
            recommendation=dossier.recommendation,
            data_sources=dossier.data_sources,
            raw_dossier_json=dossier.model_dump_json()
        )
        spot_research_evidence_store.record_event(ev)

        item = {
            "coin": coin.model_dump(),
            "classification": classification.model_dump(),
            "risk_report": risk_report.model_dump(),
            "dossier": dossier.model_dump()
        }

        # Apply category filters
        if category == "MEME" and classification.category != "MEME":
            continue
        elif category == "NEW" and classification.category != "NEW":
            continue
        elif category == "HIGH_RISK" and risk_report.overall_risk_level != "HIGH":
            continue
        elif category == "TOP_OPPORTUNITIES" and dossier.opportunity_score < 60.0:
            continue

        results.append(item)

    # Sort by opportunity score descending
    results = sorted(results, key=lambda x: x["dossier"]["opportunity_score"], reverse=True)

    return {
        "status": "success",
        "total_discovered": len(results),
        "timestamp": time.time(),
        "coins": results
    }

@router.get("/coin/{symbol:path}/research")
async def get_coin_research_dossier(
    symbol: str,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch deep research dossier, multi-vector risk breakdown, and AI catalysts for a specific coin."""
    coins = coin_discovery_engine.discover_all_coins()
    target_coin = next((c for c in coins if c.symbol.lower() == symbol.lower() or c.base_asset.lower() == symbol.lower()), None)

    if not target_coin:
        raise HTTPException(status_code=404, detail=f"Coin '{symbol}' not found in active discovery registry.")

    classification = coin_classifier.classify(target_coin)
    risk_report = coin_risk_engine.evaluate_risk(target_coin)
    dossier = coin_ai_researcher.generate_research_dossier(target_coin, classification, risk_report)

    return {
        "status": "success",
        "coin": target_coin.model_dump(),
        "classification": classification.model_dump(),
        "risk_report": risk_report.model_dump(),
        "dossier": dossier.model_dump(),
        "last_updated": time.time()
    }

@router.post("/coin/{symbol:path}/paper-test")
async def start_paper_validation_test(
    symbol: str,
    allocation_usd: float = Query(250.0, ge=10.0, le=5000.0),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Execute gated paper-trade validation for a coin."""
    coins = coin_discovery_engine.discover_all_coins()
    target_coin = next((c for c in coins if c.symbol.lower() == symbol.lower() or c.base_asset.lower() == symbol.lower()), None)

    if not target_coin:
        raise HTTPException(status_code=404, detail=f"Coin '{symbol}' not found.")

    classification = coin_classifier.classify(target_coin)
    risk_report = coin_risk_engine.evaluate_risk(target_coin)
    dossier = coin_ai_researcher.generate_research_dossier(target_coin, classification, risk_report)

    res = paper_validation_engine.execute_paper_validation(
        coin=target_coin,
        dossier=dossier,
        allocation_usd=allocation_usd
    )

    if res["status"] == "REJECTED":
        raise HTTPException(status_code=400, detail=res["reason"])

    return res

@router.get("/paper-tests")
async def get_paper_validation_tests(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch active and closed paper validation tests."""
    return paper_validation_engine.get_all_trades()

# ==========================================
# AUTONOMOUS INTELLIGENT BOT & SUB-WALLET ENDPOINTS
# ==========================================

@router.get("/bot/status")
async def get_spot_bot_status(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Get live status of autonomous learner bot, dedicated sub-wallet, open trades, and learned lessons."""
    # Ensure bot background loop is active if enabled
    if spot_autonomous_bot.config.is_enabled and not spot_autonomous_bot.is_running():
        spot_autonomous_bot.start()
    return spot_autonomous_bot.get_status()

@router.post("/bot/config")
async def update_spot_bot_config(
    config_update: SpotBotConfig,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Update autonomous spot bot parameters (capital per trade, max positions, risk tolerances, etc.)."""
    spot_autonomous_bot.save_config(config_update)
    if config_update.is_enabled and not spot_autonomous_bot.is_running():
        spot_autonomous_bot.start()
    elif not config_update.is_enabled and spot_autonomous_bot.is_running():
        spot_autonomous_bot.stop()
    return {
        "status": "success",
        "message": "Spot autonomous bot configuration updated successfully",
        "config": spot_autonomous_bot.config.model_dump()
    }

@router.post("/bot/toggle")
async def toggle_spot_bot(
    enabled: Optional[bool] = Query(None),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Start or pause the autonomous spot research bot loop."""
    current_state = spot_autonomous_bot.is_running()
    new_state = (not current_state) if enabled is None else enabled

    cfg = spot_autonomous_bot.config
    cfg.is_enabled = new_state
    spot_autonomous_bot.save_config(cfg)

    if new_state and not current_state:
        spot_autonomous_bot.start()
    elif not new_state and current_state:
        spot_autonomous_bot.stop()

    return {
        "status": "success",
        "is_running": spot_autonomous_bot.is_running(),
        "is_enabled": spot_autonomous_bot.config.is_enabled
    }

class ResetWalletRequest(BaseModel):
    initial_capital_usd: float = 10000.0

@router.post("/wallet/reset")
async def reset_spot_sub_wallet(
    payload: Optional[ResetWalletRequest] = None,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Reset the dedicated Spot Research virtual sub-wallet."""
    capital = payload.initial_capital_usd if payload else 10000.0
    spot_autonomous_bot.sub_wallet.reset_wallet(initial_capital_usd=capital)
    return {
        "status": "success",
        "message": f"Spot Research Sub-Wallet reset with ${capital:,.2f} USDT",
        "wallet": spot_autonomous_bot.sub_wallet.get_wallet_state().model_dump()
    }

@router.post("/bot/close-trade/{trade_id}")
async def close_spot_bot_trade(
    trade_id: str,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Manually close an active autonomous paper trade."""
    trade = spot_autonomous_bot.active_bot_trades.get(trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Active trade not found.")

    curr_price = trade.get("current_price", trade["entry_price"])
    pnl_usd = trade.get("unrealized_pnl_usd", 0.0)
    pnl_pct = trade.get("roi_pct", 0.0)

    spot_autonomous_bot._close_position(
        trade_id=trade_id,
        reason="MANUAL_USER_EXIT",
        exit_price=curr_price,
        net_pnl_usd=pnl_usd,
        pnl_pct=pnl_pct
    )

    return {
        "status": "success",
        "message": f"Closed trade {trade_id} on {trade['symbol']}",
        "pnl_usd": pnl_usd
    }

@router.get("/bot/lessons")
async def get_spot_bot_lessons(
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Fetch self-learning lessons and weight adjustments."""
    lessons = [l.model_dump() for l in spot_autonomous_bot.learned_lessons[:limit]]
    return {
        "status": "success",
        "total_lessons": len(spot_autonomous_bot.learned_lessons),
        "lessons": lessons,
        "adaptive_multipliers": spot_autonomous_bot.category_risk_multipliers
    }

@router.get("/evidence/events")
async def get_forensic_evidence_events(
    limit: int = Query(50, ge=1, le=500),
    category: Optional[str] = Query(None)
):
    """Fetch immutable forensic research evidence events."""
    events = spot_research_evidence_store.query_events(limit=limit, category=category)
    return {"total": len(events), "events": events}

@router.get("/evidence/export/csv")
async def export_evidence_csv():
    """Export research evidence log as CSV."""
    csv_data = spot_research_evidence_store.export_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=spot_research_evidence.csv"}
    )

@router.get("/evidence/export/json")
async def export_evidence_json():
    """Export research evidence log as JSON."""
    return spot_research_evidence_store.export_json()
