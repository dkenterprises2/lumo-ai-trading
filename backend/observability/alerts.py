import time
from typing import Dict, Any, List

class AlertEngine:
    """Alertmanager Notification Rules & System Alerts Engine."""

    def __init__(self):
        self._alerts: List[Dict[str, Any]] = [
            {
                "id": "ALT-101",
                "severity": "CRITICAL",
                "component": "Exchange Connectivity",
                "summary": "High latency detected on OKX WebSocket stream (>150ms)",
                "status": "FIRING",
                "triggered_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            },
            {
                "id": "ALT-102",
                "severity": "WARNING",
                "component": "Risk Engine",
                "summary": "Strategy 'Trend Following' reached 80% of daily loss limit",
                "status": "RESOLVED",
                "triggered_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        return self._alerts


    def trigger_alert(self, severity: str, component: str, summary: str) -> Dict[str, Any]:
        """Trigger new system alert notification."""
        alert = {
            "id": f"ALT-{int(time.time())}",
            "severity": severity.upper(),
            "component": component,
            "summary": summary,
            "status": "FIRING",
            "triggered_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._alerts.insert(0, alert)
        return alert

alert_engine = AlertEngine()
