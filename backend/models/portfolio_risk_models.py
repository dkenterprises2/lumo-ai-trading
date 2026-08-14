import time
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.session import Base

class PortfolioRiskStateModel(Base):
    """SQLAlchemy model for portfolio risk states."""
    __tablename__ = "portfolio_risk_states"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    equity = Column(Float, default=10000.0)
    available_balance = Column(Float, default=10000.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl_today = Column(Float, default=0.0)
    drawdown_pct = Column(Float, default=0.0)
    volatility_regime = Column(String(32), default="NORMAL")
    market_regime = Column(String(32), default="BULL")
    open_positions = Column(Integer, default=0)
    configured_max_positions = Column(Integer, default=10)
    dynamic_max_positions = Column(Integer, default=10)
    effective_max_positions = Column(Integer, default=10)
    portfolio_heat_pct = Column(Float, default=0.0)
    correlation_risk_score = Column(Float, default=0.0)
    concentration_risk_score = Column(Float, default=0.0)
    leverage_used = Column(Float, default=1.0)
    recommended_max_leverage = Column(Float, default=2.0)
    risk_budget_remaining_pct = Column(Float, default=5.0)
    risk_score = Column(Float, default=0.0)
    overall_status = Column(String(32), default="HEALTHY")
    created_at = Column(DateTime, default=time.time)
    metadata_json = Column(JSON, nullable=True)

class PortfolioKillSwitchEventModel(Base):
    """SQLAlchemy model for kill-switch events audit log."""
    __tablename__ = "portfolio_kill_switch_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    event_type = Column(String(64), nullable=False) # ACTIVATED, RECOVERED
    state = Column(String(32), nullable=False) # HALTED, NORMAL
    reason = Column(Text, nullable=True)
    triggered_by = Column(String(64), nullable=True)
    timestamp = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=time.time)
