from typing import Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.session import Base

class SystemAlertModel(Base):
    """System Alerts Table."""
    __tablename__ = "system_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_code: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    component: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="FIRING")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class HealthCheckLogModel(Base):
    """Health Check Log Table."""
    __tablename__ = "health_check_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    overall_status: Mapped[str] = mapped_column(String, nullable=False)
    subsystem_details: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

class BackupSnapshotModel(Base):
    """Backup Snapshot Log Table."""
    __tablename__ = "backup_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    backup_id: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    size_mb: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="COMPLETED")
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())
