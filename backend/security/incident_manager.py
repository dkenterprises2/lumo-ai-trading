import time
from typing import Dict, Any, List

class SecurityIncidentManager:
    """Security Incident Management System."""

    def __init__(self):
        self._incidents: List[Dict[str, Any]] = [
            {
                "incident_id": "INC-2026-001",
                "severity": "LOW",
                "title": "Failed API Key Auth Burst Detected",
                "status": "CONTAINED",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def create_incident(self, title: str, severity: str = "MEDIUM") -> Dict[str, Any]:
        inc = {
            "incident_id": f"INC-{int(time.time())}",
            "severity": severity,
            "title": title,
            "status": "OPEN",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._incidents.insert(0, inc)
        return inc

    def list_incidents(self) -> List[Dict[str, Any]]:
        return self._incidents

security_incident_manager = SecurityIncidentManager()
