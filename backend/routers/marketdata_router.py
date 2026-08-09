from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.marketdata.tick_ingestion import tick_ingestion_engine
from backend.marketdata.orderbook_engine import orderbook_engine
from backend.marketdata.dom_processor import dom_processor
from backend.marketdata.orderbook_imbalance import orderbook_imbalance
from backend.marketdata.spread_analytics import spread_analytics
from backend.marketdata.volume_profile import volume_profile_engine
from backend.marketdata.footprint_engine import footprint_engine
from backend.marketdata.liquidity_heatmap import liquidity_heatmap
from backend.marketdata.microstructure_alpha import microstructure_alpha
from backend.marketdata.spoofing_detector import spoofing_detector
from backend.marketdata.layering_detector import layering_detector
from backend.marketdata.replay_service import replay_service

router = APIRouter(tags=["Real-Time Market Data & Order Book Intelligence"])

@router.get("/api/marketdata/ticks/{symbol}")
async def get_market_ticks(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return {"ticks": tick_ingestion_engine.get_recent_ticks(symbol)}

@router.get("/api/marketdata/orderbook/{symbol}")
async def get_orderbook(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return orderbook_engine.get_orderbook(symbol, 10)

@router.get("/api/marketdata/orderbook/{symbol}/depth/{levels}")
async def get_orderbook_depth(symbol: str, levels: int, current_user: UserModel = Depends(get_current_user)):
    return orderbook_engine.get_orderbook(symbol, levels)

@router.get("/api/marketdata/dom/{symbol}")
async def get_dom_metrics(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return dom_processor.process_dom(symbol)

@router.get("/api/marketdata/imbalance/{symbol}")
async def get_orderbook_imbalance(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return orderbook_imbalance.get_imbalance(symbol)

@router.get("/api/marketdata/spread/{symbol}")
async def get_spread_metrics(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return spread_analytics.get_spread_metrics(symbol)

@router.get("/api/marketdata/volume-profile/{symbol}")
async def get_volume_profile(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return volume_profile_engine.get_volume_profile(symbol)

@router.get("/api/marketdata/footprint/{symbol}")
async def get_footprint_analytics(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return footprint_engine.get_footprint(symbol)

@router.get("/api/marketdata/liquidity-heatmap/{symbol}")
async def get_liquidity_heatmap(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return liquidity_heatmap.get_heatmap(symbol)

@router.get("/api/marketdata/microstructure-signals/{symbol}")
async def get_microstructure_signals(symbol: str, current_user: UserModel = Depends(get_current_user)):
    return microstructure_alpha.generate_signal(symbol)

@router.get("/api/marketdata/spoofing-alerts")
async def get_spoofing_alerts(current_user: UserModel = Depends(get_current_user)):
    return {"alerts": spoofing_detector.list_alerts()}

@router.get("/api/marketdata/layering-alerts")
async def get_layering_alerts(current_user: UserModel = Depends(get_current_user)):
    return {"alerts": layering_detector.list_alerts()}

@router.post("/api/marketdata/replay/start")
async def start_replay_session(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    symbol = body.get("symbol", "BTC/USDT")
    speed = body.get("speed", 1.0)
    return replay_service.start_replay(symbol, speed)

@router.get("/api/marketdata/replay/{session_id}")
async def get_replay_session(session_id: str, current_user: UserModel = Depends(get_current_user)):
    return replay_service.get_session(session_id)

@router.post("/api/marketdata/replay/{session_id}/pause")
async def pause_replay_session(session_id: str, current_user: UserModel = Depends(get_current_user)):
    return replay_service.pause_session(session_id)

@router.post("/api/marketdata/replay/{session_id}/resume")
async def resume_replay_session(session_id: str, current_user: UserModel = Depends(get_current_user)):
    return replay_service.resume_session(session_id)
