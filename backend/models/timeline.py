from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy import String, Text, DateTime, Integer, Float, ForeignKey, JSON

from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class TradeTimelineModel(Base):
    """Database model for storing sequential trade decision timelines."""
    __tablename__ = "trade_timelines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trade_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trade_id": self.trade_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "event_type": self.event_type,
            "description": self.description,
            "metadata": self.event_metadata or {},
            "timestamp": self.timestamp,
            "created_at": self.created_at.isoformat() if self.created_at else ""
        }
