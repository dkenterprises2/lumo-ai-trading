from typing import Dict, Any

class AIGuardrailPolicyEngine:
    """Prompt Sanitizer, Security & Policy Enforcement Engine."""

    @staticmethod
    def evaluate_action(action_type: str, user_role: str) -> Dict[str, Any]:
        if action_type == "LIVE_DEPLOYMENT" and user_role != "ADMIN":
            return {"decision": "BLOCK", "reason": "UNAUTHORIZED_ROLE_FOR_LIVE_DEPLOYMENT"}
        if action_type == "LIVE_DEPLOYMENT":
            return {"decision": "REQUIRE_APPROVAL", "reason": "MANDATORY_GOVERNANCE_GATE"}
        return {"decision": "ALLOW", "reason": "SAFE_ACTION"}

guardrail_policy_engine = AIGuardrailPolicyEngine()
