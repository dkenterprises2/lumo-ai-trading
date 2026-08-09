from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class ExchangeAccountModel(Base):
    """Connected Live Exchange Accounts Table."""
    __tablename__ = "exchange_accounts_v24"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    exchange_name: Mapped[str] = mapped_column(String, nullable=False)
    api_key_masked: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ExchangeBalanceModel(Base):
    """Synced Live Exchange Balances Table."""
    __tablename__ = "exchange_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    exchange_name: Mapped[str] = mapped_column(String, nullable=False)
    asset: Mapped[str] = mapped_column(String, nullable=False)
    free_amount: Mapped[float] = mapped_column(Float, nullable=False)
    locked_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class LiveOrderModel(Base):
    """Live Exchange Orders Table."""
    __tablename__ = "live_orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    exchange_name: Mapped[str] = mapped_column(String, nullable=False)
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    side: Mapped[str] = mapped_column(String, nullable=False)
    order_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="OPEN")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class OrderFillModel(Base):
    """Live Order Fills Table."""
    __tablename__ = "order_fills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    fill_price: Mapped[float] = mapped_column(Float, nullable=False)
    fill_amount: Mapped[float] = mapped_column(Float, nullable=False)
    fee_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ExecutionReportModel(Base):
    """Execution Reports Audit Log Table."""
    __tablename__ = "execution_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    summary: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ReconciliationEventModel(Base):
    """Reconciliation Audit Events Table."""
    __tablename__ = "reconciliation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    matched_count: Mapped[int] = mapped_column(Integer, nullable=False)
    discrepancies: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ExchangeLatencyHistoryModel(Base):
    """API & WebSocket Response Latency Table."""
    __tablename__ = "exchange_latency_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exchange_name: Mapped[str] = mapped_column(String, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class SlippageHistoryModel(Base):
    """Slippage History Log Table."""
    __tablename__ = "slippage_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    slippage_bps: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class PositionSyncHistoryModel(Base):
    """Position Sync Audit Trail Table."""
    __tablename__ = "position_sync_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    converged: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())
