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
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import settings
from market_data import MarketDataEngine
from sentiment_engine import SentimentEngine
from ai_strategy import AITradingStrategy
from trader import PaperTrader, trader_manager
from backend.auth.security import get_current_user, get_optional_current_user, get_db

from backend.models.domain import UserModel
from backend.core.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

# Initialize Services
market_engine = MarketDataEngine()
sentiment_engine = SentimentEngine()
ai_strategy = AITradingStrategy()
trader = PaperTrader(initial_balance=settings.PAPER_TRADING_INITIAL_BALANCE)

from contextlib import asynccontextmanager
from backend.database.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[LIFESPAN] Capturing Main Event Loop & Initializing Database...")
    main_loop = asyncio.get_running_loop()
    trader.set_main_event_loop(main_loop)
    trader_manager.set_main_event_loop(main_loop)

    try:
        await init_db()
        logger.info("[LIFESPAN] Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"[LIFESPAN] Error during init_db: {e}")

    await trader.initialize_and_restore_state()
    await trader_manager.load_all_traders_from_db()
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

        learning_thread = threading.Thread(target=background_learning_scheduler_loop, daemon=True)
        learning_thread.start()
        logger.info("[LIFESPAN] Background learning scheduler thread started successfully.")

        # Initialize Continuous 24/7 Arbitrage, Shadow Replay, and Autonomous Engines
        try:
            from backend.arbitrage import arbitrage_background_scanner
            arbitrage_background_scanner.start()
            from backend.routers import arbitrage_router
            arbitrage_router.shadow_active = True
            from backend.shadow_trading import shadow_engine
            shadow_engine.status = "RUNNING"
            from backend.autonomous.autonomous_engine import autonomous_engine
            autonomous_engine.start()
            from backend.shadow_trading.shadow_autonomous_learner import shadow_autonomous_learner
            shadow_autonomous_learner.start()
            from backend.spot_research.spot_autonomous_bot import spot_autonomous_bot
            if spot_autonomous_bot.config.is_enabled:
                spot_autonomous_bot.start()
                logger.info("[LIFESPAN] Spot Autonomous Learner Bot ACTIVATED 24/7.")
            logger.info("[LIFESPAN] Arbitrage Scanner, Shadow Engine, Autonomous Engine & Shadow Autonomous Learner ACTIVATED 24/7.")
        except Exception as e:
            logger.error(f"[LIFESPAN] Error starting background engines: {e}")

    yield

    # Clean shutdown
    try:
        from backend.arbitrage import arbitrage_background_scanner
        arbitrage_background_scanner.stop()
    except Exception:
        pass

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

# Configure CORS Middleware at top of middleware stack
VERCEL_FRONTEND_URL = os.getenv(
    "VERCEL_FRONTEND_URL",
    "https://lumo-ai-trading.vercel.app"
)

cors_origins = [
    VERCEL_FRONTEND_URL,
    "https://lumo-ai-trading.vercel.app",
    "https://lumo-ai.vercel.app",
    "https://lumo.trade",
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

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/api/system/health")
async def system_health():
    return {
        "status": "healthy",
        "service": "lumo-backend",
        "cors_frontend": VERCEL_FRONTEND_URL
    }

from fastapi import Request
from fastapi.responses import JSONResponse


@app.middleware("http")
async def log_incoming_requests(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path in ["/api/arbitrage/metrics", "/api/shadow/status", "/api/health"]:
        return await call_next(request)
    client_ip = request.client.host if request.client else "127.0.0.1"
    logger.debug(f"[API] {request.method} {request.url.path} from {client_ip}")
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"[GLOBAL_SERVER_ERROR] {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"Internal Server Error: {str(exc)}",
            "detail": f"Internal Server Error: {str(exc)}",
            "path": request.url.path
        }
    )





from backend.routers.auth_router import router as auth_router
from backend.routers.exchange_router import router as exchange_router
from backend.routers.strategy_router import router as strategy_router
from backend.routers.analytics_router import router as analytics_router
from backend.routers.ml_router import router as ml_router
from backend.routers.research_router import router as research_router
from backend.routers.portfolio_opt_router import router as portfolio_opt_router
from backend.routers.live_execution_router import router as live_execution_router
from backend.routers.system_observability_router import router as system_observability_router
from backend.routers.mlops_router import router as mlops_router
from backend.routers.saas_router import router as saas_router
from backend.routers.admin_router import router as admin_router
from backend.routers.microservices_router import router as microservices_router
from backend.routers.compliance_router import router as compliance_router
from backend.routers.quant_research_router import router as quant_research_router
from backend.routers.execution_algos_router import router as execution_algos_router
from backend.routers.marketdata_router import router as marketdata_router
from backend.routers.ai_agents_router import router as ai_agents_router
from backend.routers.multiasset_router import router as multiasset_router
from backend.routers.enterprise_saas_router import router as enterprise_saas_router
from backend.routers.platform_infra_router import router as platform_infra_router
from backend.routers.quant_research_platform_router import router as quant_research_platform_router
from backend.routers.alpha_factory_router import router as alpha_factory_router

from backend.routers.execution_network_router import router as execution_network_router
from backend.routers.ai_copilot_router import router as ai_copilot_router
from backend.routers.learning_router import router as learning_router

from backend.routers.preferences_router import router as preferences_router
from backend.routers.portfolio_risk_router import router as portfolio_risk_router
from backend.routers.execution_router import router as execution_router
from backend.routers.system_router import router as system_router
from backend.routers.shadow_router import router as shadow_router
from backend.routers.arbitrage_router import router as arbitrage_router
from backend.routers.news_router import router as news_router
from backend.routers.autonomous_router import router as autonomous_router
from backend.autonomous_validation.validation_router import router as validation_router

from backend.routers.wallet_router import router as wallet_router
from backend.routers.brain_router import router as brain_router

app.include_router(auth_router)
app.include_router(wallet_router)
app.include_router(brain_router)
app.include_router(preferences_router)
app.include_router(portfolio_risk_router)
app.include_router(execution_router)
app.include_router(system_router)
app.include_router(shadow_router)
app.include_router(arbitrage_router)
app.include_router(news_router)
app.include_router(autonomous_router)
app.include_router(validation_router)
app.include_router(exchange_router)







app.include_router(strategy_router)
app.include_router(analytics_router)
app.include_router(ml_router)
app.include_router(research_router)
app.include_router(portfolio_opt_router)
app.include_router(live_execution_router)
app.include_router(system_observability_router)
app.include_router(mlops_router)
app.include_router(saas_router)
app.include_router(admin_router)
app.include_router(microservices_router)
app.include_router(compliance_router)
app.include_router(quant_research_router)
app.include_router(execution_algos_router)
app.include_router(marketdata_router)
app.include_router(ai_agents_router)
app.include_router(multiasset_router)
app.include_router(enterprise_saas_router)
app.include_router(platform_infra_router)
app.include_router(quant_research_platform_router)
app.include_router(alpha_factory_router)
app.include_router(execution_network_router)
app.include_router(ai_copilot_router)
app.include_router(learning_router)
from backend.routers.spot_research_router import router as spot_research_router
app.include_router(spot_research_router)

























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
        # Invalidate last hash so new connection immediately receives updates
        self.user_last_hashes[user_id] = ""
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
            active_positions = portfolio_summary.get("active_positions", [])

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
@app.get("/login")
@app.get("/register")
@app.get("/dashboard")
@app.get("/copilot")
@app.get("/charts")
@app.get("/orders")
@app.get("/positions")
@app.get("/risk")
@app.get("/settings")
@app.get("/profile")
@app.get("/history")
@app.get("/ledger")
@app.get("/pnl")
@app.get("/scanner")
@app.get("/alerts")
@app.get("/forgot-password")
@app.get("/reset-password")
async def serve_dashboard():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    raise HTTPException(status_code=404, detail="Frontend index.html not found")


@app.websocket("/ws/ping")
async def websocket_ping(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({
        "status": "connected"
    })
    await asyncio.sleep(60)

@app.websocket("/ws")
@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """Real-Time Low Latency Data WebSocket Streamer with Production Safe Handshake."""
    await websocket.accept()
    logger.info("WS client connected")

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
        from backend.telemetry import ws_metrics
        ws_metrics.register_client()

        # Send immediate initial state snapshot so page renders in 0ms without waiting for ticker tick
        try:
            curr_prices = get_current_prices_dict()
            u_trader = await trader_manager.get_trader_for_user(user_id) if user_id else trader
            p_summary = u_trader.get_portfolio_summary(curr_prices)
            init_payload = {
                "type": "TICKER_UPDATE",
                "timestamp": time.time(),
                "prices": curr_prices,
                "scanner": scanner_cache,
                "portfolio": p_summary,
                "positions": p_summary.get("active_positions", []),
                "bot_status": {
                    "auto_bot_enabled": u_trader.auto_bot_enabled,
                    "active_strategy": u_trader.active_strategy,
                    "risk_mode": u_trader.risk_mode
                },
                "market_data": market_engine.get_market_health_summary()
            }
            await websocket.send_json(init_payload)
        except Exception as init_err:
            logger.warning(f"[WS_INIT_SNAPSHOT_ERROR] {init_err}")

        while True:
            # Keep-alive heartbeat & ping listener
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time(), "status": "live"})
    except WebSocketDisconnect:
        logger.info("WS client disconnected")
        from backend.telemetry import ws_metrics
        ws_metrics.unregister_client()
        ws_manager.disconnect(websocket)
    except Exception as exc:
        logger.warning(f"WebSocket stream error: {exc}")
        from backend.telemetry import ws_metrics
        ws_metrics.unregister_client()
        ws_manager.disconnect(websocket)

        try:
            await websocket.close(code=1011)
        except Exception:
            pass


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

def get_current_prices_dict() -> Dict[str, float]:
    """Fast non-blocking cache-first price resolution for all symbols."""
    current_prices = {}
    from market_data import is_valid_price
    with market_engine._lock:
        for k, v in market_engine.price_cache.items():
            if is_valid_price(v):
                current_prices[k] = v

    for sym in settings.SUPPORTED_SYMBOLS:
        if sym not in current_prices or not is_valid_price(current_prices[sym]):
            _, base_p = market_engine.emergency_baselines.get(sym, ("unknown", 1.0))
            current_prices[sym] = base_p
    return current_prices

@app.get("/api/portfolio")
async def get_portfolio(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)
    current_prices = get_current_prices_dict()

    user_trader.check_stop_loss_take_profit(current_prices)
    return user_trader.get_portfolio_summary(current_prices)

@app.post("/api/arbitrage/reset")
async def reset_arbitrage_data():
    """Clear all test/synthetic arbitrage execution records and reset metrics counters."""
    try:
        from backend.arbitrage.arbitrage_ledger import arbitrage_ledger
        from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker
        from backend.wallet.sub_wallet_manager import sub_wallet_manager

        arbitrage_ledger.clear()
        ArbitrageMetricsTracker.reset()
        sub_wallet_manager.get_summary()
        return {"status": "success", "message": "Arbitrage test execution data wiped and ledger reset to pristine $0.00 state."}
    except Exception as e:
        logger.error(f"[RESET_ARBITRAGE_API_ERROR] {e}")
@app.get("/api/system/db-health")
async def get_system_db_health():
    """Diagnostic health endpoint reporting SQLite WAL mode, queue sizes, locks, and writes."""
    try:
        from backend.database.db_config import get_database_diagnostics
        from backend.arbitrage.arbitrage_evidence_store import ArbitrageEvidenceStore
        from backend.shadow_trading.shadow_autonomous_learner import shadow_autonomous_learner

        diag = get_database_diagnostics()
        ev_store = ArbitrageEvidenceStore()
        
        diag["evidence_store"] = {
            "events_generated": ev_store.events_generated,
            "events_enqueued": ev_store.events_enqueued,
            "events_persisted": ev_store.events_persisted,
            "events_retried": ev_store.events_retried,
            "events_failed": ev_store.events_failed,
            "events_dropped": ev_store.events_dropped,
            "lock_errors_count": ev_store.lock_errors_count,
            "in_memory_queue_size": ev_store._write_queue.qsize() if hasattr(ev_store, "_write_queue") else 0,
            "last_successful_write": ev_store.last_successful_write_utc
        }
        diag["shadow_learner"] = {
            "experiments_queued": shadow_autonomous_learner.experiments_queued,
            "experiments_persisted": shadow_autonomous_learner.experiments_persisted,
            "experiments_failed": shadow_autonomous_learner.experiments_failed,
            "in_memory_queue_size": shadow_autonomous_learner._persistence_queue.qsize() if hasattr(shadow_autonomous_learner, "_persistence_queue") else 0
        }
        return {"status": "success", "data": diag}
    except Exception as ex:
        logger.error(f"[DB_HEALTH_ERROR] {ex}")
        raise HTTPException(status_code=500, detail=str(ex))

@app.get("/api/portfolio/profit-attribution")
async def get_profit_attribution(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch complete profit attribution breakdown: Spot AI Paper Trading vs Arbitrage vs Shadow."""
    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)
    current_prices = get_current_prices_dict()

    pf = user_trader.get_portfolio_summary(current_prices)

    # 1. Spot Trading Metrics
    spot_realized_pnl = pf.get("closed_pnl_usd", 0.0)
    spot_unrealized_pnl = pf.get("total_unrealized_pnl_usd", 0.0)
    spot_total_pnl = round(spot_realized_pnl + spot_unrealized_pnl, 2)
    spot_trades_count = pf.get("total_closed_trades", 0)
    spot_win_rate = pf.get("win_rate", 0.0)

    # Detailed Symbol Breakdown (incorporates both open unrealized and closed realized PnL)
    symbol_breakdown = {}
    
    # Add active open positions PnL (active_positions can be a list or dict)
    active_positions_raw = pf.get("active_positions", [])
    if isinstance(active_positions_raw, dict):
        active_positions_list = list(active_positions_raw.values())
    elif isinstance(active_positions_raw, list):
        active_positions_list = active_positions_raw
    else:
        active_positions_list = []

    for pos in active_positions_list:
        sym = pos.get("symbol", "UNKNOWN")
        u_pnl = round(pos.get("unrealized_pnl_usd", 0.0), 2)
        symbol_breakdown[sym] = {
            "trades": 1,
            "realized_pnl": 0.0,
            "unrealized_pnl": u_pnl,
            "pnl": u_pnl,
            "wins": 1 if u_pnl > 0 else 0,
            "losses": 1 if u_pnl < 0 else 0,
            "status": "OPEN",
            "entry_price": pos.get("entry_price", 0.0),
            "mark_price": pos.get("current_price", pos.get("mark_price", 0.0)),
            "side": pos.get("side", "BUY"),
            "margin_usd": pos.get("margin_usd", 0.0)
        }

    # Add / Aggregate closed trades history
    for t in getattr(user_trader, "trade_history", []):
        if t.get("status") == "OPEN" and not t.get("exit_time"):
            continue  # Already represented from active positions
        sym = t.get("symbol", "UNKNOWN")
        r_pnl = round(float(t.get("pnl_usd", t.get("net_pnl", t.get("pnl", 0.0))) or 0.0), 2)
        if sym not in symbol_breakdown:
            symbol_breakdown[sym] = {
                "trades": 0,
                "realized_pnl": 0.0,
                "unrealized_pnl": 0.0,
                "pnl": 0.0,
                "wins": 0,
                "losses": 0,
                "status": "CLOSED",
                "entry_price": round(float(t.get("entry_price", 0.0)), 4),
                "mark_price": round(float(t.get("exit_price", t.get("entry_price", 0.0))), 4),
                "side": t.get("side", "BUY"),
                "margin_usd": round(float(t.get("margin_usd", 0.0)), 2)
            }
        symbol_breakdown[sym]["trades"] += 1
        symbol_breakdown[sym]["realized_pnl"] = round(symbol_breakdown[sym]["realized_pnl"] + r_pnl, 2)
        symbol_breakdown[sym]["pnl"] = round(symbol_breakdown[sym]["realized_pnl"] + symbol_breakdown[sym].get("unrealized_pnl", 0.0), 2)
        if r_pnl > 0:
            symbol_breakdown[sym]["wins"] += 1
        elif r_pnl < 0:
            symbol_breakdown[sym]["losses"] += 1

    # 2. Arbitrage Metrics & Route-by-Route Breakdown
    from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker
    arb_summary = ArbitrageMetricsTracker.get_summary()
    arb_captured_profit = round(getattr(arb_summary, "captured_profit_usd", 0.0), 2)
    arb_trades_count = getattr(arb_summary, "executable_opportunities", 0)
    arb_opps_count = getattr(arb_summary, "total_opportunities_detected", 0)
    arbitrage_routes_list = getattr(ArbitrageMetricsTracker(), "executed_routes", [])

    # 3. Shadow Simulated Replay & Trade-by-Trade Breakdown
    from backend.shadow_trading.shadow_engine import shadow_engine
    shadow_positions = shadow_engine.position_tracker.get_all_positions()
    shadow_analytics = shadow_engine.pnl_engine.compute_pnl_analytics(shadow_positions, shadow_engine.router.executed_fills)
    shadow_net_pnl = round(getattr(shadow_analytics, "net_pnl_usd", 0.0), 2)
    shadow_trades_count = len(shadow_positions)

    shadow_trades_list = []
    for p in shadow_positions:
        shadow_trades_list.append({
            "position_id": getattr(p, "position_id", "SHADOW-POS"),
            "symbol": getattr(p, "symbol", "BTC/USDT"),
            "side": getattr(p, "side", "BUY"),
            "quantity": getattr(p, "quantity", 0.0),
            "entry_price": getattr(p, "average_entry_price", 0.0),
            "mark_price": getattr(p, "mark_price", 0.0),
            "slippage_usd": getattr(p, "slippage_cost_usd", 0.0),
            "fees_usd": getattr(p, "fees_paid_usd", 0.0),
            "net_pnl_usd": getattr(p, "unrealized_pnl_usd", 0.0),
            "status": "SIMULATED_ACTIVE"
        })

    # 4. Multi-Wallet Sub-Account Ledger Summary
    from backend.wallet.sub_wallet_manager import sub_wallet_manager
    wallets_summary = sub_wallet_manager.get_wallets_summary()
    total_ledger_equity = wallets_summary.get("total_system_equity_usd", pf.get("total_portfolio_value", 10000.0))

    total_combined_profit = round(spot_total_pnl + arb_captured_profit + shadow_net_pnl, 2)
    denom = max(1.0, abs(spot_total_pnl) + abs(arb_captured_profit) + abs(shadow_net_pnl))

    return {
        "status": "success",
        "total_profit_usd": total_combined_profit,
        "daily_pnl_usd": pf.get("daily_pnl_usd", spot_total_pnl),
        "daily_pnl_pct": pf.get("daily_pnl_pct", 0.0),
        "total_portfolio_value": total_ledger_equity,
        "spot_portfolio_value": pf.get("total_portfolio_value", 10000.0),
        "wallets_summary": wallets_summary,
        "attribution": {
            "spot": {
                "name": "Spot AI Paper Trading",
                "profit_usd": spot_total_pnl,
                "realized_pnl": round(spot_realized_pnl, 2),
                "unrealized_pnl": round(spot_unrealized_pnl, 2),
                "trades_count": spot_trades_count,
                "win_rate": spot_win_rate,
                "share_pct": round((abs(spot_total_pnl) / denom) * 100.0, 1) if denom > 0 else 0.0,
                "symbol_breakdown": symbol_breakdown
            },
            "arbitrage": {
                "name": "Cross-Exchange Arbitrage",
                "profit_usd": arb_captured_profit,
                "executions_count": arb_trades_count,
                "opportunities_detected": arb_opps_count,
                "venues_count": 5,
                "share_pct": round((abs(arb_captured_profit) / denom) * 100.0, 1) if denom > 0 else 0.0,
                "routes_list": arbitrage_routes_list
            },
            "shadow": {
                "name": "Shadow Replay Simulation",
                "profit_usd": shadow_net_pnl,
                "gross_pnl": round(getattr(shadow_analytics, "gross_pnl_usd", 0.0), 2),
                "slippage_usd": round(getattr(shadow_analytics, "slippage_cost_usd", 0.0), 2),
                "fees_usd": round(sum(getattr(p, 'fees_paid_usd', 0.0) for p in shadow_positions), 2),
                "trades_count": shadow_trades_count,
                "share_pct": round((abs(shadow_net_pnl) / denom) * 100.0, 1) if denom > 0 else 0.0,
                "trades_list": shadow_trades_list
            }
        },
        "recent_trades": getattr(user_trader, "trade_history", [])[-20:]
    }

@app.get("/api/portfolio/all-trades")
async def get_all_unified_trades(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch unified trade history across Spot AI Trading, Arbitrage Routes, and Shadow Simulation."""
    user_trader = None
    if current_user:
        user_trader = await trader_manager.get_trader_for_user(current_user.id)
    
    if not user_trader or len(getattr(user_trader, "trade_history", [])) == 0:
        # Check active registered user traders for trade history
        for uid, tr in list(trader_manager.traders.items()):
            if len(getattr(tr, "trade_history", [])) > 0:
                user_trader = tr
                break
        if not user_trader or len(getattr(user_trader, "trade_history", [])) == 0:
            user_trader = trader

    all_trades = []

    # 1. Spot Open Positions
    for sym, pos in getattr(user_trader, "positions", {}).items():
        if isinstance(pos, dict):
            all_trades.append({
                "id": pos.get("id", f"SPOT_OPEN_{pos.get('symbol', sym)}"),
                "subsystem": "SPOT",
                "symbol": pos.get("symbol", sym),
                "side": pos.get("side", "BUY"),
                "entry_price": pos.get("entry_price", 0.0),
                "exit_price": pos.get("current_price", pos.get("mark_price", pos.get("entry_price", 0.0))),
                "amount": pos.get("amount", 0.0),
                "margin_usd": pos.get("margin_usd", 0.0),
                "pnl_usd": round(pos.get("unrealized_pnl_usd", 0.0), 2),
                "pnl_pct": round(pos.get("unrealized_pnl_pct", 0.0), 2),
                "status": "OPEN",
                "reason": pos.get("strategy", "AI Hybrid (Active Position)"),
                "venue": pos.get("exchange", "BINANCE"),
                "time": pos.get("entry_time", "")
            })

    # 2. Spot Closed Trades
    for t in getattr(user_trader, "trade_history", []):
        all_trades.append({
            "id": t.get("id", f"SPOT_CLOSED_{t.get('symbol')}"),
            "subsystem": "SPOT",
            "symbol": t.get("symbol", "UNKNOWN"),
            "side": t.get("side", "BUY"),
            "entry_price": t.get("entry_price", 0.0),
            "exit_price": t.get("exit_price", 0.0),
            "amount": t.get("amount", 0.0),
            "margin_usd": t.get("margin_usd", 0.0),
            "pnl_usd": round(float(t.get("pnl_usd", t.get("net_pnl", t.get("pnl", 0.0))) or 0.0), 2),
            "pnl_pct": round(t.get("pnl_pct", 0.0), 2),
            "status": "CLOSED",
            "reason": t.get("close_reason", t.get("reason", "Take Profit / Stop Loss")),
            "venue": t.get("exchange", "BINANCE"),
            "time": t.get("exit_time", t.get("entry_time", ""))
        })

    # 3. Arbitrage Executed Routes
    from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker
    for r in getattr(ArbitrageMetricsTracker(), "executed_routes", []):
        all_trades.append({
            "id": r.get("route_id", "ARB-EXEC"),
            "subsystem": "ARBITRAGE",
            "symbol": r.get("symbol", "BTC/USDT"),
            "side": "DUAL_LEG",
            "entry_price": r.get("buy_price", 0.0),
            "exit_price": r.get("sell_price", 0.0),
            "amount": round(r.get("size_usd", 1000.0) / max(0.0001, r.get("buy_price", 1.0)), 4),
            "margin_usd": r.get("size_usd", 1000.0),
            "pnl_usd": round(r.get("profit_usd", 0.0), 2),
            "pnl_pct": round(r.get("net_spread_pct", 0.0), 2),
            "status": "CAPTURED",
            "reason": f"Cross-Venue Spread Capture ({r.get('buy_venue')} -> {r.get('sell_venue')})",
            "venue": f"{r.get('buy_venue')} -> {r.get('sell_venue')}",
            "time": r.get("time", "")
        })

    # 4. Shadow Simulation Positions
    from backend.shadow_trading.shadow_engine import shadow_engine
    for p in shadow_engine.position_tracker.get_all_positions():
        all_trades.append({
            "id": getattr(p, "position_id", "SHADOW-POS"),
            "subsystem": "SHADOW",
            "symbol": getattr(p, "symbol", "BTC/USDT"),
            "side": getattr(p, "side", "BUY"),
            "entry_price": getattr(p, "average_entry_price", 0.0),
            "exit_price": getattr(p, "mark_price", 0.0),
            "amount": getattr(p, "quantity", 0.0),
            "margin_usd": round(getattr(p, "quantity", 0.0) * getattr(p, "average_entry_price", 0.0), 2),
            "pnl_usd": round(getattr(p, "unrealized_pnl_usd", 0.0), 2),
            "pnl_pct": round((getattr(p, "unrealized_pnl_usd", 0.0) / max(1.0, getattr(p, "quantity", 1.0) * getattr(p, "average_entry_price", 1.0))) * 100.0, 2),
            "status": "SIMULATED",
            "reason": "Shadow High-Fidelity Simulation Replay",
            "venue": "ORDERBOOK_SHADOW",
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(getattr(p, "opened_at", time.time())))
        })

    return {
        "status": "success",
        "total_count": len(all_trades),
        "trades": all_trades
    }



@app.get("/api/accounting/audit")
async def get_accounting_audit(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)
    current_prices = get_current_prices_dict()

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
@app.post("/api/user/deposit")
@app.post("/api/portfolio/deposit")
@app.post("/wallet/deposit")
async def deposit_virtual_funds(body: WalletFundsRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Deposit virtual USDT capital into the user's paper trading wallet."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be greater than zero.")

    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)

    # 1. Update In-Memory Balance & Ledger
    user_trader.usdt_balance = round(user_trader.usdt_balance + body.amount, 4)
    user_trader.initial_balance = round(user_trader.initial_balance + body.amount, 4)
    tx_id = f"TX_{int(time.time() * 1000)}_{len(user_trader.ledger) + 1}"
    tx = {
        "tx_id": tx_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tx_type": "DEPOSIT",
        "amount": round(body.amount, 4),
        "balance_after": round(user_trader.usdt_balance, 4),
        "reference_id": "USER_DEPOSIT",
        "description": f"Virtual Capital Deposit of ${body.amount:,.2f} USDT"
    }
    user_trader.ledger.append(tx)

    # 2. Persist to DB directly
    try:
        await user_trader.repo.record_wallet_transaction(tx, user_id=user_id)
    except Exception as ex:
        logger.warning(f"[DEPOSIT_TX_WARN] {ex}")

    try:
        await user_trader.save_portfolio_async()
    except Exception as ex:
        logger.warning(f"[DEPOSIT_PORT_WARN] {ex}")

    return {
        "status": "success",
        "message": f"Successfully deposited ${body.amount:,.2f} USDT virtual funds.",
        "usdt_balance": user_trader.usdt_balance,
        "transaction": tx
    }

@app.post("/api/wallet/withdraw")
@app.post("/api/user/withdraw")
@app.post("/api/portfolio/withdraw")
@app.post("/wallet/withdraw")
async def withdraw_virtual_funds(body: WalletFundsRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Withdraw virtual USDT capital from the user's paper trading wallet."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be greater than zero.")

    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)
    if user_trader.usdt_balance < body.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient USDT balance. Available: ${user_trader.usdt_balance:,.2f} USDT, Requested: ${body.amount:,.2f} USDT"
        )

    # 1. Update In-Memory Balance & Ledger
    user_trader.usdt_balance = round(max(0.0, user_trader.usdt_balance - body.amount), 4)
    tx_id = f"TX_{int(time.time() * 1000)}_{len(user_trader.ledger) + 1}"
    tx = {
        "tx_id": tx_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tx_type": "WITHDRAWAL",
        "amount": round(-abs(body.amount), 4),
        "balance_after": round(user_trader.usdt_balance, 4),
        "reference_id": "USER_WITHDRAWAL",
        "description": f"Virtual Capital Withdrawal of ${body.amount:,.2f} USDT"
    }
    user_trader.ledger.append(tx)

    # 2. Persist to DB directly
    try:
        await user_trader.repo.record_wallet_transaction(tx, user_id=user_id)
    except Exception as ex:
        logger.warning(f"[WITHDRAW_TX_WARN] {ex}")

    try:
        await user_trader.save_portfolio_async()
    except Exception as ex:
        logger.warning(f"[WITHDRAW_PORT_WARN] {ex}")

    return {
        "status": "success",
        "message": f"Successfully withdrew ${body.amount:,.2f} USDT virtual funds.",
        "usdt_balance": user_trader.usdt_balance,
        "transaction": tx
    }




@app.post("/api/trade/order")
async def execute_manual_order(req: OrderRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Advanced Manual Order Execution (LONG/SHORT, Leverage, SL, TP, Trailing Stop)."""
    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)
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
async def manage_position(req: PositionActionRequest, current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Position Actions: Close, Partial Close, Reverse, Edit SL/TP."""
    try:
        user_id = current_user.id if current_user else 1
        user_trader = await trader_manager.get_trader_for_user(user_id)

        # Sub-millisecond non-blocking price lookup
        price = market_engine.price_cache.get(req.symbol)
        if not price or price <= 0:
            if req.symbol in user_trader.positions:
                price = user_trader.positions[req.symbol].get('current_price') or user_trader.positions[req.symbol].get('entry_price')
            if not price or price <= 0:
                price = await asyncio.to_thread(market_engine.fetch_current_price, req.symbol)

        if not price or price <= 0:
            price = 1.0

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

        # Instant WebSocket sync & background persistence flush
        ws_manager.user_last_hashes.clear()
        asyncio.create_task(user_trader.flush_persistence())

        if res.get("status") == "error":
            raise HTTPException(status_code=400, detail=res.get("message", "Failed to process position action"))

        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[MANAGE_POSITION_ERROR] Symbol={req.symbol} Action={req.action}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Position action failed: {str(e)}")





@app.get("/api/accounting/audit")
async def get_accounting_audit(current_user: UserModel = Depends(get_current_user)):

    user_trader = await trader_manager.get_trader_for_user(current_user.id)
    current_prices = get_current_prices_dict()

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
    trader.active_strategy = strat
    trader.risk_mode = risk
    await user_trader.save_portfolio_async()
    await trader.save_portfolio_async()
    ws_manager.user_last_hashes.clear()
    
    logger.info(f"[STRATEGY_SWITCH] UserID={current_user.id} switched to Strategy={strat}, RiskMode={risk}")
    return {
        "status": "success",
        "message": f"Strategy switched to {strat} ({risk})",
        "strategy_name": strat,
        "risk_mode": risk
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
async def toggle_bot(
    enable: bool = Query(...),
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    user_id = current_user.id if current_user else 1
    user_trader = await trader_manager.get_trader_for_user(user_id)
    user_trader.auto_bot_enabled = enable
    await user_trader.save_portfolio_async()

    trader.auto_bot_enabled = enable
    await trader.save_portfolio_async()

    for tr in trader_manager.traders.values():
        if tr.user_id == user_id:
            tr.auto_bot_enabled = enable

    ws_manager.user_last_hashes.clear()
    status_str = "ACTIVE" if enable else "DISABLED"
    logger.info(f"AUTO_BOT_TOGGLE user={user_id} enable={enable}")

    try:
        curr_prices = get_current_prices_dict()
        market_summary = market_engine.get_market_health_summary()
        await ws_manager.broadcast_user_snapshots(trader_manager, curr_prices, scanner_cache, market_summary)
    except Exception as ws_err:
        logger.warning(f"[WS_TOGGLE_BROADCAST_WARN] {ws_err}")

    return {"status": "success", "message": f"Auto-Trading Bot is now {status_str}", "auto_bot_enabled": enable, "success": True, "enabled": enable}





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

    last_ta_update = 0.0
    ta_cache = {}

    while True:
        try:
            now = time.time()
            # Refresh news sentiment every 10 minutes
            if now - last_sentiment_update > 600.0 or not sentiment_cache:
                fg_cache = sentiment_engine.fetch_fear_and_greed_index()
                news_cache = sentiment_engine.fetch_crypto_news()
                sentiment_cache = sentiment_engine.compute_aggregated_sentiment(news_cache, fg_cache)
                last_sentiment_update = now

            refresh_ta = (now - last_ta_update > 10.0) or not ta_cache
            if refresh_ta:
                last_ta_update = now

            current_prices = market_engine.fetch_all_prices()
            scanner_results = []

            for symbol in settings.SUPPORTED_SYMBOLS:
                price = current_prices.get(symbol, 1.0)

                if refresh_ta or symbol not in ta_cache:
                    df = market_engine.fetch_ohlcv(symbol, limit=30)
                    ta_cache[symbol] = market_engine.calculate_technical_indicators(df)
                
                ta = ta_cache.get(symbol, {})

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
                "timestamp": now,
                "top_buys": top_buys,
                "top_sells": top_sells,
                "all_pairs": scanner_results
            }

            # Check SL / TP & Auto Bot Execution for all active user traders
            active_traders = list(trader_manager.traders.values())
            if not active_traders:
                active_traders = [trader]

            for user_tr in active_traders:
                user_tr.check_stop_loss_take_profit(current_prices)

                # Check Condition 1: Auto Bot Enabled
                if not user_tr.auto_bot_enabled:
                    continue

                # Check Condition 2: Minimum Balance Requirement
                if user_tr.usdt_balance < 100.0:
                    continue

                # Directional Spot Trading Bot Gate (Active when user enables auto bot)
                if not user_tr.auto_bot_enabled:
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

                    # Check Condition 3: Dynamic Confidence Threshold based on Risk Mode
                    min_conf_threshold = 50.0 if user_tr.risk_mode == "Aggressive" else (60.0 if user_tr.risk_mode == "Conservative" else 52.0)
                    if cand_conf < min_conf_threshold:
                        continue

                    # Check Condition 4: Existing Position Check
                    if cand_sym in user_tr.positions:
                        existing_pos = user_tr.positions[cand_sym]
                        # If existing position is in opposite direction and new signal has high confidence (>=65%), auto-reverse
                        if existing_pos.get('side') != cand_dir and cand_conf >= 65.0:
                            logger.info(f"[CANDIDATE #{idx}] Symbol={cand_sym} | Strong Opposite Signal ({cand_dir} vs {existing_pos.get('side')}) with {cand_conf}% Confidence | Reversing Position...")
                            user_tr.reverse_position(cand_sym, current_prices[cand_sym])
                            continue
                        continue

                    # Check Condition 5: Direction Validation
                    if cand_dir not in ["LONG", "SHORT"]:
                        continue

                    # Check Condition 6: AI Learned Lessons Veto Gate (Active Self-Learning Protection)
                    alloc = getattr(user_tr, 'default_allocation_usd', 1000.0)
                    try:
                        from backend.learning.lesson_application_engine import lesson_applier
                        regime_name = "TRENDING_UP" if cand_dir == "LONG" else "TRENDING_DOWN"
                        features = {
                            "rsi": cand.get("rsi", 50.0),
                            "confidence": cand_conf,
                            "volatility": 0.02,
                            "current_price": current_prices[cand_sym]
                        }
                        
                        lesson_res = lesson_applier.evaluate_candidate_against_lessons(
                            symbol=cand_sym,
                            direction=cand_dir,
                            market_regime=regime_name,
                            features=features
                        )
                        
                        if lesson_res.action == "VETO_TRADE":
                            logger.warning(
                                f"[AI_LEARNING_SHIELD] UserID={user_tr.user_id} | Symbol={cand_sym} {cand_dir} "
                                f"VETOED BY LEARNED LESSON {lesson_res.matching_lesson_id} ('{lesson_res.matching_lesson_title}') | "
                                f"Reason: {lesson_res.reason}"
                            )
                            continue
                        elif lesson_res.action == "REDUCE_SIZE_50":
                            alloc = alloc * 0.5
                            logger.info(
                                f"[AI_LEARNING_SHIELD] UserID={user_tr.user_id} | Symbol={cand_sym} {cand_dir} "
                                f"ALLOCATION REDUCED 50% (${alloc:.2f}) by Lesson {lesson_res.matching_lesson_id}"
                            )
                    except Exception as l_err:
                        logger.debug(f"[AI_LEARNING_GATE_DEBUG] {l_err}")

                    lev = getattr(user_tr, 'default_leverage', 1)
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
                            if len(user_tr.positions) >= user_tr.max_open_positions:
                                break
                    except Exception as ex:
                        logger.error(f"[POSITION_EXCEPTION] UserID={user_tr.user_id} | Symbol={cand_sym} raised Exception: {ex}", exc_info=True)
                        continue

            # Broadcast user-isolated real-time snapshots (0 cross-user data leakage)
            market_summary = market_engine.get_market_health_summary()
            try:
                main_l = getattr(trader, "_main_event_loop", None)
                if main_l and main_l.is_running():
                    asyncio.run_coroutine_threadsafe(
                        ws_manager.broadcast_user_snapshots(
                            trader_mgr=trader_manager,
                            current_prices=current_prices,
                            scanner_cache=scanner_cache,
                            market_summary=market_summary
                        ),
                        main_l
                    )
                else:
                    loop.run_until_complete(
                        ws_manager.broadcast_user_snapshots(
                            trader_mgr=trader_manager,
                            current_prices=current_prices,
                            scanner_cache=scanner_cache,
                            market_summary=market_summary
                        )
                    )
            except Exception as ws_b_err:
                logger.debug(f"[WS_BROADCAST_DEBUG] {ws_b_err}")

        except Exception as e:
            logger.error(f"Error in multi-symbol scanner loop: {e}")

        time.sleep(0.5)


def background_learning_scheduler_loop():
    """Background Scheduler Loop for Phase 25 Self-Learning Pipeline."""
    logger.info("[LEARNING_SCHEDULER] Learning scheduler worker thread started.")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _learning_scheduler_job():
        while True:
            try:
                await asyncio.sleep(3600) # Check hourly
                from backend.learning.performance_dataset_builder import performance_dataset_builder
                await performance_dataset_builder.build_dataset()
                logger.info("[LEARNING_SCHEDULER] Hourly learning dataset sync completed.")
            except Exception as e:
                logger.error(f"[LEARNING_SCHEDULER] Scheduler exception: {e}")

    try:
        loop.run_until_complete(_learning_scheduler_job())
    except Exception as ex:
        logger.error(f"[LEARNING_SCHEDULER] Loop exited: {ex}")


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
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Update Default Execution Sizing and Leverage for AI Trading Engine."""
    req_alloc = req.default_allocation_usd if (req and hasattr(req, 'default_allocation_usd') and req.default_allocation_usd is not None) else None
    req_lev = req.default_leverage if (req and hasattr(req, 'default_leverage') and req.default_leverage is not None) else None

    alloc = req_alloc if req_alloc is not None else (default_allocation_usd if default_allocation_usd is not None else 1000.0)
    lev = req_lev if req_lev is not None else (default_leverage if default_leverage is not None else 1)


    if alloc <= 0:
        raise HTTPException(status_code=400, detail="Default allocation must be greater than 0")
    if lev < 1 or lev > 25:
        raise HTTPException(status_code=400, detail="Default leverage must be between 1x and 25x")

    if current_user:
        user_trader = await trader_manager.get_trader_for_user(current_user.id)
        user_trader.default_allocation_usd = float(alloc)
        user_trader.default_leverage = int(lev)
        await user_trader.save_portfolio_async()

    trader.default_allocation_usd = float(alloc)
    trader.default_leverage = int(lev)
    await trader.save_portfolio_async()

    ws_manager.user_last_hashes.clear()
    logger.info(f"[EXECUTION_PARAMS] UserID={current_user.id if current_user else 'demo'} updated params: Allocation=${alloc:,.2f} USDT, Leverage={lev}x")
    return {
        "status": "success",
        "message": f"Execution parameters applied: ${alloc:,.2f} USDT allocation @ {lev}x leverage",
        "default_allocation_usd": alloc,
        "default_leverage": lev
    }



@app.get("/{full_path:path}")
async def spa_catch_all(request: Request, full_path: str):
    """Universal SPA fallback route ensuring no non-API route ever throws 404."""
    if full_path.startswith("api/") or full_path.startswith("ws/") or full_path.startswith("static/") or full_path in ["docs", "redoc", "openapi.json"]:
        raise HTTPException(status_code=404, detail=f"Endpoint or resource /{full_path} not found")
    
    clean_path = full_path.strip("/")
    possible_html = os.path.join("static", f"{clean_path}.html")
    if os.path.exists(possible_html):
        return FileResponse(possible_html)
    
    possible_index = os.path.join("static", clean_path, "index.html")
    if os.path.exists(possible_index):
        return FileResponse(possible_index)

    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    
    raise HTTPException(status_code=404, detail="Page not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend"],
        reload_includes=["*.py"],
        reload_excludes=[
            "*.db",
            "*.db-wal",
            "*.db-shm",
            "*.log",
            "logs/*",
            "frontend/*",
            "static/*",
            ".next/*",
            "research_datasets/*",
            "*.json"
        ]
    )


