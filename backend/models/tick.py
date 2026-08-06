from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import String, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class MarketTickModel(Base):
    """Database model for storing real-time and replay market ticks."""
    __tablename__ = "market_ticks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, default=100.0)
    bid: Mapped[float] = mapped_column(Float, default=0.0)
    ask: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "price": self.price,
            "volume": self.volume,
            "bid": self.bid,
            "ask": self.ask,
            "timestamp": self.timestamp,
            "created_at": self.created_at.isoformat() if self.created_at else ""
        }
