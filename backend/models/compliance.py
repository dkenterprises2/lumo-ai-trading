from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class AuditLedgerEntryModel(Base):
    """Immutable Audit Ledger Table."""
    __tablename__ = "audit_ledger_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entry_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    current_entry_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class PrivilegedAccessEventModel(Base):
    """Privileged Access Events Table."""
    __tablename__ = "privileged_access_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class APIAccessLogModel(Base):
    """API Access Logs Table."""
    __tablename__ = "api_access_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    log_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class ComplianceIncidentModel(Base):
    """Compliance Incidents Table."""
    __tablename__ = "compliance_incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="OPEN")

class SecurityIncidentModel(Base):
    """Security Incidents Table."""
    __tablename__ = "security_incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)

class TradeSurveillanceAlertModel(Base):
    """Trade Surveillance Alerts Table."""
    __tablename__ = "trade_surveillance_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String, nullable=False)

class SuspiciousActivityReportModel(Base):
    """Suspicious Activity Reports Table."""
    __tablename__ = "suspicious_activity_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DataRetentionPolicyModel(Base):
    """Data Retention Policies Table."""
    __tablename__ = "data_retention_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    data_category: Mapped[str] = mapped_column(String, nullable=False)

class ArchivedRecordModel(Base):
    """Archived Records Table."""
    __tablename__ = "archived_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    archive_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class RegulatoryReportModel(Base):
    """Regulatory Reports Table."""
    __tablename__ = "regulatory_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ComplianceExportModel(Base):
    """Compliance Exports Table."""
    __tablename__ = "compliance_exports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    export_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class EncryptionKeyVersionModel(Base):
    """Encryption Key Versions Table."""
    __tablename__ = "encryption_key_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    version_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class GovernancePolicyViolationModel(Base):
    """Governance Policy Violations Table."""
    __tablename__ = "governance_policy_violations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    violation_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class PenetrationTestEvidenceModel(Base):
    """Penetration Test Evidence Table."""
    __tablename__ = "penetration_test_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    evidence_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class UserConsentRecordModel(Base):
    """User Consent Records Table."""
    __tablename__ = "user_consent_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    consent_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class DataSubjectRequestModel(Base):
    """Data Subject Requests Table."""
    __tablename__ = "data_subject_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class ComplianceTaskModel(Base):
    """Compliance Tasks Table."""
    __tablename__ = "compliance_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
