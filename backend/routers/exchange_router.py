from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.exchange.exchange_manager import exchange_manager_v21
from backend.execution.order_engine import live_order_engine

router = APIRouter(prefix="/api", tags=["Live Exchange & Execution Engine"])

@router.get("/exchanges")
async def get_supported_exchanges(current_user: UserModel = Depends(get_current_user)):
    """Return supported exchanges list."""
    return {
        "supported_exchanges": [
            {"id": "PAPER", "name": "Paper Trading Simulation", "type": "SPOT/FUTURES"},
            {"id": "BINANCE_SPOT", "name": "Binance Spot", "type": "SPOT"},
            {"id": "BINANCE_FUTURES", "name": "Binance USDSM Futures", "type": "FUTURES"},
            {"id": "BYBIT", "name": "Bybit Spot & USDT Perpetual", "type": "SPOT/FUTURES"},
            {"id": "OKX", "name": "OKX Spot & Swap", "type": "SPOT/FUTURES"}
        ]
    }

@router.get("/exchanges/status")
async def get_exchange_status(current_user: UserModel = Depends(get_current_user)):
    """Return latency, rate limit, and connection status across user's connected exchanges."""
    return exchange_manager_v21.get_exchange_status(current_user.id)

@router.post("/exchanges/connect")
async def connect_exchange_account(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Connect live exchange API key & secret key."""
    ex_name = body.get("exchange_name", "BINANCE_SPOT")
    api_key = body.get("api_key", "")
    secret_key = body.get("secret_key", "")
    testnet = body.get("is_testnet", True)

    adapter = exchange_manager_v21.connect_exchange(
        user_id=current_user.id,
        exchange_name=ex_name,
        api_key=api_key,
        secret_key=secret_key,
        testnet=testnet
    )

    return {
        "status": "success",
        "message": f"Successfully connected to {adapter.get_exchange_name()}.",
        "exchange_name": adapter.get_exchange_name()
    }

@router.post("/exchanges/disconnect")
async def disconnect_exchange_account(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Disconnect exchange account."""
    ex_name = body.get("exchange_name", "BINANCE_SPOT").upper()
    if current_user.id in exchange_manager_v21.user_adapters:
        exchange_manager_v21.user_adapters[current_user.id].pop(ex_name, None)
    return {"status": "success", "message": f"Disconnected {ex_name}."}

@router.get("/account/balance")
async def get_account_balance(exchange_name: str = Query("PAPER"), current_user: UserModel = Depends(get_current_user)):
    """Fetch wallet balance from connected exchange."""
    adapter = exchange_manager_v21.get_adapter(current_user.id, exchange_name)
    return adapter.fetch_balance()

@router.get("/account/positions")
async def get_account_positions(exchange_name: str = Query("PAPER"), current_user: UserModel = Depends(get_current_user)):
    """Fetch open positions from connected exchange."""
    adapter = exchange_manager_v21.get_adapter(current_user.id, exchange_name)
    return adapter.fetch_positions()

@router.get("/account/orders")
async def get_account_open_orders(exchange_name: str = Query("PAPER"), symbol: Optional[str] = None, current_user: UserModel = Depends(get_current_user)):
    """Fetch open active orders from connected exchange."""
    adapter = exchange_manager_v21.get_adapter(current_user.id, exchange_name)
    return adapter.fetch_open_orders(symbol=symbol)

@router.post("/orders")
async def submit_live_order(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    """Submit new order with pre-trade risk verification."""
    symbol = body.get("symbol", "BTC/USDT")
    side = body.get("side", "BUY").upper()
    amount_usd = float(body.get("amount_usd", 1000.0))
    order_type = body.get("order_type", "MARKET").upper()
    ex_name = body.get("exchange_name", "PAPER")
    leverage = int(body.get("leverage", 1))
    sl = body.get("stop_loss_price")
    tp = body.get("take_profit_price")
    price = body.get("price")

    return live_order_engine.submit_order(
        user_id=current_user.id,
        symbol=symbol,
        side=side,
        amount_usd=amount_usd,
        order_type=order_type,
        exchange_name=ex_name,
        leverage=leverage,
        stop_loss_price=float(sl) if sl else None,
        take_profit_price=float(tp) if tp else None,
        price=float(price) if price else None
    )

@router.delete("/orders/{order_id}")
async def cancel_live_order(order_id: str, symbol: str = Query("BTC/USDT"), exchange_name: str = Query("PAPER"), current_user: UserModel = Depends(get_current_user)):
    """Cancel an active open order."""
    return live_order_engine.cancel_order(current_user.id, order_id, symbol, exchange_name)
