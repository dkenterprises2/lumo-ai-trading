from typing import Dict, Any, List

class TenantContext:
    """Strict Tenant Context Model & Resolution Engine."""

    def __init__(self, tenant_id: str = "org_demo", organization_slug: str = "lumo-demo", workspace_id: str = "ws_default", plan: str = "ENTERPRISE", user_role: str = "ADMIN"):
        self.tenant_id = tenant_id
        self.organization_slug = organization_slug
        self.workspace_id = workspace_id
        self.plan = plan
        self.feature_flags: List[str] = ["ai_trading", "multiasset", "white_label", "saml_sso"]
        self.user_role = user_role

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "organization_slug": self.organization_slug,
            "workspace_id": self.workspace_id,
            "plan": self.plan,
            "feature_flags": self.feature_flags,
            "user_role": self.user_role
        }

current_tenant_context = TenantContext()
