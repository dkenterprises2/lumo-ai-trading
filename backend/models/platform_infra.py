from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class ClusterDeploymentModel(Base):
    """Cluster Deployments Table."""
    __tablename__ = "cluster_deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deploy_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    app: Mapped[str] = mapped_column(String, nullable=False)

class CanaryRolloutModel(Base):
    """Canary Rollouts Table."""
    __tablename__ = "canary_rollouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rollout_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class GitOpsSyncStateModel(Base):
    """GitOps Sync States Table."""
    __tablename__ = "gitops_sync_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    app_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ServiceMeshRouteModel(Base):
    """Service Mesh Routes Table."""
    __tablename__ = "service_mesh_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    route_name: Mapped[str] = mapped_column(String, nullable=False)

class SecretRotationModel(Base):
    """Secret Rotations Table."""
    __tablename__ = "secret_rotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    secret_path: Mapped[str] = mapped_column(String, nullable=False)

class ObservabilityAlertModel(Base):
    """Observability Alerts Table."""
    __tablename__ = "observability_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_name: Mapped[str] = mapped_column(String, nullable=False)

class SREIncidentModel(Base):
    """SRE Incidents Table."""
    __tablename__ = "sre_incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class SLOTargetModel(Base):
    """SLO Targets Table."""
    __tablename__ = "slo_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ChaosExperimentModel(Base):
    """Chaos Experiments Table."""
    __tablename__ = "chaos_experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experiment_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class SupplyChainScanModel(Base):
    """Supply Chain Scans Table."""
    __tablename__ = "supply_chain_scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_tag: Mapped[str] = mapped_column(String, index=True, nullable=False)

class DRRunbookExecutionModel(Base):
    """DR Runbook Executions Table."""
    __tablename__ = "dr_runbook_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    execution_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
