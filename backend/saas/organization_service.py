from typing import Dict, Any, List

class OrganizationService:
    """Enterprise Organization & Hierarchy Service."""

    def __init__(self):
        self._organizations: List[Dict[str, Any]] = [
            {
                "org_id": "org_acme",
                "name": "Acme Capital Management",
                "slug": "acme-capital",
                "plan": "ENTERPRISE",
                "owner_email": "owner@acme.com",
                "status": "ACTIVE"
            }
        ]

    def list_organizations(self) -> List[Dict[str, Any]]:
        return self._organizations

    def create_organization(self, name: str, slug: str, owner_email: str) -> Dict[str, Any]:
        org = {
            "org_id": f"org_{slug}",
            "name": name,
            "slug": slug,
            "plan": "ENTERPRISE",
            "owner_email": owner_email,
            "status": "ACTIVE"
        }
        self._organizations.append(org)
        return org

organization_service = OrganizationService()
