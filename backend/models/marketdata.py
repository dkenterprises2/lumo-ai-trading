from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class MarketTickModel(Base):
    """Market Ticks Table."""
    __tablename__ = "market_ticks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class OrderbookSnapshotModel(Base):
    """Orderbook Snapshots Table."""
    __tablename__ = "orderbook_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)
    sequence_id: Mapped[int] = mapped_column(Integer, nullable=False)

class OrderbookDeltaModel(Base):
    """Orderbook Deltas Table."""
    __tablename__ = "orderbook_deltas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)

class VolumeProfileModel(Base):
    """Volume Profiles Table."""
    __tablename__ = "volume_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)
    poc_price: Mapped[float] = mapped_column(Float, nullable=False)

class FootprintBarModel(Base):
    """Footprint Bars Table."""
    __tablename__ = "footprint_bars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)

class LiquidityHeatmapModel(Base):
    """Liquidity Heatmaps Table."""
    __tablename__ = "liquidity_heatmaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)

class MarketImpactEstimateModel(Base):
    """Market Impact Estimates Table."""
    __tablename__ = "market_impact_estimates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)

class SpoofingAlertModel(Base):
    """Spoofing Alerts Table."""
    __tablename__ = "spoofing_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class LayeringAlertModel(Base):
    """Layering Alerts Table."""
    __tablename__ = "layering_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class MicrostructureSignalModel(Base):
    """Microstructure Signals Table."""
    __tablename__ = "microstructure_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, index=True, nullable=False)

class ReplaySessionModel(Base):
    """Replay Sessions Table."""
    __tablename__ = "replay_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExchangeFeedStatusModel(Base):
    """Exchange Feed Status Table."""
    __tablename__ = "exchange_feed_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exchange: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class WebSocketMarketDataSessionModel(Base):
    """WebSocket Market Data Sessions Table."""
    __tablename__ = "websocket_marketdata_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
