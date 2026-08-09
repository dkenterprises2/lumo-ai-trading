from typing import Dict, Any

class QuotaEnforcerService:
    """Soft & Hard Quota Limit Threshold Enforcement Engine."""

    @staticmethod
    def check_quota(category: str, current_usage: float, max_limit: float = 200000.0) -> Dict[str, Any]:
        pct = (current_usage / max_limit) * 100.0
        status = "OK"
        if pct >= 100.0:
            status = "HARD_LIMIT_REACHED"
        elif pct >= 95.0:
            status = "SOFT_LIMIT_WARNING"
        elif pct >= 80.0:
            status = "WARNING_80"

        return {
            "category": category,
            "current_usage": current_usage,
            "max_limit": max_limit,
            "utilization_pct": round(pct, 2),
            "status": status
        }

quota_enforcer = QuotaEnforcerService()
