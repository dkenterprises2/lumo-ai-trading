import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy import select
from loguru import logger

from backend.database.session import AsyncSessionLocal
from backend.models.trading_preferences import TradingPreferencesModel

PLAN_CONCURRENT_LIMITS: Dict[str, int] = {
    "FREE": 2,
    "BASIC": 5,
    "PRO": 10,
    "INSTITUTIONAL": 50,
}

class TradingPreferencesRepository:
    """Data repository for managing user trading preferences and plan tier limits."""

    @staticmethod
    def get_max_concurrent_limit_for_plan(plan_tier: str) -> int:
        tier_upper = (plan_tier or "FREE").upper()
        return PLAN_CONCURRENT_LIMITS.get(tier_upper, 2)

    async def get_by_user_id(self, user_id: int) -> TradingPreferencesModel:
        """Fetch trading preferences for a user, creating defaults if missing."""
        async with AsyncSessionLocal() as session:
            stmt = select(TradingPreferencesModel).where(TradingPreferencesModel.user_id == user_id)
            res = await session.execute(stmt)
            prefs = res.scalars().first()

            if not prefs:
                prefs = TradingPreferencesModel(
                    user_id=user_id,
                    max_concurrent_trades=3,
                    max_capital_per_trade_pct=10.0,
                    daily_loss_limit_pct=5.0,
                    symbol_cooldown_minutes=15,
                    allowed_symbols_json=json.dumps([
                        "BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "BNB/USDT", "LINK/USDT", "DOT/USDT", "ADA/USDT"
                    ])
                )
                session.add(prefs)
                await session.commit()
                await session.refresh(prefs)
                logger.info(f"[PREFERENCES_REPO] Created default trading preferences for user_id={user_id}")

            return prefs

    async def update_by_user_id(
        self,
        user_id: int,
        updates: Dict[str, Any],
        user_plan: str = "FREE"
    ) -> Tuple[Optional[TradingPreferencesModel], Optional[str]]:
        """
        Validate and update trading preferences for a user.
        Enforces plan-tier bounds on max_concurrent_trades.
        """
        plan_max_trades = self.get_max_concurrent_limit_for_plan(user_plan)

        async with AsyncSessionLocal() as session:
            stmt = select(TradingPreferencesModel).where(TradingPreferencesModel.user_id == user_id)
            res = await session.execute(stmt)
            prefs = res.scalars().first()

            if not prefs:
                prefs = TradingPreferencesModel(user_id=user_id)
                session.add(prefs)

            # Validate max_concurrent_trades
            if "max_concurrent_trades" in updates and updates["max_concurrent_trades"] is not None:
                val = int(updates["max_concurrent_trades"])
                if val < 1:
                    return None, "max_concurrent_trades must be at least 1."
                if val > plan_max_trades:
                    return None, f"Your {user_plan.upper()} plan permits a maximum of {plan_max_trades} concurrent trades. Upgrade your plan to increase this limit."
                prefs.max_concurrent_trades = val

            # Validate max_capital_per_trade_pct
            if "max_capital_per_trade_pct" in updates and updates["max_capital_per_trade_pct"] is not None:
                cap_pct = float(updates["max_capital_per_trade_pct"])
                if not (0.5 <= cap_pct <= 100.0):
                    return None, "max_capital_per_trade_pct must be between 0.5% and 100.0%."
                prefs.max_capital_per_trade_pct = cap_pct

            # Validate daily_loss_limit_pct
            if "daily_loss_limit_pct" in updates and updates["daily_loss_limit_pct"] is not None:
                loss_pct = float(updates["daily_loss_limit_pct"])
                if not (0.5 <= loss_pct <= 50.0):
                    return None, "daily_loss_limit_pct must be between 0.5% and 50.0%."
                prefs.daily_loss_limit_pct = loss_pct

            # Validate symbol_cooldown_minutes
            if "symbol_cooldown_minutes" in updates and updates["symbol_cooldown_minutes"] is not None:
                cool_mins = int(updates["symbol_cooldown_minutes"])
                if not (0 <= cool_mins <= 1440):
                    return None, "symbol_cooldown_minutes must be between 0 and 1440 minutes."
                prefs.symbol_cooldown_minutes = cool_mins

            # Validate allowed_symbols
            if "allowed_symbols" in updates and updates["allowed_symbols"] is not None:
                syms = updates["allowed_symbols"]
                if not isinstance(syms, list) or len(syms) == 0:
                    return None, "allowed_symbols must be a non-empty list of trading symbol strings."
                prefs.allowed_symbols = [str(s).upper().strip() for s in syms]

            prefs.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(prefs)
            logger.info(f"[PREFERENCES_REPO] Updated preferences for user_id={user_id}")
            return prefs, None

trading_preferences_repo = TradingPreferencesRepository()
