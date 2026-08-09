from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class BrokerModel(Base):
    """Brokers Table."""
    __tablename__ = "p23_brokers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    broker_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

class BrokerConnectionModel(Base):
    """Broker Connections Table."""
    __tablename__ = "broker_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conn_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class FIXSessionModel(Base):
    """FIX Sessions Table."""
    __tablename__ = "fix_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class FIXMessageModel(Base):
    """FIX Messages Table."""
    __tablename__ = "fix_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    msg_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class OMSOrderModel(Base):
    """OMS Orders Table."""
    __tablename__ = "oms_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String, nullable=False)

class OrderStateTransitionModel(Base):
    """Order State Transitions Table."""
    __tablename__ = "order_state_transitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trans_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class BasketOrderModel(Base):
    """Basket Orders Table."""
    __tablename__ = "basket_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    basket_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ChildOrderModel(Base):
    """Child Orders Table."""
    __tablename__ = "child_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    child_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExecutionReportModel(Base):
    """Execution Reports Table."""
    __tablename__ = "p23_execution_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AllocationModel(Base):
    """Allocations Table."""
    __tablename__ = "p23_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alloc_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class TradeBlotterEntryModel(Base):
    """Trade Blotter Entries Table."""
    __tablename__ = "trade_blotter_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entry_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class SORDecisionModel(Base):
    """SOR Decisions Table."""
    __tablename__ = "sor_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    decision_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class VenueSnapshotModel(Base):
    """Venue Snapshots Table."""
    __tablename__ = "venue_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snapshot_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExecutionAlgorithmModel(Base):
    """Execution Algorithms Table."""
    __tablename__ = "execution_algorithms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    algo_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class TCAReportModel(Base):
    """TCA Reports Table."""
    __tablename__ = "tca_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class SlippageRecordModel(Base):
    """Slippage Records Table."""
    __tablename__ = "slippage_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    record_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class VenueQualityScoreModel(Base):
    """Venue Quality Scores Table."""
    __tablename__ = "venue_quality_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RiskRejectionModel(Base):
    """Risk Rejections Table."""
    __tablename__ = "risk_rejections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rejection_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DropcopyEventModel(Base):
    """Dropcopy Events Table."""
    __tablename__ = "dropcopy_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ComplianceAlertModel(Base):
    """Compliance Alerts Table."""
    __tablename__ = "p23_compliance_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExecutionReplayEventModel(Base):
    """Execution Replay Events Table."""
    __tablename__ = "execution_replay_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class EnvironmentSwitchRequestModel(Base):
    """Environment Switch Requests Table."""
    __tablename__ = "environment_switch_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    req_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class LiveTradingApprovalModel(Base):
    """Live Trading Approvals Table."""
    __tablename__ = "live_trading_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    approval_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
