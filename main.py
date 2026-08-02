import threading
import time
import os
import json
import asyncio
import logging
import pandas as pd
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import settings
from market_data import MarketDataEngine
from sentiment_engine import SentimentEngine
from ai_strategy import AITradingStrategy
from trader import PaperTrader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Initialize Services
market_engine = MarketDataEngine()
sentiment_engine = SentimentEngine()
ai_strategy = AITradingStrategy()
trader = PaperTrader(initial_balance=settings.PAPER_TRADING_INITIAL_BALANCE)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Database & Restoring Trader State...")
    await trader.initialize_and_restore_state()
    logger.info("Trader State Restored Successfully.")
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

# The dashboard is a separately served Next.js application.  Without this
# middleware, all browser REST requests are rejected before their responses
# reach the frontend, despite the API working for direct clients.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

# Serve Static Assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket Connection Manager for Real-Time Streaming
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected to WebSocket stream. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

ws_manager = ConnectionManager()

# Data Models
class OrderRequest(BaseModel):
    symbol: str
    side: str # LONG or SHORT
    order_type: str = "MARKET" # MARKET, LIMIT, STOP
    allocation_usd: float = 1000.0
    leverage: int = 1
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    trailing_stop_pct: Optional[float] = None

class PositionActionRequest(BaseModel):
    symbol: str
    action: str # CLOSE, PARTIAL_CLOSE, REVERSE, EDIT_SL_TP
    ratio: Optional[float] = 1.0
    new_stop_loss: Optional[float] = None
    new_take_profit: Optional[float] = None

class StrategyConfigRequest(BaseModel):
    strategy_name: str
    risk_mode: str

# Multi-Symbol Cache Storage for Scanner
scanner_cache: Dict[str, Any] = {}

@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Real-Time Low Latency (<250ms target) Data WebSocket Streamer."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive heartbeat & ping listener
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket connection closed: {e}")
        ws_manager.disconnect(websocket)

@app.get("/api/market-summary")
async def get_market_summary(symbol: str = "BTC/USDT", timeframe: str = "1h"):
    price = market_engine.fetch_current_price(symbol)
    df = market_engine.fetch_ohlcv(symbol, timeframe=timeframe, limit=60)
    ta_data = market_engine.calculate_technical_indicators(df)

    chart_list = []
    if not df.empty:
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        for idx, row in df.iterrows():
            chart_list.append({
                "timestamp": int(row['timestamp']),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": float(row['volume']),
                "sma_20": round(float(row['sma_20']), 2) if not pd.isna(row['sma_20']) else float(row['close']),
                "ema_9": round(float(row['ema_9']), 2) if not pd.isna(row['ema_9']) else float(row['close'])
            })

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "current_price": price,
        "rsi": ta_data.get("rsi", 50),
        "macd": ta_data.get("macd", 0),
        "vwap": ta_data.get("vwap", price),
        "atr": ta_data.get("atr", 0.0),
        "trend": ta_data.get("trend", "NEUTRAL"),
        "technical_score": ta_data.get("technical_score", 50.0),
        "ta_summary": ta_data,
        "chart_data": chart_list
    }

@app.get("/api/news-sentiment")
async def get_news_sentiment():
    fear_greed = sentiment_engine.fetch_fear_and_greed_index()
    news_articles = sentiment_engine.fetch_crypto_news()
    sentiment_summary = sentiment_engine.compute_aggregated_sentiment(news_articles, fear_greed)

    return {
        "fear_greed": fear_greed,
        "sentiment_summary": sentiment_summary,
        "news_articles": news_articles
    }

@app.get("/api/ai-signal/{symbol:path}")
async def get_ai_signal(symbol: str, strategy: str = "AI Hybrid", risk_mode: str = "Moderate"):
    price = market_engine.fetch_current_price(symbol)
    df = market_engine.fetch_ohlcv(symbol, timeframe="1h", limit=50)
    ta_data = market_engine.calculate_technical_indicators(df)

    fear_greed = sentiment_engine.fetch_fear_and_greed_index()
    news_articles = sentiment_engine.fetch_crypto_news()
    sentiment_summary = sentiment_engine.compute_aggregated_sentiment(news_articles, fear_greed)

    signal = ai_strategy.evaluate_trading_signal(
        symbol=symbol,
        current_price=price,
        technical_data=ta_data,
        sentiment_summary=sentiment_summary,
        strategy_name=strategy,
        risk_mode=risk_mode
    )
    return signal

@app.get("/api/scanner/summary")
async def get_multi_symbol_scanner():
    """Multi-Symbol Scanner API across all 14 supported crypto pairs."""
    return scanner_cache

@app.get("/api/portfolio")
async def get_portfolio():
    current_prices = {}
    for sym in settings.SUPPORTED_SYMBOLS:
        current_prices[sym] = market_engine.price_cache.get(sym, market_engine.fetch_current_price(sym))

    trader.check_stop_loss_take_profit(current_prices)
    return trader.get_portfolio_summary(current_prices)

@app.get("/api/accounting/audit")
async def get_accounting_audit():
    current_prices = {}
    for sym in settings.SUPPORTED_SYMBOLS:
        current_prices[sym] = market_engine.price_cache.get(sym, market_engine.fetch_current_price(sym))

    pf = trader.get_portfolio_summary(current_prices)
    audit_res = trader.validate_accounting(
        total_portfolio_value=pf["total_portfolio_value"],
        total_open_margin=pf["margin_used"],
        total_unrealized_pnl=pf["total_unrealized_pnl_usd"]
    )
    reconstructed = sum(tx["amount"] for tx in trader.ledger)

    return {
        "wallet": {
            "balance": pf["usdt_balance"],
            "reconstructed_ledger_balance": round(reconstructed, 4),
            "margin_used": pf["margin_used"]
        },
        "ledger": trader.ledger,
        "equity": {
            "portfolio_value": pf["total_portfolio_value"],
            "unrealized_pnl": pf["total_unrealized_pnl_usd"],
            "realized_pnl": pf["closed_pnl_usd"]
        },
        "positions": pf["active_positions"],
        "trades": pf["trade_history"],
        "consistency": {
            "formula": f"Wallet ({pf['usdt_balance']:.2f}) + Margin ({pf['margin_used']:.2f}) + Unrealized PnL ({pf['total_unrealized_pnl_usd']:.2f}) = Portfolio ({pf['total_portfolio_value']:.2f})",
            "mismatch_usdt": audit_res["mismatch_usdt"],
            "ledger_mismatch": audit_res["ledger_mismatch"],
            "within_tolerance": audit_res["within_tolerance"]
        },
        "audit_status": trader.accounting_status,
        "database_sync_status": trader.database_sync_status,
        "last_portfolio_validation": trader.last_validation_time
    }


@app.post("/api/trade/order")
async def execute_manual_order(req: OrderRequest):
    """Advanced Manual Order Execution (LONG/SHORT, Leverage, SL, TP, Trailing Stop)."""
    price = market_engine.fetch_current_price(req.symbol)
    
    sl_price = req.stop_loss_price or (price * 0.975 if req.side.upper() == "LONG" else price * 1.025)
    tp_price = req.take_profit_price or (price * 1.05 if req.side.upper() == "LONG" else price * 0.95)

    res = trader.open_position(
        symbol=req.symbol,
        side=req.side.upper(),
        price=price,
        allocation_usd=req.allocation_usd,
        stop_loss_price=sl_price,
        take_profit_price=tp_price,
        leverage=req.leverage,
        order_type=req.order_type,
        trailing_stop_pct=req.trailing_stop_pct,
        reason=f"Manual Order ({req.side} {req.leverage}x)"
    )
    return res

@app.post("/api/trade/position-action")
async def manage_position(req: PositionActionRequest):
    """Position Actions: Close, Partial Close, Reverse, Edit SL/TP."""
    price = market_engine.fetch_current_price(req.symbol)
    action = req.action.upper()

    if action == "CLOSE":
        return trader.close_position(req.symbol, price, reason="Manual Position Close")
    elif action == "PARTIAL_CLOSE":
        return trader.close_position(req.symbol, price, reason="Partial Take Profit", ratio=req.ratio or 0.5)
    elif action == "REVERSE":
        return trader.reverse_position(req.symbol, price)
    elif action == "EDIT_SL_TP":
        if req.symbol in trader.positions:
            pos = trader.positions[req.symbol]
            if req.new_stop_loss: pos['stop_loss_price'] = req.new_stop_loss
            if req.new_take_profit: pos['take_profit_price'] = req.new_take_profit
            return {"status": "success", "message": f"Updated SL/TP targets for {req.symbol}"}
        return {"status": "error", "message": "Position not found"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@app.post("/api/bot/strategy")
async def update_bot_strategy(req: StrategyConfigRequest):
    """Switch Active Bot Strategy and Risk Mode."""
    trader.active_strategy = req.strategy_name
    trader.risk_mode = req.risk_mode
    logger.info(f"Bot Strategy updated to: {req.strategy_name} ({req.risk_mode})")
    return {"status": "success", "message": f"Strategy switched to {req.strategy_name} ({req.risk_mode})"}

@app.post("/api/bot/toggle")
async def toggle_bot(enable: bool = Query(...)):
    trader.auto_bot_enabled = enable
    status_str = "ACTIVE" if enable else "DISABLED"
    logger.info(f"Auto-Trading Bot state: {status_str}")
    return {"status": "success", "message": f"Auto-Trading Bot is now {status_str}", "auto_bot_enabled": enable}

# Multi-Symbol Continuous Background Scanner & Broadcast Daemon
def background_scanner_loop():
    logger.info("Launching 24/7 Multi-Symbol Scanner & Real-Time Broadcast Loop...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    last_sentiment_update = 0.0
    sentiment_cache = {}

    while True:
        try:
            # Refresh news sentiment every 5 minutes
            if time.time() - last_sentiment_update > 300.0 or not sentiment_cache:
                fg_cache = sentiment_engine.fetch_fear_and_greed_index()
                news_cache = sentiment_engine.fetch_crypto_news()
                sentiment_cache = sentiment_engine.compute_aggregated_sentiment(news_cache, fg_cache)
                last_sentiment_update = time.time()
            current_prices = {}
            scanner_results = []

            for symbol in settings.SUPPORTED_SYMBOLS:
                price = market_engine.fetch_current_price(symbol)
                current_prices[symbol] = price

                df = market_engine.fetch_ohlcv(symbol, limit=40)
                ta = market_engine.calculate_technical_indicators(df)

                signal = ai_strategy.evaluate_trading_signal(
                    symbol=symbol,
                    current_price=price,
                    technical_data=ta,
                    sentiment_summary=sentiment_cache,
                    strategy_name=trader.active_strategy,
                    risk_mode=trader.risk_mode
                )

                scanner_results.append(signal)

            # Sort scanner results
            top_buys = sorted([s for s in scanner_results if "BUY" in s['action']], key=lambda x: x['confidence_score'], reverse=True)
            top_sells = sorted([s for s in scanner_results if "SELL" in s['action']], key=lambda x: x['confidence_score'], reverse=True)

            global scanner_cache
            scanner_cache = {
                "timestamp": time.time(),
                "top_buys": top_buys,
                "top_sells": top_sells,
                "all_pairs": scanner_results
            }

            # Check SL / TP
            trader.check_stop_loss_take_profit(current_prices)

            # Automated 24/7 Bot Trade Execution Loop
            if trader.auto_bot_enabled and trader.usdt_balance >= 100.0:
                best_opportunity = top_buys[0] if top_buys else (top_sells[0] if top_sells else None)
                if best_opportunity and best_opportunity['confidence_score'] >= 65.0:
                    sym = best_opportunity['symbol']
                    side = best_opportunity['direction']
                    if sym not in trader.positions and side in ["LONG", "SHORT"]:
                        alloc = min(1500.0, trader.usdt_balance * 0.20)
                        trader.open_position(
                            symbol=sym,
                            side=side,
                            price=current_prices[sym],
                            allocation_usd=alloc,
                            stop_loss_price=best_opportunity['stop_loss_price'],
                            take_profit_price=best_opportunity['take_profit_price'],
                            leverage=1,
                            reason=f"Auto-Bot 24/7 ({best_opportunity['strategy']}) Confidence: {best_opportunity['confidence_score']}%"
                        )

            # Broadcast Real-Time Data over WebSockets
            portfolio_summary = trader.get_portfolio_summary(current_prices)
            ws_payload = {
                "type": "TICKER_UPDATE",
                "timestamp": time.time(),
                "prices": current_prices,
                "portfolio": portfolio_summary,
                "scanner": scanner_cache
            }
            loop.run_until_complete(ws_manager.broadcast(ws_payload))

        except Exception as e:
            logger.error(f"Error in multi-symbol scanner loop: {e}")

        time.sleep(2.0)  # High-frequency 2-second scan interval

scanner_thread = threading.Thread(target=background_scanner_loop, daemon=True)
scanner_thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
