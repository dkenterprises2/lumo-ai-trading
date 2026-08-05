import threading
import time
import os
import json
import asyncio
import sqlite3
import logging
import pandas as pd
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Body, WebSocket, WebSocketDisconnect, Depends

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import settings
from market_data import MarketDataEngine
from sentiment_engine import SentimentEngine
from ai_strategy import AITradingStrategy
from trader import PaperTrader, trader_manager
from backend.auth.security import get_current_user, get_db
from backend.models.domain import UserModel
from backend.core.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

# Initialize Services
market_engine = MarketDataEngine()
sentiment_engine = SentimentEngine()
ai_strategy = AITradingStrategy()
trader = PaperTrader(initial_balance=settings.PAPER_TRADING_INITIAL_BALANCE)

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[LIFESPAN] Capturing Main Event Loop & Initializing Database...")
    main_loop = asyncio.get_running_loop()
    trader.set_main_event_loop(main_loop)
    trader_manager.set_main_event_loop(main_loop)

    await trader.initialize_and_restore_state()
    logger.info(f"[LIFESPAN] State restoration complete. Final state: {trader.state}")

    logger.info("[STARTUP] Printing all registered FastAPI routes during startup:")
    from backend.routers.auth_router import router as _auth_r
    for r in _auth_r.routes:
        logger.info(f"  Auth Router Route: {r.methods} {r.path}")
    for r in app.router.routes:
        if hasattr(r, 'path'):
            logger.info(f"  App Route: {getattr(r, 'methods', 'ALL')} {r.path}")

    # Launch background scanner worker thread ONLY after database restore completes
    if os.getenv("TESTING") != "true":
        logger.info("[LIFESPAN] Starting background_scanner_loop worker thread...")
        scanner_thread = threading.Thread(target=background_scanner_loop, daemon=True)
        scanner_thread.start()
        logger.info("[LIFESPAN] Background scanner thread started successfully.")


    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

# Configure CORS Middleware at top of middleware stack

cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

raw_cors = getattr(settings, "CORS_ALLOWED_ORIGINS", "")
if isinstance(raw_cors, str):
    cors_origins.extend([o.strip() for o in raw_cors.split(",") if o.strip()])
elif isinstance(raw_cors, (list, tuple)):
    cors_origins.extend([o.strip() for o in raw_cors if isinstance(o, str) and o.strip()])

cors_origins = list(dict.fromkeys(cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request

@app.middleware("http")
async def log_incoming_requests(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    client_ip = request.client.host if request.client else "Unknown"
    logger.info(f"[BACKEND_REQUEST]\n{request.method} {request.url.path}\nHost: {request.headers.get('host')}\nOrigin: {request.headers.get('origin')}\nReferer: {request.headers.get('referer')}\nClient IP: {client_ip}")
    response = await call_next(request)
    return response




from backend.routers.auth_router import router as auth_router

app.include_router(auth_router)

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
    strategy_name: Optional[str] = None
    risk_mode: Optional[str] = None

class ExecutionParametersRequest(BaseModel):
    default_allocation_usd: Optional[float] = 1000.0
    default_leverage: Optional[int] = 1



# Multi-Symbol Cache Storage for Scanner
scanner_cache: Dict[str, Any] = {}

@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Real-Time Low Latency (<250ms target) Data WebSocket Streamer."""
    origin = websocket.headers.get("origin", "")
    allowed_origins = [o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
    if allowed_origins and origin not in allowed_origins:
        logger.warning(f"WebSocket connection rejected from origin: {origin}")
        await websocket.close(code=4001)
        return
    
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
async def get_portfolio(current_user: UserModel = Depends(get_current_user)):
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    current_prices = {}
    for sym in settings.SUPPORTED_SYMBOLS:
        current_prices[sym] = market_engine.price_cache.get(sym, market_engine.fetch_current_price(sym))

    user_trader.check_stop_loss_take_profit(current_prices)
    return user_trader.get_portfolio_summary(current_prices)

@app.get("/api/accounting/audit")
async def get_accounting_audit(current_user: UserModel = Depends(get_current_user)):
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    current_prices = {}
    for sym in settings.SUPPORTED_SYMBOLS:
        current_prices[sym] = market_engine.price_cache.get(sym, market_engine.fetch_current_price(sym))

    pf = user_trader.get_portfolio_summary(current_prices)
    audit_res = user_trader.validate_accounting(
        total_portfolio_value=pf["total_portfolio_value"],
        total_open_margin=pf["margin_used"],
        total_unrealized_pnl=pf["total_unrealized_pnl_usd"]
    )
    reconstructed = sum(tx["amount"] for tx in user_trader.ledger)

    return {
        "wallet": {
            "balance": pf["usdt_balance"],
            "reconstructed_ledger_balance": round(reconstructed, 4),
            "margin_used": pf["margin_used"]
        },
        "ledger": user_trader.ledger,
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
        "audit_status": user_trader.accounting_status,
        "database_sync_status": user_trader.database_sync_status,
        "last_portfolio_validation": user_trader.last_validation_time
    }


class WalletFundsRequest(BaseModel):
    amount: float

@app.post("/api/wallet/deposit")
async def deposit_virtual_funds(body: WalletFundsRequest, current_user: UserModel = Depends(get_current_user)):
    """Deposit virtual USDT capital into the user's paper trading wallet."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be greater than zero.")

    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    tx = user_trader._execute_ledger_transaction(
        tx_type="DEPOSIT",
        amount=body.amount,
        reference_id="USER_DEPOSIT",
        description=f"Virtual Capital Deposit of ${body.amount:.2f} USDT"
    )
    user_trader._sync_save_portfolio()
    return {
        "status": "success",
        "message": f"Successfully deposited ${body.amount:.2f} USDT virtual funds.",
        "usdt_balance": user_trader.usdt_balance,
        "transaction": tx
    }

@app.post("/api/wallet/withdraw")
async def withdraw_virtual_funds(body: WalletFundsRequest, current_user: UserModel = Depends(get_current_user)):
    """Withdraw virtual USDT capital from the user's paper trading wallet."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be greater than zero.")

    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    if user_trader.usdt_balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient USDT balance. Available: ${user_trader.usdt_balance:.2f} USDT, Requested: ${body.amount:.2f} USDT"
        )

    tx = user_trader._execute_ledger_transaction(
        tx_type="WITHDRAWAL",
        amount=-abs(body.amount),
        reference_id="USER_WITHDRAWAL",
        description=f"Virtual Capital Withdrawal of ${body.amount:.2f} USDT"
    )
    user_trader._sync_save_portfolio()
    return {
        "status": "success",
        "message": f"Successfully withdrew ${body.amount:.2f} USDT virtual funds.",
        "usdt_balance": user_trader.usdt_balance,
        "transaction": tx
    }

@app.post("/api/wallet/reset-paper-account")
async def reset_user_paper_account(current_user: UserModel = Depends(get_current_user)):
    """Reset paper trading account balance to default $10,000 USDT and clear all positions/trades."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    res = user_trader.reset_paper_account(default_balance=10000.0)
    await user_trader.flush_persistence()
    return res

@app.delete("/api/user/delete-account")
async def delete_user_account(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Permanently delete user account, session tokens, and all associated database records."""
    user_id = current_user.id

    # Clean up trader instance in memory
    async with trader_manager._lock:
        if user_id in trader_manager.traders:
            del trader_manager.traders[user_id]

    # Delete all associated database records in SQLite
    db_file = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM refresh_tokens WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM password_reset_tokens WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM api_keys WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM positions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM trades WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM pnl_snapshots WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM wallet_ledger WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM paper_portfolios WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    except Exception as e:
        logger.error(f"[DELETE_USER_ACCOUNT] Database wipe error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account data.")
    finally:
        conn.close()

    return {"status": "success", "message": "Account and all associated trading data permanently deleted."}




@app.post("/api/trade/order")
async def execute_manual_order(req: OrderRequest, current_user: UserModel = Depends(get_current_user)):
    """Advanced Manual Order Execution (LONG/SHORT, Leverage, SL, TP, Trailing Stop)."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    price = market_engine.fetch_current_price(req.symbol)
    
    sl_price = req.stop_loss_price or (price * 0.975 if req.side.upper() == "LONG" else price * 1.025)
    tp_price = req.take_profit_price or (price * 1.05 if req.side.upper() == "LONG" else price * 0.95)

    res = user_trader.open_position(
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
    await user_trader.flush_persistence()
    return res

@app.post("/api/trade/position-action")
async def manage_position(req: PositionActionRequest, current_user: UserModel = Depends(get_current_user)):
    """Position Actions: Close, Partial Close, Reverse, Edit SL/TP."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    price = market_engine.fetch_current_price(req.symbol)
    action = req.action.upper()

    if action == "CLOSE":
        res = user_trader.close_position(req.symbol, price, reason="Manual Position Close")
    elif action == "PARTIAL_CLOSE":
        res = user_trader.close_position(req.symbol, price, reason="Partial Take Profit", ratio=req.ratio or 0.5)
    elif action == "REVERSE":
        res = user_trader.reverse_position(req.symbol, price)
    elif action == "EDIT_SL_TP":
        if req.symbol in user_trader.positions:
            pos = user_trader.positions[req.symbol]
            if req.new_stop_loss: pos['stop_loss_price'] = req.new_stop_loss
            if req.new_take_profit: pos['take_profit_price'] = req.new_take_profit
            res = {"status": "success", "message": f"Updated SL/TP targets for {req.symbol}"}
        else:
            res = {"status": "error", "message": "Position not found"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    await user_trader.flush_persistence()
    return res


@app.post("/api/bot/strategy")
async def update_bot_strategy(
    req: Optional[StrategyConfigRequest] = Body(None),
    strategy_name: Optional[str] = Query(None),
    risk_mode: Optional[str] = Query(None),
    current_user: UserModel = Depends(get_current_user)
):
    """Switch Active Bot Strategy and Risk Mode."""
    strat = (req.strategy_name if req and req.strategy_name else strategy_name) or "AI Hybrid"
    risk = (req.risk_mode if req and req.risk_mode else risk_mode) or "Moderate"

    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    user_trader.active_strategy = strat
    user_trader.risk_mode = risk
    user_trader._sync_save_portfolio()
    logger.info(f"Bot Strategy updated for user_id={current_user.id} to: {strat} ({risk})")
    return {
        "status": "success",
        "message": f"Strategy switched to {strat} ({risk})",
        "strategy_name": strat,
        "risk_mode": risk
    }


@app.post("/api/bot/parameters")
async def update_bot_parameters(
    req: Optional[ExecutionParametersRequest] = Body(None),
    default_allocation_usd: Optional[float] = Query(None),
    default_leverage: Optional[int] = Query(None),
    current_user: UserModel = Depends(get_current_user)
):
    """Update Default Execution Sizing and Leverage for AI Trading Engine."""
    alloc = (req.default_allocation_usd if req and req.default_allocation_usd is not None else default_allocation_usd) or 1000.0
    lev = (req.default_leverage if req and req.default_leverage is not None else default_leverage) or 1

    if alloc <= 0:
        raise HTTPException(status_code=400, detail="Default allocation must be greater than 0")
    if lev < 1 or lev > 25:
        raise HTTPException(status_code=400, detail="Default leverage must be between 1x and 25x")

    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    user_trader.default_allocation_usd = float(alloc)
    user_trader.default_leverage = int(lev)
    user_trader._sync_save_portfolio()
    
    logger.info(f"[EXECUTION_PARAMS] UserID={current_user.id} updated params: Allocation=${alloc:,.2f} USDT, Leverage={lev}x")
    return {
        "status": "success",
        "message": f"Execution parameters applied: ${alloc:,.2f} USDT allocation @ {lev}x leverage",
        "default_allocation_usd": alloc,
        "default_leverage": lev
    }


@app.post("/api/bot/toggle")
async def toggle_bot(enable: bool = Query(...), current_user: UserModel = Depends(get_current_user)):
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    user_trader.auto_bot_enabled = enable
    user_trader._sync_save_portfolio()
    status_str = "ACTIVE" if enable else "DISABLED"
    logger.info(f"Auto-Trading Bot state for user_id={current_user.id}: {status_str}")
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
            # Refresh news sentiment every 10 minutes
            if time.time() - last_sentiment_update > 600.0 or not sentiment_cache:
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
                logger.info(f"[LIVE_AI_SIGNALS] Symbol={symbol} | Action={signal['action']} | Direction={signal['direction']} | Confidence={signal['confidence_score']}% | Price=${price:.2f}")

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

            # Check SL / TP & Auto Bot Execution for all active user traders
            active_traders = list(trader_manager.traders.values())
            if not active_traders:
                active_traders = [trader]

            cycle_ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            logger.info(f"--- [LIVE_SCAN_CYCLE] Timestamp={cycle_ts} | ActiveEngines={len(active_traders)} | TopBuys={len(top_buys)} | TopSells={len(top_sells)} ---")

            for user_tr in active_traders:
                user_tr.check_stop_loss_take_profit(current_prices)

                logger.info(f"[LIVE_CYCLE_STATE] Timestamp={cycle_ts} | UserID={user_tr.user_id} | AutoBotEnabled={user_tr.auto_bot_enabled} | Balance=${user_tr.usdt_balance:.2f} | OpenPositions={len(user_tr.positions)} ({list(user_tr.positions.keys())})")

                # Check Condition 1: Auto Bot Enabled
                if not user_tr.auto_bot_enabled:
                    logger.info(f"[LIVE_BOT_DECISION] [SKIPPED] UserID={user_tr.user_id} | Reason: Auto-Trading Bot is DISABLED.")
                    continue

                # Check Condition 2: Minimum Balance Requirement
                if user_tr.usdt_balance < 100.0:
                    logger.info(f"[LIVE_BOT_DECISION] [SKIPPED] UserID={user_tr.user_id} | Balance=${user_tr.usdt_balance:.2f} | Reason: Balance below $100.0 minimum requirement.")
                    continue

                # Combine & rank candidate opportunities by confidence score (descending)
                candidates = sorted(top_buys + top_sells, key=lambda x: x['confidence_score'], reverse=True)
                seen_symbols = set()

                for idx, cand in enumerate(candidates, 1):
                    cand_sym = cand['symbol']
                    cand_conf = cand['confidence_score']
                    cand_dir = cand['direction']

                    if cand_sym in seen_symbols:
                        continue
                    seen_symbols.add(cand_sym)

                    # Check Condition 3: Confidence Score Threshold
                    if cand_conf < 65.0:
                        logger.info(f"[CANDIDATE #{idx}] Symbol={cand_sym} | Confidence={cand_conf}% | Decision=SKIPPED | Reason=Below 65.0% Threshold")
                        continue

                    # Check Condition 4: Existing Position Check
                    if cand_sym in user_tr.positions:
                        logger.info(f"[CANDIDATE #{idx}] Symbol={cand_sym} | Confidence={cand_conf}% | Decision=SKIPPED | Reason=Already Open")
                        continue

                    # Check Condition 5: Direction Validation
                    if cand_dir not in ["LONG", "SHORT"]:
                        logger.info(f"[CANDIDATE #{idx}] Symbol={cand_sym} | Confidence={cand_conf}% | Decision=SKIPPED | Reason=Invalid Direction")
                        continue

                    logger.info(f"[CANDIDATE #{idx}] Symbol={cand_sym} | Direction={cand_dir} | Confidence={cand_conf}% | Decision=PASSED")

                    alloc = getattr(user_tr, 'default_allocation_usd', 1000.0)
                    lev = getattr(user_tr, 'default_leverage', 1)
                    logger.info(f"[RISK_MANAGER] UserID={user_tr.user_id} | Symbol={cand_sym} | Side={cand_dir} | Alloc=${alloc:.2f} | Leverage={lev}x | Price=${current_prices[cand_sym]:.2f} | Decision=PASSED")

                    try:
                        res = user_tr.open_position(
                            symbol=cand_sym,
                            side=cand_dir,
                            price=current_prices[cand_sym],
                            allocation_usd=alloc,
                            stop_loss_price=cand['stop_loss_price'],
                            take_profit_price=cand['take_profit_price'],
                            leverage=lev,
                            reason=f"Auto-Bot 24/7 ({cand['strategy']}) Confidence: {cand_conf}%"
                        )

                        if res.get("status") == "success":
                            logger.info(f"[POSITION] UserID={user_tr.user_id} | Symbol={cand_sym} | OPENED SUCCESSFULLY: {res}")
                            break # Stop loop immediately after 1 successful trade execution per scan cycle
                        else:
                            logger.info(f"[POSITION] UserID={user_tr.user_id} | Symbol={cand_sym} | REJECTED BY RISK MANAGER: {res.get('message')}")
                            continue
                    except Exception as ex:
                        logger.error(f"[POSITION_EXCEPTION] UserID={user_tr.user_id} | Symbol={cand_sym} raised Exception: {ex}", exc_info=True)
                        continue




            # Broadcast Real-Time Data over WebSockets
            ws_payload = {
                "type": "TICKER_UPDATE",
                "timestamp": time.time(),
                "prices": current_prices,
                "scanner": scanner_cache
            }

            loop.run_until_complete(ws_manager.broadcast(ws_payload))

        except Exception as e:
            logger.error(f"Error in multi-symbol scanner loop: {e}")

        time.sleep(5.0)  # Optimized 5-second interval for RAM & API stability


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

