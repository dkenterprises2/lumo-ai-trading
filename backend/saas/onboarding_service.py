from typing import Dict, Any

class TenantOnboardingService:
    """Tenant Self-Service Onboarding & Provisioning Workflow."""

    @staticmethod
    def provision_tenant(org_name: str, admin_email: str, plan: str = "ENTERPRISE") -> Dict[str, Any]:
        slug = org_name.lower().replace(" ", "-")
        return {
            "tenant_id": f"org_{slug}",
            "organization_name": org_name,
            "slug": slug,
            "admin_email": admin_email,
            "plan": plan,
            "default_workspace": "ws_trading",
            "status": "PROVISIONED"
        }

onboarding_service = TenantOnboardingService()
