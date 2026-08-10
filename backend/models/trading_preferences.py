import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base

class TradingPreferencesModel(Base):
    """User-configurable trading risk and concurrency preferences."""
    __tablename__ = "trading_preferences"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    max_concurrent_trades: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    max_capital_per_trade_pct: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    daily_loss_limit_pct: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    symbol_cooldown_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    allowed_symbols_json: Mapped[str] = mapped_column(
        Text,
        default='["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "BNB/USDT", "LINK/USDT", "DOT/USDT", "ADA/USDT"]',
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    @property
    def allowed_symbols(self) -> List[str]:
        try:
            return json.loads(self.allowed_symbols_json)
        except Exception:
            return ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT"]

    @allowed_symbols.setter
    def allowed_symbols(self, value: List[str]):
        self.allowed_symbols_json = json.dumps(value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "max_concurrent_trades": self.max_concurrent_trades,
            "max_capital_per_trade_pct": self.max_capital_per_trade_pct,
            "daily_loss_limit_pct": self.daily_loss_limit_pct,
            "symbol_cooldown_minutes": self.symbol_cooldown_minutes,
            "allowed_symbols": self.allowed_symbols,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
