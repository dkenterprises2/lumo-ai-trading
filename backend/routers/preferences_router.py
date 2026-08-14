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
    default_allocation_usd: Optional[float] = Field(default=None, ge=10.0, le=100000.0)
    default_leverage: Optional[int] = Field(default=None, ge=1, le=100)

DEFAULT_50_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT",
    "MATIC/USDT", "ATOM/USDT", "NEAR/USDT", "APT/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "LTC/USDT", "ETC/USDT", "XLM/USDT",
    "FIL/USDT", "INJ/USDT", "TIA/USDT", "UNI/USDT", "ICP/USDT", "FET/USDT", "RNDR/USDT", "PEPE/USDT", "SHIB/USDT", "FLOKI/USDT",
    "AAVE/USDT", "MKR/USDT", "SNX/USDT", "CRV/USDT", "LDO/USDT", "GRT/USDT", "ALGO/USDT", "FTM/USDT", "SAND/USDT", "MANA/USDT",
    "THETA/USDT", "AXS/USDT", "EGLD/USDT", "EOS/USDT", "FLOW/USDT", "KAVA/USDT", "MINA/USDT", "QNT/USDT", "RUNE/USDT", "WOO/USDT"
]

@router.get("/trading")
async def get_trading_preferences(current_user: UserModel = Depends(get_current_user)):
    """Fetch trading preferences for the current logged in user."""
    trader_inst = await trader_manager.get_trader_for_user(current_user.id)
    
    max_trades = getattr(trader_inst.risk_manager.config, "max_concurrent_trades", trader_inst.max_open_positions)
    max_cap_pct = getattr(trader_inst, "max_capital_per_trade_pct", 10.0)
    daily_loss_pct = getattr(trader_inst.risk_manager.config, "max_daily_loss_pct", 5.0)
    cooldown_mins = getattr(trader_inst, "symbol_cooldown_minutes", 10)
    allowed_syms = getattr(trader_inst, "allowed_symbols", DEFAULT_50_SYMBOLS)
    alloc_usd = getattr(trader_inst, "default_allocation_usd", 1000.0)
    leverage = getattr(trader_inst, "default_leverage", 1)
    
    return {
        "status": "success",
        "preferences": {
            "max_concurrent_trades": max_trades,
            "max_capital_per_trade_pct": max_cap_pct,
            "daily_loss_limit_pct": daily_loss_pct,
            "symbol_cooldown_minutes": cooldown_mins,
            "allowed_symbols": allowed_syms,
            "default_allocation_usd": alloc_usd,
            "default_leverage": leverage
        },
        "max_concurrent_trades": max_trades,
        "max_capital_per_trade_pct": max_cap_pct,
        "daily_loss_limit_pct": daily_loss_pct,
        "symbol_cooldown_minutes": cooldown_mins,
        "allowed_symbols": allowed_syms,
        "default_allocation_usd": alloc_usd,
        "default_leverage": leverage
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
        trader_inst.risk_manager.config.max_exposure_ratio = max(50.0, float(body.max_concurrent_trades * 2.0))
        trader_inst.risk_manager.config.correlation_group_limit = body.max_concurrent_trades

    if body.max_capital_per_trade_pct is not None:
        trader_inst.max_capital_per_trade_pct = body.max_capital_per_trade_pct

    if body.daily_loss_limit_pct is not None:
        trader_inst.risk_manager.config.max_daily_loss_pct = body.daily_loss_limit_pct
        trader_inst.risk_manager.config.max_daily_loss_usd = (body.daily_loss_limit_pct / 100.0) * trader_inst.initial_balance

    if body.symbol_cooldown_minutes is not None:
        trader_inst.symbol_cooldown_minutes = body.symbol_cooldown_minutes

    if body.allowed_symbols is not None and len(body.allowed_symbols) >= (body.max_concurrent_trades or 10):
        trader_inst.allowed_symbols = body.allowed_symbols
    else:
        trader_inst.allowed_symbols = DEFAULT_50_SYMBOLS

    if body.default_allocation_usd is not None:
        trader_inst.default_allocation_usd = body.default_allocation_usd

    if body.default_leverage is not None:
        trader_inst.default_leverage = body.default_leverage

    await trader_inst.save_portfolio_async()

    max_trades = trader_inst.risk_manager.config.max_concurrent_trades
    max_cap_pct = getattr(trader_inst, "max_capital_per_trade_pct", 10.0)
    daily_loss_pct = trader_inst.risk_manager.config.max_daily_loss_pct
    cooldown_mins = getattr(trader_inst, "symbol_cooldown_minutes", 10)
    allowed_syms = getattr(trader_inst, "allowed_symbols", DEFAULT_50_SYMBOLS)
    alloc_usd = getattr(trader_inst, "default_allocation_usd", 1000.0)
    leverage = getattr(trader_inst, "default_leverage", 1)

    logger.info(f"[PREFERENCES_UPDATED] UserID={current_user.id} | MaxTrades={max_trades} | MaxCap={max_cap_pct}% | DailyLossLimit={daily_loss_pct}% | Cooldown={cooldown_mins}m | Alloc=${alloc_usd} | Leverage={leverage}x")

    return {
        "status": "success",
        "message": "Trading preferences updated successfully.",
        "preferences": {
            "max_concurrent_trades": max_trades,
            "max_capital_per_trade_pct": max_cap_pct,
            "daily_loss_limit_pct": daily_loss_pct,
            "symbol_cooldown_minutes": cooldown_mins,
            "allowed_symbols": allowed_syms,
            "default_allocation_usd": alloc_usd,
            "default_leverage": leverage
        },
        "max_concurrent_trades": max_trades,
        "max_capital_per_trade_pct": max_cap_pct,
        "daily_loss_limit_pct": daily_loss_pct,
        "symbol_cooldown_minutes": cooldown_mins,
        "allowed_symbols": allowed_syms,
        "default_allocation_usd": alloc_usd,
        "default_leverage": leverage
    }

