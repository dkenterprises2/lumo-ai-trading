from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.admin.tenant_admin import tenant_admin_console
from backend.admin.platform_admin import platform_admin_console
from backend.admin.revenue_analytics import platform_revenue_analytics
from backend.admin.system_monitor import platform_system_monitor
from backend.admin.security_monitor import security_monitor_console
from backend.admin.backup_console import backup_console_manager
from backend.saas.organization_manager import organization_manager

router = APIRouter(tags=["Super Admin Platform Administration"])

def verify_super_admin(current_user: UserModel = Depends(get_current_user)):
    """Security requirement: Enforce SUPER_ADMIN role checks."""
    # jiodkd@gmail.com is registered as main platform super admin
    if current_user.email != "jiodkd@gmail.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Platform Super Admin privileges required"
        )
    return current_user

@router.get("/api/admin/tenants")
async def list_admin_tenants(admin: UserModel = Depends(verify_super_admin)):
    return {
        "tenants": organization_manager.list_organizations()
    }

@router.get("/api/admin/tenants/{tenant_id}")
async def get_admin_tenant(tenant_id: str, admin: UserModel = Depends(verify_super_admin)):
    return organization_manager.get_organization(tenant_id)

@router.patch("/api/admin/tenants/{tenant_id}/suspend")
async def suspend_tenant(tenant_id: str, admin: UserModel = Depends(verify_super_admin)):
    return tenant_admin_console.suspend_tenant(tenant_id)

@router.patch("/api/admin/tenants/{tenant_id}/activate")
async def activate_tenant(tenant_id: str, admin: UserModel = Depends(verify_super_admin)):
    return tenant_admin_console.activate_tenant(tenant_id)

@router.get("/api/admin/users")
async def list_platform_users(admin: UserModel = Depends(verify_super_admin)):
    return {"users": tenant_admin_console.list_users()}

@router.get("/api/admin/revenue")
async def get_platform_revenue(admin: UserModel = Depends(verify_super_admin)):
    return platform_revenue_analytics.get_revenue_summary()

@router.get("/api/admin/platform-metrics")
async def get_platform_metrics(admin: UserModel = Depends(verify_super_admin)):
    return platform_admin_console.get_platform_metrics()

@router.get("/api/admin/system-health")
async def get_system_health(admin: UserModel = Depends(verify_super_admin)):
    return platform_system_monitor.get_system_health()

@router.get("/api/admin/security/events")
async def get_security_events(admin: UserModel = Depends(verify_super_admin)):
    return {"events": security_monitor_console.list_security_events()}

@router.get("/api/admin/backups")
async def get_platform_backups(admin: UserModel = Depends(verify_super_admin)):
    return {"backups": backup_console_manager.list_backups()}

@router.post("/api/admin/backups/create")
async def create_platform_backup(admin: UserModel = Depends(verify_super_admin)):
    return backup_console_manager.create_backup()

@router.post("/api/admin/backups/restore")
async def restore_platform_backup(body: Dict[str, Any], admin: UserModel = Depends(verify_super_admin)):
    snapshot_id = body.get("snapshot_id", "SNAP-101")
    return backup_console_manager.restore_backup(snapshot_id)
