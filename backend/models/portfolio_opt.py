from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class PortfolioAllocationModel(Base):
    """Portfolio Strategy Allocations Table."""
    __tablename__ = "portfolio_allocations_v23"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    strategy_id: Mapped[str] = mapped_column(String, nullable=False)
    weight_pct: Mapped[float] = mapped_column(Float, nullable=False)
    allocated_usd: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class PortfolioOptimizationModel(Base):
    """Portfolio Optimization Runs Table."""
    __tablename__ = "portfolio_optimizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    model_type: Mapped[str] = mapped_column(String, nullable=False)  # MEAN_VARIANCE, RISK_PARITY, BLACK_LITTERMAN
    expected_return_pct: Mapped[float] = mapped_column(Float, nullable=False)
    expected_volatility_pct: Mapped[float] = mapped_column(Float, nullable=False)
    sharpe_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    weights_json: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class RebalanceHistoryModel(Base):
    """Portfolio Rebalance Audit Log Table."""
    __tablename__ = "rebalance_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    target_weights: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class StressTestResultModel(Base):
    """Stress Test Runs Table."""
    __tablename__ = "stress_test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    scenarios_evaluated: Mapped[int] = mapped_column(Integer, nullable=False)
    resilience_score: Mapped[float] = mapped_column(Float, nullable=False)
    results_json: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ScenarioAnalysisResultModel(Base):
    """Scenario Analysis Runs Table."""
    __tablename__ = "scenario_analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    correlation_matrix: Mapped[dict] = mapped_column(JSON, default={})
    exposure_summary: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class PortfolioConstraintModel(Base):
    """Portfolio Exposure Limits & Constraints Table."""
    __tablename__ = "portfolio_constraints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    max_strategy_exposure_pct: Mapped[float] = mapped_column(Float, default=30.0)
    max_sector_exposure_pct: Mapped[float] = mapped_column(Float, default=50.0)
    min_cash_reserve_pct: Mapped[float] = mapped_column(Float, default=10.0)
    max_leverage: Mapped[float] = mapped_column(Float, default=2.0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class StrategyExposureHistoryModel(Base):
    """Historical Strategy Exposure Snapshots Table."""
    __tablename__ = "strategy_exposure_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    strategy_id: Mapped[str] = mapped_column(String, nullable=False)
    exposure_usd: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())
