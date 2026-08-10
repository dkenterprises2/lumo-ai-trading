import time
import uuid
from typing import Dict, Any, List, Optional

class OrganizationManager:
    """Enterprise Organization & Workspace Management System."""

    def __init__(self):
        self._orgs: List[Dict[str, Any]] = [
            {
                "org_id": "ORG-101",
                "name": "Alpha Quant Capital",
                "slug": "alpha-quant",
                "owner_id": 1,
                "plan_tier": "INSTITUTIONAL",
                "status": "ACTIVE",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            },
            {
                "org_id": "ORG-ENTERPRISE",
                "name": "Kumar Dharma Enterprise",
                "slug": "kumar-dharma-enterprise",
                "owner_id": 3,
                "plan_tier": "ENTERPRISE",
                "status": "ACTIVE",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]
        self._members: List[Dict[str, Any]] = [
            {"member_id": "MEM-1", "org_id": "ORG-101", "user_id": 1, "role": "OWNER"},
            {"member_id": "MEM-2", "org_id": "ORG-ENTERPRISE", "user_id": 3, "role": "OWNER"}
        ]


    def create_organization(self, name: str, owner_id: int) -> Dict[str, Any]:
        """Create new tenant organization."""
        org_id = f"ORG-{int(time.time())}"
        slug = name.lower().replace(" ", "-")
        org = {
            "org_id": org_id,
            "name": name,
            "slug": slug,
            "owner_id": owner_id,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._orgs.insert(0, org)
        self._members.append({"member_id": f"MEM-{len(self._members)+1}", "org_id": org_id, "user_id": owner_id, "role": "OWNER"})
        return org

    def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        for o in self._orgs:
            if o["org_id"] == org_id:
                return o
        return self._orgs[0]

    def list_organizations(self) -> List[Dict[str, Any]]:
        return self._orgs

organization_manager = OrganizationManager()
