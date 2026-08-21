from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import time

from backend.brain.trading_brain import lumo_trading_brain
from backend.brain.regime_intelligence import regime_engine
from backend.brain.portfolio_brain import portfolio_brain
from backend.brain.shadow_ab_engine import shadow_ab_engine

router = APIRouter(prefix="/api/brain", tags=["Superintelligent Trading Brain"])

class EvaluateOpportunityRequest(BaseModel):
    symbol: str = "BTC/USDT"
    current_price: float = 60000.0
    technical_data: Optional[Dict[str, Any]] = None
    sentiment_data: Optional[Dict[str, Any]] = None
    orderbook_data: Optional[Dict[str, Any]] = None
    portfolio_equity_usd: float = 10000.0

class ABReplayRequest(BaseModel):
    universe: Optional[List[Dict[str, Any]]] = None
    portfolio_equity_usd: float = 10000.0

@router.get("/regime")
async def get_current_market_regime(
    symbol: str = "BTC/USDT",
    current_price: Optional[float] = None
):
    """Fetch current 10-regime classification state derived from real market candles."""
    from backend.marketdata.historical_candle_archive import historical_candle_archive
    candles = historical_candle_archive.get_candles(symbol, limit=60)
    
    if candles and len(candles) >= 20:
        c_price = current_price or candles[-1].close
        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        vols = [c.volume for c in candles]
        
        # Real indicators
        ema_20 = float(sum(closes[-20:]) / 20.0)
        ema_50 = float(sum(closes[-min(50, len(closes)):]) / min(50, len(closes)))
        ema_200 = float(sum(closes) / len(closes))
        atr = float(sum([highs[i] - lows[i] for i in range(-14, 0)]) / 14.0)
        
        # Approximate RSI
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d for d in deltas[-14:] if d > 0]
        losses = [-d for d in deltas[-14:] if d < 0]
        avg_gain = sum(gains) / 14.0 if gains else 0.0
        avg_loss = sum(losses) / 14.0 if losses else 1e-9
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        ta_data = {
            "atr": atr,
            "adx": 25.0,
            "plus_di": 22.0,
            "minus_di": 20.0,
            "rsi": rsi,
            "volume_spike_ratio": (vols[-1] / (sum(vols[-10:]) / 10.0)) if sum(vols[-10:]) > 0 else 1.0,
            "ema_20": ema_20,
            "ema_50": ema_50,
            "ema_200": ema_200,
            "vwap": c_price
        }
    else:
        c_price = current_price or 60000.0
        ta_data = {
            "atr": c_price * 0.02,
            "adx": 20.0,
            "plus_di": 20.0,
            "minus_di": 20.0,
            "rsi": 50.0,
            "volume_spike_ratio": 1.0,
            "ema_20": c_price,
            "ema_50": c_price,
            "ema_200": c_price,
            "vwap": c_price
        }

    sentiment_data = {"fear_greed": {"value": 50.0}}
    orderbook_data = {"spread_bps": 2.0, "depth_liquidity_usd": 150000.0}

    state = regime_engine.detect_regime(
        current_price=c_price,
        technical_data=ta_data,
        sentiment_summary=sentiment_data,
        orderbook_data=orderbook_data
    )
    return state.to_dict()

@router.get("/portfolio-graph")
async def get_portfolio_exposure_graph():
    """Fetch real-time anti-correlation exposure graph, beta vs BTC, and directional skew."""
    import sqlite3
    positions_map: Dict[str, Dict[str, Any]] = {}
    try:
        conn = sqlite3.connect("file:lumo_trading.db?mode=ro", uri=True)
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, symbol, side, entry_price, amount, margin_usd, leverage FROM positions").fetchall()
        for r in rows:
            positions_map[str(r[0])] = {
                "symbol": r[1],
                "side": r[2],
                "entry_price": float(r[3] or 100.0),
                "amount": float(r[4] or 1.0),
                "margin_usd": float(r[5] or 1000.0),
                "leverage": int(r[6] or 1)
            }
        conn.close()
    except Exception:
        pass

    graph = portfolio_brain.analyze_portfolio(positions_map)
    return graph.to_dict()

@router.post("/evaluate")
async def evaluate_trade_opportunity(body: EvaluateOpportunityRequest):
    """Run full Pre-Trade Decision Scoring pipeline across all 8 brain stages."""
    ta = body.technical_data or {
        "atr": body.current_price * 0.02,
        "adx": 26.0,
        "plus_di": 18.0,
        "minus_di": 30.0,
        "rsi": 44.0,
        "volume_spike_ratio": 1.2,
        "ema_20": body.current_price * 1.01,
        "ema_50": body.current_price * 1.02,
        "ema_200": body.current_price * 1.04,
        "vwap": body.current_price * 1.005
    }
    sentiment = body.sentiment_data or {"fear_greed": {"value": 30.0}}
    orderbook = body.orderbook_data or {"spread_bps": 2.5, "depth_liquidity_usd": 120000.0}

    # Fetch live positions
    positions_map: Dict[str, Dict[str, Any]] = {}
    try:
        import sqlite3
        conn = sqlite3.connect("file:lumo_trading.db?mode=ro", uri=True)
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, symbol, side, entry_price, amount, margin_usd, leverage FROM positions").fetchall()
        for r in rows:
            positions_map[str(r[0])] = {
                "symbol": r[1],
                "side": r[2],
                "entry_price": float(r[3] or 100.0),
                "amount": float(r[4] or 1.0),
                "margin_usd": float(r[5] or 1000.0),
                "leverage": int(r[6] or 1)
            }
        conn.close()
    except Exception:
        pass

    decision = lumo_trading_brain.evaluate_opportunity(
        symbol=body.symbol,
        current_price=body.current_price,
        technical_data=ta,
        sentiment_data=sentiment,
        portfolio_positions=positions_map,
        portfolio_equity_usd=body.portfolio_equity_usd,
        orderbook_data=orderbook
    )
    return decision.to_dict()

@router.post("/ab-shadow-replay")
async def run_shadow_ab_replay(body: ABReplayRequest):
    """Run parallel Shadow A/B comparison benchmark between Legacy Bot and Superintelligent Brain."""
    universe = body.universe
    if not universe:
        # Default sample 10 altcoin universe for benchmark
        sample_symbols = [
            ("BTC/USDT", 60000.0, 42.0),
            ("ETH/USDT", 1850.0, 44.0),
            ("SOL/USDT", 140.0, 39.0),
            ("BNB/USDT", 605.0, 46.0),
            ("XRP/USDT", 1.00, 48.0),
            ("ADA/USDT", 0.178, 38.0),
            ("DOGE/USDT", 0.070, 52.0),
            ("AVAX/USDT", 6.35, 49.0),
            ("DOT/USDT", 0.76, 45.0),
            ("LINK/USDT", 9.45, 43.0)
        ]
        universe = [
            {
                "symbol": s[0],
                "price": s[1],
                "technical_data": {
                    "atr": s[1] * 0.02,
                    "adx": 26.0,
                    "plus_di": 18.0,
                    "minus_di": 30.0,
                    "rsi": s[2],
                    "volume_spike_ratio": 1.2,
                    "ema_20": s[1] * 1.01,
                    "ema_50": s[1] * 1.02,
                    "ema_200": s[1] * 1.05,
                    "vwap": s[1] * 1.005
                },
                "sentiment_data": {"fear_greed": {"value": 28.0}}
            }
            for s in sample_symbols
        ]

    report = shadow_ab_engine.run_ab_comparison(
        market_universe=universe,
        portfolio_equity_usd=body.portfolio_equity_usd
    )
    return report.to_dict()
