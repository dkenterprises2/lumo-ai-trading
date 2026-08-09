import time
from typing import Dict, Any, List

class APIAccessAuditLogger:
    """API Access Audit Logger tracking endpoint calls and IP origins."""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = [
            {
                "log_id": "API-LOG-101",
                "endpoint": "/api/v1/orders",
                "method": "POST",
                "status_code": 200,
                "ip_address": "127.0.0.1",
                "tenant_id": "ORG-101",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def list_logs(self, tenant_id: str = "ORG-101") -> List[Dict[str, Any]]:
        return self._logs

api_access_audit_logger = APIAccessAuditLogger()
