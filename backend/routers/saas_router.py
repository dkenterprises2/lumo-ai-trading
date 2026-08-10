import time
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.saas.organization_manager import organization_manager
from backend.saas.rbac import rbac_manager
from backend.saas.api_key_manager import api_key_manager
from backend.saas.usage_metering import usage_metering_engine
from backend.saas.rate_limiter import tenant_rate_limiter
from backend.saas.subscription_manager import subscription_manager
from backend.saas.billing_provider import billing_provider
from backend.saas.invoice_engine import invoice_engine
from backend.saas.payment_webhooks import payment_webhook_handler
from backend.saas.tenant_middleware import tenant_middleware
from backend.saas.branding_manager import branding_manager
from backend.saas.analytics import saas_analytics
from backend.saas.audit_logger import tenant_audit_logger

router = APIRouter(tags=["Multi-Tenant SaaS & Subscription Billing"])

@router.post("/api/orgs")
async def create_organization(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "New Enterprise Org")
    return organization_manager.create_organization(name, current_user.id)

@router.get("/api/orgs")
async def list_organizations(current_user: UserModel = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "organizations": organization_manager.list_organizations()
    }

@router.get("/api/orgs/{org_id}")
async def get_organization_by_id(org_id: str, current_user: UserModel = Depends(get_current_user)):
    return organization_manager.get_organization(org_id)

@router.patch("/api/orgs/{org_id}")
async def update_organization(org_id: str, body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    org = organization_manager.get_organization(org_id)
    if "name" in body:
        org["name"] = body["name"]
    return org

@router.post("/api/orgs/{org_id}/members")
async def add_organization_member(org_id: str, body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    email = body.get("email", "newmember@company.com")
    role = body.get("role", "TRADER")
    tenant_audit_logger.log_action(org_id, current_user.email, "MEMBER_ADDED", f"Added {email} as {role}")
    return {"status": "MEMBER_ADDED", "org_id": org_id, "email": email, "role": role}

@router.delete("/api/orgs/{org_id}/members/{member_id}")
async def remove_organization_member(org_id: str, member_id: str, current_user: UserModel = Depends(get_current_user)):
    tenant_audit_logger.log_action(org_id, current_user.email, "MEMBER_REMOVED", f"Removed member {member_id}")
    return {"status": "MEMBER_REMOVED", "org_id": org_id, "member_id": member_id}

@router.post("/api/orgs/{org_id}/invite")
async def invite_organization_member(org_id: str, body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    email = body.get("email", "invite@company.com")
    role = body.get("role", "TRADER")
    token = f"inv_tok_{int(time.time())}"
    tenant_audit_logger.log_action(org_id, current_user.email, "INVITATION_SENT", f"Invited {email}")
    return {"status": "INVITATION_SENT", "org_id": org_id, "email": email, "role": role, "invitation_token": token}

@router.post("/api/orgs/invitations/{token}/accept")
async def accept_organization_invitation(token: str, current_user: UserModel = Depends(get_current_user)):
    return {"status": "INVITATION_ACCEPTED", "user_id": current_user.id, "token": token}

@router.post("/api/orgs/{org_id}/api-keys")
async def create_tenant_api_key(org_id: str, body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "Default API Key")
    return api_key_manager.create_api_key(org_id, name)

@router.get("/api/orgs/{org_id}/api-keys")
async def list_tenant_api_keys(org_id: str, current_user: UserModel = Depends(get_current_user)):
    return {
        "org_id": org_id,
        "api_keys": api_key_manager.list_api_keys(org_id)
    }

@router.delete("/api/orgs/{org_id}/api-keys/{key_id}")
async def revoke_tenant_api_key(org_id: str, key_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"status": "KEY_REVOKED", "org_id": org_id, "key_id": key_id}

@router.get("/api/billing/plans")
async def list_billing_plans():
    return {"plans": subscription_manager.list_plans()}

@router.post("/api/billing/subscribe")
async def subscribe_organization(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    org_id = body.get("org_id", "ORG-101")
    plan_id = body.get("plan_id", "plan_pro")
    session = billing_provider.create_checkout_session(org_id, plan_id)
    sub = subscription_manager.subscribe_org(org_id, plan_id)
    return {"subscription": sub, "checkout": session}

@router.get("/api/billing/subscription")
async def get_current_subscription(org_id: str = Query("ORG-101"), current_user: UserModel = Depends(get_current_user)):
    return {
        "org_id": org_id,
        "plan": "Institutional Enterprise",
        "status": "ACTIVE",
        "seats_purchased": 25,
        "renewal_date": "2026-09-01 00:00:00 UTC"
    }

@router.get("/api/billing/invoices")
async def get_organization_invoices(org_id: str = Query("ORG-101"), current_user: UserModel = Depends(get_current_user)):
    return {
        "org_id": org_id,
        "invoices": invoice_engine.list_invoices(org_id)
    }

@router.post("/api/billing/webhooks/stripe")
async def stripe_billing_webhook(body: Dict[str, Any]):
    event_type = body.get("type", "payment_intent.succeeded")
    return payment_webhook_handler.process_webhook(event_type, body)

@router.get("/api/usage/summary")
async def get_usage_summary(org_id: str = Query("ORG-101"), current_user: UserModel = Depends(get_current_user)):
    return usage_metering_engine.get_usage_summary(org_id)

@router.get("/api/usage/history")
async def get_usage_history(org_id: str = Query("ORG-101"), current_user: UserModel = Depends(get_current_user)):
    return {
        "org_id": org_id,
        "history": [
            {"date": "2026-08-08", "api_requests": 1420, "active_bots": 4},
            {"date": "2026-08-07", "api_requests": 1380, "active_bots": 4}
        ]
    }

from backend.auth.admin_guard import require_super_admin

@router.get("/api/admin/tenants")
async def list_admin_tenants(admin: UserModel = Depends(require_super_admin)):
    return {"total_tenants": 48, "tenants": organization_manager.list_organizations()}

@router.get("/api/admin/revenue")
async def get_admin_revenue_metrics(admin: UserModel = Depends(require_super_admin)):
    return saas_analytics.get_revenue_metrics()

@router.get("/api/admin/platform-metrics")
async def get_admin_platform_metrics(admin: UserModel = Depends(require_super_admin)):
    return saas_analytics.get_platform_metrics()

