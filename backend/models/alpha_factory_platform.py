from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class MarketplaceStrategyModel(Base):
    """Marketplace Strategies Table."""
    __tablename__ = "marketplace_strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

class StrategyVersionModel(Base):
    """Strategy Versions Table."""
    __tablename__ = "strategy_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class StrategyReviewModel(Base):
    """Strategy Reviews Table."""
    __tablename__ = "strategy_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    review_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class StrategyReputationScoreModel(Base):
    """Strategy Reputation Scores Table."""
    __tablename__ = "strategy_reputation_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AutoMLSearchSpaceModel(Base):
    """AutoML Search Spaces Table."""
    __tablename__ = "automl_search_spaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    space_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AutoMLTrialModel(Base):
    """AutoML Trials Table."""
    __tablename__ = "automl_trials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trial_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class GeneticPopulationModel(Base):
    """Genetic Populations Table."""
    __tablename__ = "genetic_populations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    population_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class GeneticGenerationModel(Base):
    """Genetic Generations Table."""
    __tablename__ = "genetic_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gen_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class BayesianOptimizationRunModel(Base):
    """Bayesian Optimization Runs Table."""
    __tablename__ = "bayesian_optimization_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class OptimizationTrialModel(Base):
    """Optimization Trials Table."""
    __tablename__ = "optimization_trials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trial_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ValidationReportModel(Base):
    """Validation Reports Table."""
    __tablename__ = "validation_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RobustnessScoreModel(Base):
    """Robustness Scores Table."""
    __tablename__ = "robustness_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class EnsembleDefinitionModel(Base):
    """Ensemble Definitions Table."""
    __tablename__ = "ensemble_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ensemble_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class MetaLearningPolicyModel(Base):
    """Meta Learning Policies Table."""
    __tablename__ = "meta_learning_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    policy_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AlphaCandidateModel(Base):
    """Alpha Candidates Table (P22)."""
    __tablename__ = "p22_alpha_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AlphaCertificationModel(Base):
    """Alpha Certifications Table."""
    __tablename__ = "alpha_certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cert_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class PromotionPipelineRunModel(Base):
    """Promotion Pipeline Runs Table."""
    __tablename__ = "promotion_pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DriftAlertModel(Base):
    """Drift Alerts Table."""
    __tablename__ = "drift_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class StrategyRetirementModel(Base):
    """Strategy Retirements Table."""
    __tablename__ = "strategy_retirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    retire_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class AlphaLineageNodeModel(Base):
    """Alpha Lineage Nodes Table."""
    __tablename__ = "alpha_lineage_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    node_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ProvenanceEdgeModel(Base):
    """Provenance Edges Table."""
    __tablename__ = "provenance_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    edge_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class MarketplaceLicenseModel(Base):
    """Marketplace Licenses Table."""
    __tablename__ = "marketplace_licenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    license_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RevenueSharingRecordModel(Base):
    """Revenue Sharing Records Table."""
    __tablename__ = "revenue_sharing_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    record_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
