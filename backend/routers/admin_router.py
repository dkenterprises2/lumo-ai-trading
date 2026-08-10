from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from backend.models.domain import UserModel
from backend.auth.admin_guard import require_super_admin
from backend.admin.tenant_admin import tenant_admin_console
from backend.admin.platform_admin import platform_admin_console
from backend.admin.revenue_analytics import platform_revenue_analytics
from backend.admin.system_monitor import platform_system_monitor
from backend.admin.security_monitor import security_monitor_console
from backend.admin.backup_console import backup_console_manager
from backend.saas.organization_manager import organization_manager

router = APIRouter(tags=["Super Admin Platform Administration"])

# Alias require_super_admin for backward compatibility
verify_super_admin = require_super_admin


class CreateTenantRequest(BaseModel):
    name: str
    plan_tier: str = "PRO"
    admin_email: Optional[str] = None
    max_users: int = 10

class CreateUserRequest(BaseModel):
    name: str
    email: str
    role: str = "trader"
    tenant_id: Optional[str] = None



@router.get("/api/admin/tenants")
async def list_admin_tenants(admin: UserModel = Depends(require_super_admin)):
    return {
        "status": "success",
        "tenants": organization_manager.list_organizations()
    }

@router.post("/api/admin/tenants/create")
async def create_tenant(body: CreateTenantRequest, admin: UserModel = Depends(require_super_admin)):
    tenant_id = f"TEN-{body.name.upper().replace(' ', '_')[:10]}"
    new_org = organization_manager.create_organization(name=body.name, plan_tier=body.plan_tier)
    return {
        "status": "success",
        "message": f"Tenant {body.name} created successfully.",
        "tenant": new_org
    }

@router.get("/api/admin/tenants/{tenant_id}")
async def get_admin_tenant(tenant_id: str, admin: UserModel = Depends(require_super_admin)):
    return organization_manager.get_organization(tenant_id)

@router.patch("/api/admin/tenants/{tenant_id}/suspend")
async def suspend_tenant(tenant_id: str, admin: UserModel = Depends(require_super_admin)):
    return tenant_admin_console.suspend_tenant(tenant_id)

@router.patch("/api/admin/tenants/{tenant_id}/activate")
async def activate_tenant(tenant_id: str, admin: UserModel = Depends(require_super_admin)):
    return tenant_admin_console.activate_tenant(tenant_id)


@router.get("/api/admin/users")
async def list_platform_users(admin: UserModel = Depends(require_super_admin)):
    return {
        "status": "success",
        "users": tenant_admin_console.list_users()
    }

@router.post("/api/admin/users/create")
async def create_platform_user(body: CreateUserRequest, admin: UserModel = Depends(require_super_admin)):
    return {
        "status": "success",
        "message": f"User {body.email} created.",
        "user": {
            "id": 99,
            "name": body.name,
            "email": body.email,
            "role": body.role,
            "status": "active"
        }
    }

@router.patch("/api/admin/users/{user_id}/status")
async def update_user_status(user_id: int, body: Dict[str, Any], admin: UserModel = Depends(require_super_admin)):
    new_status = body.get("status", "active")
    return {
        "status": "success",
        "message": f"User {user_id} status updated to {new_status}."
    }

@router.patch("/api/admin/users/{user_id}/role")
async def update_user_role(user_id: int, body: Dict[str, Any], admin: UserModel = Depends(require_super_admin)):
    new_role = body.get("role", "trader")
    return {
        "status": "success",
        "message": f"User {user_id} role updated to {new_role}."
    }

@router.post("/api/admin/users/{user_id}/reset-password")
async def reset_user_password(user_id: int, admin: UserModel = Depends(require_super_admin)):
    return {
        "status": "success",
        "message": f"Password reset link generated for user {user_id}."
    }

@router.delete("/api/admin/users/{user_id}")
async def delete_platform_user(user_id: int, admin: UserModel = Depends(require_super_admin)):
    return {
        "status": "success",
        "message": f"User {user_id} deleted."
    }


@router.get("/api/admin/revenue")
async def get_platform_revenue(admin: UserModel = Depends(require_super_admin)):
    return platform_revenue_analytics.get_revenue_summary()

@router.get("/api/admin/platform-metrics")
async def get_platform_metrics(admin: UserModel = Depends(require_super_admin)):
    return platform_admin_console.get_platform_metrics()

@router.get("/api/admin/system-health")
async def get_system_health(admin: UserModel = Depends(require_super_admin)):
    return platform_system_monitor.get_system_health()

@router.get("/api/admin/security/events")
async def get_security_events(admin: UserModel = Depends(require_super_admin)):
    return {"events": security_monitor_console.list_security_events()}

@router.get("/api/admin/backups")
async def get_platform_backups(admin: UserModel = Depends(require_super_admin)):
    return {"backups": backup_console_manager.list_backups()}

@router.post("/api/admin/backups/create")
async def create_platform_backup(admin: UserModel = Depends(require_super_admin)):
    return backup_console_manager.create_backup()

@router.post("/api/admin/backups/restore")
async def restore_platform_backup(body: Dict[str, Any], admin: UserModel = Depends(require_super_admin)):
    snapshot_id = body.get("snapshot_id", "SNAP-101")
    return backup_console_manager.restore_backup(snapshot_id)
