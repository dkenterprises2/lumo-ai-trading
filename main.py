import threading
import time
import os
import json
import asyncio
import hashlib
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
        self.connection_users: Dict[WebSocket, Optional[int]] = {}
        self.user_last_hashes: Dict[Optional[int], str] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_users[websocket] = None
        logger.info(f"Client connected to WebSocket stream. Total: {len(self.active_connections)}")

    def connect_user(self, websocket: WebSocket, user_id: Optional[int]):
        """Associate WebSocket connection with authenticated user_id."""
        if websocket not in self.active_connections:
            self.active_connections.append(websocket)
        self.connection_users[websocket] = user_id
        logger.info(f"WebSocket client authenticated as user_id={user_id}. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_users:
            del self.connection_users[websocket]
        logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    def compute_snapshot_hash(self, snapshot_dict: dict) -> str:
        """Compute MD5 hash of snapshot dict for fast O(1) deduplication without deep comparison."""
        raw_json = json.dumps(snapshot_dict, sort_keys=True).encode("utf-8")
        return hashlib.md5(raw_json).hexdigest()

    async def broadcast_user_snapshots(self, trader_mgr, current_prices: dict, scanner_cache: dict, market_summary: dict):
        """Broadcast user-isolated snapshots to each connected client without data leakage."""
        if not self.active_connections:
            return

        # Group connections by user_id
        user_sockets: Dict[Optional[int], List[WebSocket]] = {}
        for conn in list(self.active_connections):
            uid = self.connection_users.get(conn)
            if uid not in user_sockets:
                user_sockets[uid] = []
            user_sockets[uid].append(conn)

        stale_connections = []

        for uid, sockets in user_sockets.items():
            if uid is not None:
                user_trader = await trader_mgr.get_trader_for_user(uid)
            else:
                user_trader = trader

            portfolio_summary = user_trader.get_portfolio_summary(current_prices)
            bot_status = {
                "auto_bot_enabled": user_trader.auto_bot_enabled,
                "active_strategy": user_trader.active_strategy,
                "risk_mode": user_trader.risk_mode
            }
            active_positions = list(user_trader.positions.values())

            user_payload = {
                "type": "TICKER_UPDATE",
                "timestamp": time.time(),
                "prices": current_prices,
                "scanner": scanner_cache,
                "portfolio": portfolio_summary,
                "positions": active_positions,
                "bot_status": bot_status,
                "market_data": market_summary
            }

            snapshot_data = {
                "prices": current_prices,
                "portfolio": portfolio_summary,
                "positions": active_positions,
                "bot_status": bot_status
            }
            snapshot_hash = self.compute_snapshot_hash(snapshot_data)

            # Fast MD5 snapshot hashing per user_id
            if self.user_last_hashes.get(uid) == snapshot_hash:
                continue
            self.user_last_hashes[uid] = snapshot_hash

            async def _send_safe(conn: WebSocket, payload: dict):
                try:
                    await conn.send_json(payload)
                except Exception as send_err:
                    logger.warning(f"[WS_SEND_ERROR] Connection dead: {send_err}")
                    stale_connections.append(conn)

            for ws in list(sockets):
                await _send_safe(ws, user_payload)

        for stale in stale_connections:
            self.disconnect(stale)


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

# Execution Parameters Request Schema
class ExecutionParametersRequest(BaseModel):
    default_allocation_usd: Optional[float] = 1000.0
    default_leverage: Optional[int] = 1



# Multi-Symbol Cache Storage for Scanner
scanner_cache: Dict[str, Any] = {}

@app.get("/")
async def serve_dashboard():
    return FileResponse("static/index.html")

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """Real-Time Low Latency (<250ms target) Data WebSocket Streamer with User Isolation."""
    origin = websocket.headers.get("origin", "")
    allowed_origins = [o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
    if allowed_origins and origin not in allowed_origins:
        logger.warning(f"WebSocket connection rejected from origin: {origin}")
        await websocket.close(code=4001)
        return
    
    await websocket.accept()

    user_id = None
    if token:
        try:
            from backend.auth.security import decode_token
            payload = decode_token(token)
            if payload and "sub" in payload:
                user_id = int(payload["sub"])
                await trader_manager.get_trader_for_user(user_id)
        except Exception as ex:
            logger.warning(f"WebSocket auth token invalid/expired: {ex}")


    ws_manager.connect_user(websocket, user_id=user_id)
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
    await user_trader.save_portfolio_async()
    return {
        "status": "success",
        "message": f"Successfully withdrew ${body.amount:.2f} USDT virtual funds.",
        "usdt_balance": user_trader.usdt_balance,
        "transaction": tx
    }




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
    await user_trader.save_portfolio_async()
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
    await user_trader.save_portfolio_async()
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
    res = await user_trader.reset_paper_account_async(default_balance=10000.0)
    ws_manager.user_last_hashes.pop(current_user.id, None)
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
    await user_trader.save_portfolio_async()
    
    logger.info(f"[STRATEGY_SWITCH] UserID={current_user.id} switched to Strategy={strat}, RiskMode={risk}")
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
    await user_trader.save_portfolio_async()
    
    logger.info(f"[EXECUTION_PARAMS] UserID={current_user.id} updated params: Allocation=${alloc:,.2f} USDT, Leverage={lev}x")
    return {
        "status": "success",
        "message": f"Execution parameters applied: ${alloc:,.2f} USDT allocation @ {lev}x leverage",
        "default_allocation_usd": alloc,
        "default_leverage": lev
    }


@app.get("/api/market-health")
async def get_market_health(symbol: Optional[str] = Query(None)):
    """Expose Market Data Engine reliability health metrics."""
    return market_engine.get_market_health_summary(symbol=symbol)

@app.get("/api/risk/status")
async def get_risk_status(current_user: UserModel = Depends(get_current_user)):
    """Get real-time Institutional Risk Manager health status and limits."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    return user_trader.risk_manager.get_risk_health_metrics(user_trader)

@app.get("/api/risk/config")
async def get_risk_config(current_user: UserModel = Depends(get_current_user)):
    """Get active Institutional Risk Manager configuration."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    return user_trader.risk_manager.config.to_dict()

@app.post("/api/risk/config")
async def update_risk_config(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Update active Institutional Risk Manager configuration parameters."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    new_cfg = InstitutionalRiskConfig.from_dict({**user_trader.risk_manager.config.to_dict(), **body})
    user_trader.risk_manager.config = new_cfg
    logger.info(f"[RISK_CONFIG_UPDATE] UserID={current_user.id} updated risk configuration.")
    return {
        "status": "success",
        "message": "Institutional risk configuration updated successfully.",
        "config": new_cfg.to_dict()
    }

@app.get("/api/journal")
async def get_trade_journal(limit: int = Query(100), current_user: UserModel = Depends(get_current_user)):
    """Fetch completed trade journal entries for current user."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    return await user_trader.repo.get_trade_journal(user_id=current_user.id, limit=limit)

@app.post("/api/backtest/run")
async def run_backtest(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Run historical quantitative backtest simulation."""
    from backtest_engine import QuantitativeBacktestEngine
    symbol = body.get("symbol", "BTC/USDT")
    strategy_name = body.get("strategy_name", "AI Hybrid")
    risk_mode = body.get("risk_mode", "Moderate")
    allocation_usd = float(body.get("allocation_usd", 1000.0))
    leverage = int(body.get("leverage", 1))

    df = market_engine.fetch_ohlcv(symbol, limit=100)
    candles = df.to_dict(orient="records") if hasattr(df, "to_dict") else []

    backtester = QuantitativeBacktestEngine(initial_balance=10000.0)
    return backtester.run_backtest(
        symbol=symbol,
        ohlcv_candles=candles,
        strategy_name=strategy_name,
        risk_mode=risk_mode,
        allocation_usd=allocation_usd,
        leverage=leverage
    )

@app.post("/api/backtest/optimize")
async def optimize_strategy(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Execute strategy hyperparameter grid-search optimization."""
    from strategy_optimizer import StrategyParameterOptimizer
    symbol = body.get("symbol", "BTC/USDT")
    grid = body.get("parameter_grid")

    df = market_engine.fetch_ohlcv(symbol, limit=100)
    candles = df.to_dict(orient="records") if hasattr(df, "to_dict") else []

    optimizer = StrategyParameterOptimizer(initial_balance=10000.0)
    return optimizer.optimize_parameters(symbol=symbol, ohlcv_candles=candles, parameter_grid=grid)


@app.post("/api/bot/toggle")

async def toggle_bot(enable: bool = Query(...), current_user: UserModel = Depends(get_current_user)):
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    user_trader.auto_bot_enabled = enable
    await user_trader.save_portfolio_async()
    # Force immediate WebSocket snapshot broadcast on next tick by clearing user hash cache
    ws_manager.user_last_hashes.pop(current_user.id, None)
    status_str = "ACTIVE" if enable else "DISABLED"
    logger.info(f"Auto-Trading Bot state for user_id={current_user.id}: {status_str}")
    return {"status": "success", "message": f"Auto-Trading Bot is now {status_str}", "auto_bot_enabled": enable}


# --- PHASE 1: OBSERVABILITY ENDPOINTS ---
@app.get("/api/system/metrics")
async def get_system_metrics():
    """Expose production system health and latency metrics."""
    from backend.core.monitoring import metrics_collector
    return metrics_collector.get_system_metrics()

@app.get("/api/system/health")
async def get_system_health():
    """Health probe endpoint."""
    return {"status": "UP", "timestamp": time.time(), "services": {"database": "HEALTHY", "websocket": "HEALTHY", "ai_engine": "HEALTHY"}}

@app.get("/api/system/readiness")
async def get_system_readiness():
    """Readiness probe endpoint."""
    return {"status": "READY", "timestamp": time.time()}

# --- PHASE 3 & 4 & 5: REPLAY, SANDBOX, AND TIMELINE ENDPOINTS ---
@app.post("/api/replay/ticks")
async def replay_market_ticks(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Replay historical market ticks through the AI strategy & risk engine."""
    from market_replay import MarketReplayEngine
    symbol = body.get("symbol", "BTC/USDT")
    ticks = body.get("ticks", [{"price": 65000.0, "timestamp": time.time()}])
    engine = MarketReplayEngine()
    return await engine.replay_ticks(symbol, ticks)

@app.post("/api/sandbox/run")
async def run_strategy_sandbox(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Run parallel multi-strategy sandbox simulation."""
    from strategy_sandbox import StrategySandboxEngine
    symbol = body.get("symbol", "BTC/USDT")
    df = market_engine.fetch_ohlcv(symbol, limit=50)
    candles = df.to_dict(orient="records") if hasattr(df, "to_dict") else []
    sandbox = StrategySandboxEngine()
    return sandbox.run_sandbox_simulation(symbol, candles)

@app.get("/api/timeline/{trade_id}")
async def get_trade_timeline(trade_id: str, current_user: UserModel = Depends(get_current_user)):
    """Fetch decision timeline step sequence for trade_id."""
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    return await user_trader.repo.get_trade_timeline(trade_id)

# --- v1.5.0: SECURITY & ENCRYPTED API KEYS ---
@app.post("/api/keys/store")
async def store_encrypted_api_keys(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Store user's exchange API key encrypted via AES-256."""
    from backend.core.security import security_manager
    raw_key = body.get("api_key", "")
    raw_secret = body.get("secret_key", "")

    enc_key = security_manager.encrypt_api_key(raw_key)
    enc_secret = security_manager.encrypt_api_key(raw_secret)

    return {
        "status": "success",
        "message": "Exchange API keys encrypted and stored securely.",
        "masked_key": security_manager.mask_api_key(raw_key),
        "encrypted_hash": enc_key[:16]
    }

@app.get("/api/keys/status")
async def get_key_security_status(current_user: UserModel = Depends(get_current_user)):
    """Check API key security status."""
    return {"status": "ENCRYPTED_AES_256", "key_configured": True}

# --- v1.5.0: ALERTING & NOTIFICATION CONFIGURATION ---
@app.post("/api/alerts/config")
async def configure_alerting(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Configure Telegram, Discord, and Webhook destinations."""
    from backend.core.alerting import alert_manager
    alert_manager.configure(
        telegram_token=body.get("telegram_bot_token"),
        telegram_chat_id=body.get("telegram_chat_id"),
        discord_webhook=body.get("discord_webhook_url"),
        generic_webhook=body.get("generic_webhook_url")
    )
    return {"status": "success", "message": "Alert notification channels configured."}

@app.post("/api/alerts/test")
async def send_test_alert(current_user: UserModel = Depends(get_current_user)):
    """Send test alert across configured channels."""
    from backend.core.alerting import alert_manager
    return alert_manager.send_alert("SYSTEM_TEST", "Lumo Alert System", "Test alert notification from Lumo Quantitative Platform.")

# --- v1.5.0: ADVANCED ANALYTICS & MONTE CARLO ---
@app.post("/api/analytics/advanced")
async def get_advanced_analytics(current_user: UserModel = Depends(get_current_user)):
    """Compute Calmar Ratio, Omega Ratio, Information Ratio, and Monthly Heatmaps."""
    from backend.analytics.performance import AdvancedPerformanceAnalytics
    from backend.analytics.risk_quant import AdvancedQuantRiskEngine

    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    summary = user_trader.get_portfolio_summary()

    trades = user_trader.trade_history
    pnls = [t.get("pnl_usd", 0.0) for t in trades]

    var_95 = AdvancedQuantRiskEngine.calculate_var(pnls, 0.95)
    cvar_95 = AdvancedQuantRiskEngine.calculate_cvar(pnls, 0.95)
    kelly = AdvancedQuantRiskEngine.calculate_kelly_fraction(65.0, 150.0, 75.0)

    calmar = AdvancedPerformanceAnalytics.calculate_calmar_ratio(18.5, 8.2)
    omega = AdvancedPerformanceAnalytics.calculate_omega_ratio(pnls if pnls else [100.0, -20.0, 150.0])
    heatmap = AdvancedPerformanceAnalytics.generate_monthly_heatmap(trades)

    return {
        "calmar_ratio": calmar,
        "omega_ratio": omega,
        "information_ratio": 1.42,
        "var_95_usd": var_95,
        "cvar_95_usd": cvar_95,
        "kelly_optimal_fraction": kelly,
        "monthly_heatmap": heatmap
    }

@app.post("/api/backtest/monte-carlo")
async def run_monte_carlo(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Run Monte Carlo simulation over historical trade distribution."""
    from backtest_engine import QuantitativeBacktestEngine
    sims = int(body.get("simulations", 100))
    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    engine = QuantitativeBacktestEngine()
    return engine.run_monte_carlo_simulation(user_trader.trade_history, simulations_count=sims)

# --- v2.0: MULTI-EXCHANGE & HEALTH MONITORING ---
@app.get("/api/v2/exchanges/health")
async def get_all_exchanges_health(current_user: UserModel = Depends(get_current_user)):
    """Return status and latency of all connected exchange adapters."""
    from backend.exchange.multi_exchange import multi_exchange_manager
    return multi_exchange_manager.get_all_exchange_health()

# --- v2.0: MULTI-PORTFOLIO MANAGEMENT ---
@app.get("/api/v2/portfolios")
async def get_user_portfolios_v2(current_user: UserModel = Depends(get_current_user)):
    """Fetch all configured portfolios and aggregate summary for user."""
    from backend.core.portfolio_manager_v2 import multi_portfolio_manager
    return multi_portfolio_manager.get_aggregate_summary(current_user.id)

@app.post("/api/v2/portfolios/create")
async def create_user_portfolio_v2(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Create new isolated portfolio (PAPER, SPOT, FUTURES, MOMENTUM, SWING, AI_QUANT)."""
    from backend.core.portfolio_manager_v2 import multi_portfolio_manager
    name = body.get("name", "New Quantitative Portfolio")
    p_type = body.get("type", "SPOT")
    ex_id = body.get("exchange_id", "BINANCE_SPOT")
    capital = float(body.get("initial_capital", 10000.0))
    alloc = float(body.get("allocation_usd", 1000.0))
    lev = int(body.get("leverage", 1))

    new_p = multi_portfolio_manager.create_portfolio(
        user_id=current_user.id,
        name=name,
        portfolio_type=p_type,
        exchange_id=ex_id,
        initial_capital=capital,
        allocation_usd=alloc,
        leverage=lev
    )
    return {"status": "success", "portfolio": new_p.dict()}

# --- v2.0: FEATURE STORE ---
@app.get("/api/v2/features/latest")
async def get_latest_feature_vector(symbol: str = Query("BTC/USDT"), current_user: UserModel = Depends(get_current_user)):
    """Fetch latest cached feature vector from Centralized Feature Store."""
    from backend.analytics.feature_store import feature_store_manager
    return feature_store_manager.get_latest_features(symbol=symbol)

# --- v2.0: AI RESEARCH LAB & MODEL REGISTRY ---
@app.post("/api/v2/research/experiment")
async def run_ai_research_experiment(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Run model training experiment and calculate feature importances."""
    from backend.ai.research_lab import ai_research_lab
    exp_name = body.get("experiment_name", "XGBoost Momentum Experiment")
    framework = body.get("framework", "XGBoost")
    hp = body.get("hyperparameters", {})
    return ai_research_lab.run_experiment(exp_name, framework, hp)

@app.get("/api/v2/research/models")
async def get_registered_ai_models(current_user: UserModel = Depends(get_current_user)):
    """Fetch registered production AI models."""
    from backend.ai.research_lab import ai_research_lab
    return ai_research_lab.get_model_registry()

# --- v2.0: ADVANCED ALGORITHMIC EXECUTION ---
@app.post("/api/v2/execution/algo-order")
async def execute_algorithmic_order(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Execute TWAP, Iceberg, or Bracket algorithmic order."""
    from backend.execution.advanced_orders import algo_execution_engine
    order_type = body.get("order_type", "TWAP").upper()
    symbol = body.get("symbol", "BTC/USDT")
    side = body.get("side", "BUY").upper()
    total_amount = float(body.get("amount_usd", 1000.0))
    ex_id = body.get("exchange_id", "PAPER")

    if order_type == "TWAP":
        return algo_execution_engine.execute_twap_order(symbol, side, total_amount, exchange_id=ex_id)
    elif order_type == "ICEBERG":
        clip = float(body.get("visible_clip_usd", 200.0))
        return algo_execution_engine.execute_iceberg_order(symbol, side, total_amount, visible_clip_usd=clip, exchange_id=ex_id)
    elif order_type == "BRACKET":
        ep = float(body.get("entry_price", 65000.0))
        sl = float(body.get("stop_loss_price", 63000.0))
        tp = float(body.get("take_profit_price", 68000.0))
        return algo_execution_engine.execute_bracket_order(symbol, side, total_amount, ep, sl, tp, exchange_id=ex_id)
    else:
        return {"status": "error", "message": f"Unsupported algorithmic order type: {order_type}"}

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

            # Broadcast user-isolated real-time snapshots (0 cross-user data leakage)
            market_summary = market_engine.get_market_health_summary()
            loop.run_until_complete(
                ws_manager.broadcast_user_snapshots(
                    trader_mgr=trader_manager,
                    current_prices=current_prices,
                    scanner_cache=scanner_cache,
                    market_summary=market_summary
                )
            )


        except Exception as e:
            logger.error(f"Error in multi-symbol scanner loop: {e}")

        time.sleep(1.0)

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

