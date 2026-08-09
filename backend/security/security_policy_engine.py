from typing import Dict, Any, List

class SecurityPolicyEnforcementEngine:
    """Security Policy Enforcement Engine."""

    def list_policies(self) -> List[Dict[str, Any]]:
        return [
            {"policy_name": "API_KEY_EXPIRATION", "max_days": 90, "enforced": True},
            {"policy_name": "MFA_FOR_ADMIN", "enforced": True},
            {"policy_name": "RATE_LIMIT_STRICT", "rpm": 600, "enforced": True}
        ]

security_policy_engine = SecurityPolicyEnforcementEngine()
