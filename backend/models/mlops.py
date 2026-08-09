from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class MLExperimentModel(Base):
    """MLOps Experiments Table."""
    __tablename__ = "ml_experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experiment_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class MLRunModel(Base):
    """MLOps Runs Table."""
    __tablename__ = "ml_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    experiment_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, default={})
    params: Mapped[dict] = mapped_column(JSON, default={})
    logged_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class FeatureStoreVersionModel(Base):
    """Feature Store Versions Table."""
    __tablename__ = "feature_store_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feature_set_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    features: Mapped[dict] = mapped_column(JSON, default=[])
    version: Mapped[str] = mapped_column(String, nullable=False)
    is_immutable: Mapped[bool] = mapped_column(Boolean, default=True)
    registered_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class FeatureStatisticsModel(Base):
    """Feature Statistics Table."""
    __tablename__ = "feature_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feature_name: Mapped[str] = mapped_column(String, nullable=False)
    mean_val: Mapped[float] = mapped_column(Float, default=0.0)
    std_val: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ModelRegistryVersionModel(Base):
    """Model Registry Versions Table."""
    __tablename__ = "model_registry_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    stage: Mapped[str] = mapped_column(String, default="STAGING")
    registered_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ModelDeploymentModel(Base):
    """Model Deployments Table."""
    __tablename__ = "model_deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    deployment_type: Mapped[str] = mapped_column(String, default="PRODUCTION")
    traffic_pct: Mapped[float] = mapped_column(Float, default=100.0)
    deployed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ModelDriftEventModel(Base):
    """Model Drift Events Table."""
    __tablename__ = "model_drift_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    psi_score: Mapped[float] = mapped_column(Float, nullable=False)
    drift_status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class DataQualityReportModel(Base):
    """Data Quality Reports Table."""
    __tablename__ = "data_quality_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    overall_quality: Mapped[str] = mapped_column(String, default="PASSED")
    null_value_pct: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class RetrainingJobModel(Base):
    """Retraining Jobs Table."""
    __tablename__ = "retraining_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    trigger_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="IN_PROGRESS")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class AIAuditLogModel(Base):
    """AI Audit Logs Table."""
    __tablename__ = "ai_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    audit_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    model_id: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    approver: Mapped[str] = mapped_column(String, default="System")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class InferencePerformanceHistoryModel(Base):
    """Inference Performance History Table."""
    __tablename__ = "inference_performance_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    avg_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    qps: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ShadowModelResultModel(Base):
    """Shadow Model Results Table."""
    __tablename__ = "shadow_model_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_model_id: Mapped[str] = mapped_column(String, nullable=False)
    predictions_matched: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())
