from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from backend.auth.security import get_current_user
from backend.models.domain import UserModel
from trader import trader_manager

router = APIRouter(prefix="/api/preferences", tags=["Trading Preferences"])

class TradingPreferencesUpdateSchema(BaseModel):
    max_concurrent_trades: Optional[int] = Field(default=None, ge=1, le=50)
    max_capital_per_trade_pct: Optional[float] = Field(default=None, ge=1.0, le=25.0)
    daily_loss_limit_pct: Optional[float] = Field(default=None, ge=1.0, le=20.0)
    symbol_cooldown_minutes: Optional[int] = Field(default=None, ge=0, le=120)
    allowed_symbols: Optional[List[str]] = None

@router.get("/trading")
async def get_trading_preferences(current_user: UserModel = Depends(get_current_user)):
    """Fetch trading preferences for the current logged in user."""
    trader_inst = await trader_manager.get_trader_for_user(current_user.id)
    
    max_trades = getattr(trader_inst.risk_manager.config, "max_concurrent_trades", trader_inst.max_open_positions)
    max_cap_pct = getattr(trader_inst, "max_capital_per_trade_pct", 10.0)
    daily_loss_pct = getattr(trader_inst.risk_manager.config, "max_daily_loss_pct", 5.0)
    cooldown_mins = getattr(trader_inst, "symbol_cooldown_minutes", 10)
    allowed_syms = getattr(trader_inst, "allowed_symbols", ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "AVAX/USDT", "DOGE/USDT", "XRP/USDT", "ADA/USDT", "LINK/USDT", "DOT/USDT"])
    
    return {
        "status": "success",
        "preferences": {
            "max_concurrent_trades": max_trades,
            "max_capital_per_trade_pct": max_cap_pct,
            "daily_loss_limit_pct": daily_loss_pct,
            "symbol_cooldown_minutes": cooldown_mins,
            "allowed_symbols": allowed_syms
        },
        # Direct key mappings for flexible frontend consumption
        "max_concurrent_trades": max_trades,
        "max_capital_per_trade_pct": max_cap_pct,
        "daily_loss_limit_pct": daily_loss_pct,
        "symbol_cooldown_minutes": cooldown_mins,
        "allowed_symbols": allowed_syms
    }

@router.put("/trading")
async def update_trading_preferences(
    body: TradingPreferencesUpdateSchema,
    current_user: UserModel = Depends(get_current_user)
):
    """Update trading preferences and apply changes immediately to Risk Manager and Trader Engine."""
    trader_inst = await trader_manager.get_trader_for_user(current_user.id)

    if body.max_concurrent_trades is not None:
        trader_inst.max_open_positions = body.max_concurrent_trades
        trader_inst.risk_manager.config.max_concurrent_trades = body.max_concurrent_trades

    if body.max_capital_per_trade_pct is not None:
        trader_inst.max_capital_per_trade_pct = body.max_capital_per_trade_pct

    if body.daily_loss_limit_pct is not None:
        trader_inst.risk_manager.config.max_daily_loss_pct = body.daily_loss_limit_pct
        trader_inst.risk_manager.config.max_daily_loss_usd = (body.daily_loss_limit_pct / 100.0) * trader_inst.initial_balance

    if body.symbol_cooldown_minutes is not None:
        trader_inst.symbol_cooldown_minutes = body.symbol_cooldown_minutes

    if body.allowed_symbols is not None:
        trader_inst.allowed_symbols = body.allowed_symbols

    await trader_inst.save_portfolio_async()

    max_trades = trader_inst.risk_manager.config.max_concurrent_trades
    max_cap_pct = getattr(trader_inst, "max_capital_per_trade_pct", 10.0)
    daily_loss_pct = trader_inst.risk_manager.config.max_daily_loss_pct
    cooldown_mins = getattr(trader_inst, "symbol_cooldown_minutes", 10)
    allowed_syms = getattr(trader_inst, "allowed_symbols", ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "AVAX/USDT", "DOGE/USDT", "XRP/USDT", "ADA/USDT", "LINK/USDT", "DOT/USDT"])

    logger.info(f"[PREFERENCES_UPDATED] UserID={current_user.id} | MaxTrades={max_trades} | MaxCap={max_cap_pct}% | DailyLossLimit={daily_loss_pct}% | Cooldown={cooldown_mins}m")

    return {
        "status": "success",
        "message": "Trading preferences updated successfully.",
        "preferences": {
            "max_concurrent_trades": max_trades,
            "max_capital_per_trade_pct": max_cap_pct,
            "daily_loss_limit_pct": daily_loss_pct,
            "symbol_cooldown_minutes": cooldown_mins,
            "allowed_symbols": allowed_syms
        },
        "max_concurrent_trades": max_trades,
        "max_capital_per_trade_pct": max_cap_pct,
        "daily_loss_limit_pct": daily_loss_pct,
        "symbol_cooldown_minutes": cooldown_mins,
        "allowed_symbols": allowed_syms
    }
