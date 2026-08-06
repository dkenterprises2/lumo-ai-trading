from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class StrategyConfigModel(Base):
    """Strategy Registration and Configuration Table."""
    __tablename__ = "strategies"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    risk_level: Mapped[str] = mapped_column(String, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    parameters: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class StrategyRunModel(Base):
    """Strategy Run Execution Logs Table."""
    __tablename__ = "strategy_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    strategy_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)  # RUNNING, PAUSED, STOPPED, ERROR
    allocation_pct: Mapped[float] = mapped_column(Float, default=12.5)
    last_run_time: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class PortfolioAllocationModel(Base):
    """Smart Portfolio Capital Allocation Snapshots Table."""
    __tablename__ = "portfolio_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    portfolio_name: Mapped[str] = mapped_column(String, nullable=False)
    allocated_usd: Mapped[float] = mapped_column(Float, nullable=False)
    allocation_pct: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class StrategyMetricsModel(Base):
    """Strategy Performance Metrics Table."""
    __tablename__ = "strategy_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    strategy_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    sharpe_ratio: Mapped[float] = mapped_column(Float, default=1.5)
    sortino_ratio: Mapped[float] = mapped_column(Float, default=2.1)
    win_rate: Mapped[float] = mapped_column(Float, default=65.0)
    profit_factor: Mapped[float] = mapped_column(Float, default=1.8)
    total_pnl_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())
