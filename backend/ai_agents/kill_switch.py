from typing import Dict, Any

class AIKillSwitchManager:
    """Global Emergency AI Kill-Switch Manager."""

    def __init__(self):
        self._active: bool = False

    def is_active(self) -> bool:
        return self._active

    def activate(self, reason: str = "Emergency Operator Override") -> Dict[str, Any]:
        self._active = True
        return {"kill_switch_active": True, "reason": reason, "status": "BLOCKED"}

    def deactivate(self) -> Dict[str, Any]:
        self._active = False
        return {"kill_switch_active": False, "status": "OPERATIONAL"}

ai_kill_switch = AIKillSwitchManager()
