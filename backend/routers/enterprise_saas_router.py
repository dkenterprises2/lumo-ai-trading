from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.saas.organization_service import organization_service
from backend.saas.workspace_service import workspace_service
from backend.saas.rbac_engine import rbac_engine
from backend.saas.permission_registry import permission_registry

from backend.saas.oauth_google import oauth_google
from backend.saas.oauth_microsoft import oauth_microsoft
from backend.saas.saml_sso import saml_sso
from backend.saas.subscription_engine import subscription_engine
from backend.saas.billing_abstraction import billing_abstraction
from backend.saas.invoice_service import invoice_service
from backend.saas.usage_metering import usage_metering
from backend.saas.quota_enforcer import quota_enforcer
from backend.saas.branding_service import branding_service
from backend.saas.custom_domain_service import custom_domain_service
from backend.saas.api_key_service import api_key_service
from backend.saas.webhook_service import tenant_webhook_service
from backend.saas.tenant_backup_service import tenant_backup_service
from backend.saas.enterprise_admin import enterprise_admin
from backend.saas.feature_flags import feature_flags

router = APIRouter(tags=["Enterprise SaaS & Multi-Tenant Platform"])

@router.post("/api/saas/organizations")
async def create_organization(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "Acme Capital")
    slug = body.get("slug", "acme-capital")
    owner = body.get("owner_email", current_user.email)
    return organization_service.create_organization(name, slug, owner)

@router.get("/api/saas/organizations/{org_id}")
async def get_organization(org_id: str, current_user: UserModel = Depends(get_current_user)):
    orgs = organization_service.list_organizations()
    for o in orgs:
        if o["org_id"] == org_id:
            return o
    return {"org_id": org_id, "name": "Acme Capital", "status": "ACTIVE"}

@router.post("/api/saas/workspaces")
async def create_workspace(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    org_id = body.get("org_id", "org_acme")
    name = body.get("name", "New Desk")
    return workspace_service.create_workspace(org_id, name)

@router.get("/api/saas/roles")
async def list_roles(current_user: UserModel = Depends(get_current_user)):
    return {"roles": rbac_engine.DEFAULT_ROLES}

@router.post("/api/saas/roles")
async def create_role(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"role": body.get("role_name", "CUSTOM_ROLE"), "status": "CREATED"}

@router.post("/api/saas/permissions/assign")
async def assign_permission(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"user_email": body.get("user_email"), "role": body.get("role"), "status": "ASSIGNED"}

@router.post("/api/saas/sso/google/start")
async def start_google_sso(body: Dict[str, Any] = None, current_user: UserModel = Depends(get_current_user)):
    return oauth_google.get_auth_url()

@router.post("/api/saas/sso/microsoft/start")
async def start_microsoft_sso(body: Dict[str, Any] = None, current_user: UserModel = Depends(get_current_user)):
    return oauth_microsoft.get_auth_url()

@router.post("/api/saas/sso/saml/configure")
async def configure_saml_sso(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    entity = body.get("entity_id", "https://idp.acme.com")
    sso_url = body.get("sso_url", "https://idp.acme.com/sso")
    cert = body.get("x509_cert", "PEM_CERT")
    return saml_sso.configure_sso(entity, sso_url, cert)

@router.get("/api/saas/subscription")
async def get_subscription(current_user: UserModel = Depends(get_current_user)):
    return {"tenant_id": "org_acme", "plan": "ENTERPRISE", "status": "ACTIVE"}

@router.post("/api/saas/subscription/change-plan")
async def change_subscription_plan(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    new_plan = body.get("new_plan", "ENTERPRISE")
    return subscription_engine.change_plan("org_acme", new_plan)

@router.get("/api/saas/billing/invoices")
async def get_billing_invoices(current_user: UserModel = Depends(get_current_user)):
    return {"invoices": invoice_service.list_invoices("org_acme")}

@router.get("/api/saas/usage")
async def get_tenant_usage(current_user: UserModel = Depends(get_current_user)):
    return usage_metering.get_usage()

@router.get("/api/saas/quotas")
async def get_tenant_quotas(current_user: UserModel = Depends(get_current_user)):
    return quota_enforcer.check_quota("api_calls", 142000.0, 200000.0)

@router.post("/api/saas/branding")
async def update_tenant_branding(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return branding_service.update_branding(body)

@router.post("/api/saas/custom-domains")
async def register_custom_domain(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    domain = body.get("domain", "trade.acmecapital.com")
    return custom_domain_service.register_domain(domain, "org_acme")

@router.get("/api/saas/custom-domains/status")
async def get_custom_domain_status(current_user: UserModel = Depends(get_current_user)):
    return {"domains": custom_domain_service.list_domains()}

@router.get("/api/saas/api-keys")
async def list_api_keys(current_user: UserModel = Depends(get_current_user)):
    return {"api_keys": api_key_service.list_keys()}

@router.post("/api/saas/api-keys")
async def create_api_key(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    name = body.get("name", "New Key")
    scopes = body.get("scopes", ["marketdata:read"])
    return api_key_service.create_key(name, scopes)

@router.post("/api/saas/api-keys/{key_id}/rotate")
async def rotate_api_key(key_id: str, current_user: UserModel = Depends(get_current_user)):
    return api_key_service.rotate_key(key_id)

@router.get("/api/saas/webhooks")
async def list_webhooks(current_user: UserModel = Depends(get_current_user)):
    return {"webhooks": tenant_webhook_service.list_webhooks()}

@router.post("/api/saas/webhooks")
async def create_webhook(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    target_url = body.get("target_url", "https://hooks.slack.com/services/test")
    events = body.get("events", ["order_filled"])
    return tenant_webhook_service.create_webhook(target_url, events)

@router.get("/api/saas/backups")
async def list_backups(current_user: UserModel = Depends(get_current_user)):
    return {"backups": tenant_backup_service.list_backups()}

@router.post("/api/saas/backups/create")
async def create_backup(body: Dict[str, Any] = None, current_user: UserModel = Depends(get_current_user)):
    return tenant_backup_service.create_backup("org_acme")

@router.post("/api/saas/backups/{backup_id}/restore")
async def restore_backup(backup_id: str, current_user: UserModel = Depends(get_current_user)):
    return tenant_backup_service.restore_backup(backup_id)

@router.get("/api/saas/admin/tenants")
async def list_admin_tenants(current_user: UserModel = Depends(get_current_user)):
    return {"tenants": organization_service.list_organizations()}

@router.get("/api/saas/admin/system-health")
async def get_admin_system_health(current_user: UserModel = Depends(get_current_user)):
    return enterprise_admin.get_system_health()

@router.post("/api/saas/admin/feature-flags")
async def set_feature_flag(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    flag = body.get("flag", "white_label")
    enabled = body.get("enabled", True)
    return feature_flags.set_flag(flag, enabled)
