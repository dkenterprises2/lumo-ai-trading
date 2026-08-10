import time
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database.session import Base

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), default="Trader User")
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    avatar: Mapped[str] = mapped_column(String(256), default="https://api.dicebear.com/7.x/avataaars/svg?seed=LumoTrader")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    trading_mode: Mapped[str] = mapped_column(String(32), default="Paper")
    role: Mapped[str] = mapped_column(String(32), default="trader")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserSessionModel(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    session_token: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class PasswordResetTokenModel(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class SettingsModel(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class PortfolioModel(Base):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    usdt_balance: Mapped[float] = mapped_column(Float, default=10000.0)
    initial_balance: Mapped[float] = mapped_column(Float, default=10000.0)
    margin_used: Mapped[float] = mapped_column(Float, default=0.0)
    total_value: Mapped[float] = mapped_column(Float, default=10000.0)
    auto_bot_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    active_strategy: Mapped[str] = mapped_column(String(64), default="AI Hybrid")
    risk_mode: Mapped[str] = mapped_column(String(32), default="Moderate")
    default_allocation_usd: Mapped[float] = mapped_column(Float, default=1000.0)
    default_leverage: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class PositionModel(Base):
    __tablename__ = "positions"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False) # LONG or SHORT
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    margin_usd: Mapped[float] = mapped_column(Float, nullable=False)
    leverage: Mapped[int] = mapped_column(Integer, default=1)
    order_type: Mapped[str] = mapped_column(String(32), default="MARKET")
    stop_loss_price: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit_price: Mapped[float] = mapped_column(Float, nullable=False)
    liquidation_price: Mapped[float] = mapped_column(Float, default=0.0)
    trailing_stop_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    entry_time: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    order_type: Mapped[str] = mapped_column(String(32), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING") # PENDING, FILLED, CANCELLED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class TradeModel(Base):
    __tablename__ = "trades"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    margin_usd: Mapped[float] = mapped_column(Float, nullable=False)
    pnl_usd: Mapped[float] = mapped_column(Float, nullable=False)
    pnl_pct: Mapped[float] = mapped_column(Float, nullable=False)
    entry_time: Mapped[str] = mapped_column(String(64), nullable=False)
    exit_time: Mapped[str] = mapped_column(String(64), nullable=False)
    close_reason: Mapped[str] = mapped_column(Text, default="")
    strategy: Mapped[str] = mapped_column(String(64), default="AI Hybrid")
    confidence: Mapped[float] = mapped_column(Float, default=75.0)
    reason: Mapped[str] = mapped_column(Text, default="")
    exchange: Mapped[str] = mapped_column(String(64), default="PAPER_EXCHANGE")
    order_id: Mapped[str] = mapped_column(String(128), default="")
    entry_fee: Mapped[float] = mapped_column(Float, default=0.0)
    exit_fee: Mapped[float] = mapped_column(Float, default=0.0)
    funding_fee: Mapped[float] = mapped_column(Float, default=0.0)
    slippage: Mapped[float] = mapped_column(Float, default=0.0)
    latency: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class SignalModel(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    technical_score: Mapped[float] = mapped_column(Float, nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    strategy: Mapped[str] = mapped_column(String(64), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class MarketCacheModel(Base):
    __tablename__ = "market_cache"

    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[float] = mapped_column(Float, default=time.time)

class MarketPriceModel(Base):
    __tablename__ = "market_prices"

    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class NewsModel(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    link: Mapped[str] = mapped_column(Text, default="")
    sentiment: Mapped[str] = mapped_column(String(32), default="Neutral")
    sentiment_score: Mapped[float] = mapped_column(Float, default=50.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class SentimentModel(Base):
    __tablename__ = "sentiment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fear_greed_score: Mapped[int] = mapped_column(Integer, default=50)
    fear_greed_label: Mapped[str] = mapped_column(String(32), default="Neutral")
    combined_score: Mapped[float] = mapped_column(Float, default=50.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class PerformanceModel(Base):
    __tablename__ = "performance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    total_portfolio_value: Mapped[float] = mapped_column(Float, nullable=False)
    total_pnl_usd: Mapped[float] = mapped_column(Float, nullable=False)
    win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class EquityHistoryModel(Base):
    __tablename__ = "equity_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    equity: Mapped[float] = mapped_column(Float, nullable=False)
    wallet: Mapped[float] = mapped_column(Float, nullable=False)
    margin: Mapped[float] = mapped_column(Float, nullable=False)
    unrealized_pnl: Mapped[float] = mapped_column(Float, nullable=False)
    realized_pnl: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class WalletTransactionModel(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    tx_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    tx_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    reference_id: Mapped[str] = mapped_column(String(128), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))



