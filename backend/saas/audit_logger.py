import time
from typing import Dict, Any, List

class TenantAuditLogger:
    """Tenant Audit Logging & Security Trail System."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = [
            {
                "audit_id": "AUD-SAAS-101",
                "org_id": "ORG-101",
                "actor": "admin@alphaquant.com",
                "action": "MEMBER_INVITED",
                "details": "Invited trader@alphaquant.com as TRADER",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def log_action(self, org_id: str, actor: str, action: str, details: str = "") -> Dict[str, Any]:
        """Log tenant security action."""
        log_entry = {
            "audit_id": f"AUD-SAAS-{int(time.time())}",
            "org_id": org_id,
            "actor": actor,
            "action": action,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._logs.insert(0, log_entry)
        return log_entry

    def list_logs(self, org_id: str = "ORG-101") -> List[Dict[str, Any]]:
        return [l for l in self._logs if l["org_id"] == org_id]

tenant_audit_logger = TenantAuditLogger()
