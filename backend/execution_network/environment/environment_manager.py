from typing import Dict, Any

class ExecutionEnvironmentManager:
    """Execution Environment Manager (PAPER / SHADOW / LIVE)."""

    def __init__(self):
        self._current_env = "PAPER"

    def get_current_environment(self) -> Dict[str, Any]:
        return {"environment": self._current_env, "live_approved": self._current_env == "LIVE"}

    def request_switch(self, target_env: str) -> Dict[str, Any]:
        if target_env == "LIVE":
            return {"target": "LIVE", "status": "GOVERNANCE_APPROVAL_REQUIRED", "switched": False}
        self._current_env = target_env
        return {"target": target_env, "status": "SWITCHED", "switched": True}

environment_manager = ExecutionEnvironmentManager()
