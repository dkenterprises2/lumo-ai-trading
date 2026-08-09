from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class AIAgentModel(Base):
    """AI Agents Table."""
    __tablename__ = "ai_agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agent_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="ACTIVE")

class AIAgentVersionModel(Base):
    """AI Agent Versions Table."""
    __tablename__ = "ai_agent_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AITrainingRunModel(Base):
    """AI Training Runs Table."""
    __tablename__ = "ai_training_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AITrainingMetricModel(Base):
    """AI Training Metrics Table."""
    __tablename__ = "ai_training_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

class AIExperienceBatchModel(Base):
    """AI Experience Batches Table."""
    __tablename__ = "ai_experience_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIShadowTradeModel(Base):
    """AI Shadow Trades Table."""
    __tablename__ = "ai_shadow_trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trade_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIPolicyDecisionModel(Base):
    """AI Policy Decisions Table."""
    __tablename__ = "ai_policy_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    decision_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIRewardProfileModel(Base):
    """AI Reward Profiles Table."""
    __tablename__ = "ai_reward_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIGovernanceApprovalModel(Base):
    """AI Governance Approvals Table."""
    __tablename__ = "ai_governance_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version_id: Mapped[str] = mapped_column(String, nullable=False)

class AIExplainabilityRecordModel(Base):
    """AI Explainability Records Table."""
    __tablename__ = "ai_explainability_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    decision_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AISafetyEventModel(Base):
    """AI Safety Events Table."""
    __tablename__ = "ai_safety_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIKillSwitchEventModel(Base):
    """AI Kill-Switch Events Table."""
    __tablename__ = "ai_kill_switch_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reason: Mapped[str] = mapped_column(String, nullable=False)

class AIDistributedTrainingJobModel(Base):
    """AI Distributed Training Jobs Table."""
    __tablename__ = "ai_distributed_training_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AIModelRegistryEntryModel(Base):
    """AI Model Registry Entries Table."""
    __tablename__ = "ai_model_registry_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
