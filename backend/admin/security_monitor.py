import time
from typing import Dict, Any, List

class SecurityMonitorConsole:
    """Security & Privileged Audit Event Monitoring System."""

    def __init__(self):
        self._security_events: List[Dict[str, Any]] = [
            {
                "event_id": "SEC-EVT-101",
                "ip_address": "127.0.0.1",
                "user_id": 1,
                "tenant_id": "ORG-101",
                "action": "SUPER_ADMIN_LOGIN",
                "details": "Super admin authenticated successfully",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def list_security_events(self) -> List[Dict[str, Any]]:
        return self._security_events

security_monitor_console = SecurityMonitorConsole()
