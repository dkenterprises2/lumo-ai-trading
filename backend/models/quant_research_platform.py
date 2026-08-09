from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class ResearchDatasetModel(Base):
    """Research Datasets Table."""
    __tablename__ = "research_datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

class DatasetSnapshotModel(Base):
    """Dataset Snapshots Table."""
    __tablename__ = "dataset_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snapshot_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DatasetLineageEdgeModel(Base):
    """Dataset Lineage Edges Table."""
    __tablename__ = "dataset_lineage_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    edge_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class FeatureDefinitionModel(Base):
    """Feature Definitions Table."""
    __tablename__ = "feature_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feature_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class FeatureVersionModel(Base):
    """Feature Versions Table."""
    __tablename__ = "feature_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class FeatureMaterializationModel(Base):
    """Feature Materializations Table."""
    __tablename__ = "feature_materializations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mat_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class FactorDefinitionModel(Base):
    """Factor Definitions Table."""
    __tablename__ = "factor_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    factor_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class FactorRunModel(Base):
    """Factor Runs Table."""
    __tablename__ = "factor_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ResearchExperimentModel(Base):
    """Research Experiments Table."""
    __tablename__ = "research_experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experiment_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExperimentRunModel(Base):
    """Experiment Runs Table."""
    __tablename__ = "experiment_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExperimentMetricModel(Base):
    """Experiment Metrics Table."""
    __tablename__ = "experiment_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    metric_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ExperimentArtifactModel(Base):
    """Experiment Artifacts Table."""
    __tablename__ = "experiment_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    artifact_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class NotebookWorkspaceModel(Base):
    """Notebook Workspaces Table."""
    __tablename__ = "notebook_workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workspace_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class NotebookSessionModel(Base):
    """Notebook Sessions Table."""
    __tablename__ = "notebook_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class CollaborationCommentModel(Base):
    """Collaboration Comments Table."""
    __tablename__ = "collaboration_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ComputeJobModel(Base):
    """Compute Jobs Table."""
    __tablename__ = "compute_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ComputeJobRunModel(Base):
    """Compute Job Runs Table."""
    __tablename__ = "compute_job_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_run_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AlternativeDataSourceModel(Base):
    """Alternative Data Sources Table."""
    __tablename__ = "alternative_data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DataQualityAlertModel(Base):
    """Data Quality Alerts Table."""
    __tablename__ = "data_quality_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ResearchApprovalModel(Base):
    """Research Approvals Table."""
    __tablename__ = "research_approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    approval_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AlphaCandidateModel(Base):
    """Alpha Candidates Table."""
    __tablename__ = "alpha_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alpha_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AlphaValidationResultModel(Base):
    """Alpha Validation Results Table."""
    __tablename__ = "alpha_validation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    result_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ReproducibilitySnapshotModel(Base):
    """Reproducibility Snapshots Table."""
    __tablename__ = "reproducibility_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snapshot_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
