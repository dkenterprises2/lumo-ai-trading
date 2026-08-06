from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class TradeJournalModel(Base):
    """Institutional Trade Journal Database Model for storing completed trade provenance."""
    __tablename__ = "trade_journal"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    strategy: Mapped[str] = mapped_column(String(64), default="AI Hybrid")
    confidence: Mapped[float] = mapped_column(Float, default=75.0)
    market_regime: Mapped[str] = mapped_column(String(64), default="BULL_TREND")
    sentiment_score: Mapped[float] = mapped_column(Float, default=50.0)

    score_breakdown: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    reasons: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    indicators: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    risk_checks: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float] = mapped_column(Float, nullable=False)
    pnl_usd: Mapped[float] = mapped_column(Float, nullable=False)
    pnl_pct: Mapped[float] = mapped_column(Float, nullable=False)
    holding_time_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    execution_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)

    entry_time: Mapped[str] = mapped_column(String(64), nullable=False)
    exit_time: Mapped[str] = mapped_column(String(64), nullable=False)
    close_reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side,
            "strategy": self.strategy,
            "confidence": self.confidence,
            "market_regime": self.market_regime,
            "sentiment_score": self.sentiment_score,
            "score_breakdown": self.score_breakdown or {},
            "reasons": self.reasons or [],
            "indicators": self.indicators or {},
            "risk_checks": self.risk_checks or {},
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "pnl_usd": self.pnl_usd,
            "pnl_pct": self.pnl_pct,
            "holding_time_seconds": self.holding_time_seconds,
            "execution_latency_ms": self.execution_latency_ms,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "close_reason": self.close_reason,
            "created_at": self.created_at.isoformat() if self.created_at else ""
        }
