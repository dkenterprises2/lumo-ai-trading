import time
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Response, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.observability.metrics import metrics_exporter
from backend.observability.health import health_aggregator
from backend.observability.alerts import alert_engine
from backend.observability.tracing import opentelemetry_tracer
from backend.infrastructure.backup_manager import backup_manager
from backend.infrastructure.disaster_recovery import disaster_recovery_manager
from backend.infrastructure.redis_streams import redis_streams_manager
from backend.infrastructure.postgres_migration import postgres_migration_layer

router = APIRouter(tags=["Observability, Health & System Management"])

from backend.auth.admin_guard import require_super_admin

@router.get("/health")
async def liveness_probe():
    """Liveness probe endpoint for Kubernetes / Docker Compose."""
    return health_aggregator.get_liveness_status()

@router.get("/ready")
async def readiness_probe():
    """Readiness probe endpoint for Kubernetes / Docker Compose."""
    return health_aggregator.get_readiness_status()

@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics scrape endpoint."""
    content = metrics_exporter.generate_prometheus_metrics()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")

@router.get("/api/system/status")
async def get_system_status(admin: UserModel = Depends(require_super_admin)):
    """Return complete system component status."""
    return health_aggregator.get_full_system_status()

@router.get("/api/system/alerts")
async def get_system_alerts(admin: UserModel = Depends(require_super_admin)):
    """Return active system alerts."""
    return {
        "user_id": admin.id,
        "alerts": alert_engine.get_active_alerts(),
        "total_active": len(alert_engine.get_active_alerts())
    }

@router.get("/api/system/observability")
async def get_system_observability_summary(admin: UserModel = Depends(require_super_admin)):
    """Return aggregated metrics, Redis Pub/Sub status, & database engine info."""
    return {
        "user_id": admin.id,
        "tracing": opentelemetry_tracer.start_span("api_observability_request"),
        "redis_cluster": redis_streams_manager.get_cluster_status(),
        "database": postgres_migration_layer.get_database_status(),
        "prom_metrics_sample": {
            "http_requests_total": metrics_exporter.request_count,
            "errors_total": metrics_exporter.error_count,
            "active_websockets": metrics_exporter.active_websockets
        }
    }

@router.post("/api/system/backup")
async def trigger_manual_backup(admin: UserModel = Depends(require_super_admin)):
    """Trigger manual database snapshot backup."""
    snapshot = backup_manager.create_backup()
    return {
        "status": "BACKUP_CREATED",
        "user_id": admin.id,
        "backup": snapshot
    }

@router.post("/api/system/recovery-test")
async def run_disaster_recovery_test(admin: UserModel = Depends(require_super_admin)):
    """Execute automated disaster recovery test."""
    return disaster_recovery_manager.execute_recovery_test()

