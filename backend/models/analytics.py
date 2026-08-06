from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class AnalyticsSnapshotModel(Base):
    """Institutional Analytics Daily/Intraday Snapshots Table."""
    __tablename__ = "analytics_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    equity_usd: Mapped[float] = mapped_column(Float, nullable=False)
    drawdown_pct: Mapped[float] = mapped_column(Float, default=0.0)
    sharpe_ratio: Mapped[float] = mapped_column(Float, default=1.5)
    sortino_ratio: Mapped[float] = mapped_column(Float, default=2.1)
    snapshot_date: Mapped[str] = mapped_column(String, index=True, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class PerformanceHistoryModel(Base):
    """Historical Performance Track Record Table."""
    __tablename__ = "performance_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    period: Mapped[str] = mapped_column(String, nullable=False)  # DAILY, WEEKLY, MONTHLY
    return_pct: Mapped[float] = mapped_column(Float, nullable=False)
    net_pnl_usd: Mapped[float] = mapped_column(Float, nullable=False)
    win_rate: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class RiskHistoryModel(Base):
    """Historical Risk Exposures & Value-at-Risk Table."""
    __tablename__ = "risk_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    var_95_usd: Mapped[float] = mapped_column(Float, nullable=False)
    cvar_95_usd: Mapped[float] = mapped_column(Float, nullable=False)
    leverage_used: Mapped[float] = mapped_column(Float, default=1.0)
    margin_utilization_pct: Mapped[float] = mapped_column(Float, default=15.0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class DailyReportModel(Base):
    """Persisted Daily Institutional Reports Table."""
    __tablename__ = "daily_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    report_date: Mapped[str] = mapped_column(String, index=True, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class MonthlyReportModel(Base):
    """Persisted Monthly Institutional Reports Table."""
    __tablename__ = "monthly_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    report_month: Mapped[str] = mapped_column(String, index=True, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())
