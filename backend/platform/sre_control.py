from typing import Dict, Any, List

class SREControlCenter:
    """Site Reliability Engineering Error Budgets & Incidents Controller."""

    @staticmethod
    def get_error_budgets() -> List[Dict[str, Any]]:
        return [
            {"service": "lumo-api", "target_slo": 99.9, "current_slo": 99.98, "budget_remaining_pct": 82.0},
            {"service": "lumo-execution", "target_slo": 99.99, "current_slo": 99.995, "budget_remaining_pct": 94.0}
        ]

    @staticmethod
    def get_incidents() -> List[Dict[str, Any]]:
        return [
            {"incident_id": "INC-101", "severity": "LOW", "service": "lumo-marketdata", "status": "RESOLVED"}
        ]

sre_control = SREControlCenter()
