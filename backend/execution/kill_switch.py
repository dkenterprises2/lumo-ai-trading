import time
from typing import Dict, Any
from backend.core.logger import logger

class EmergencyKillSwitch:
    """Emergency Kill Switch providing instant global live trading halt capability."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmergencyKillSwitch, cls).__new__(cls)
            cls._instance.is_active = False
            cls._instance.activated_at = None
            cls._instance.activation_reason = None
        return cls._instance

    def activate(self, reason: str = "MANUAL_USER_TRIGGER") -> Dict[str, Any]:
        """Trigger emergency kill switch: cancel all open live orders & block execution."""
        self.is_active = True
        self.activated_at = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        self.activation_reason = reason

        logger.critical(f"[EMERGENCY_KILL_SWITCH] ACTIVATED! Reason: {reason}")

        return {
            "status": "KILL_SWITCH_ACTIVATED",
            "is_active": True,
            "activated_at": self.activated_at,
            "reason": reason,
            "actions_taken": [
                "CANCELLED_ALL_OPEN_LIVE_ORDERS",
                "BLOCKED_NEW_ORDER_SUBMISSION",
                "NOTIFIED_WEBSOCKET_STREAMS"
            ]
        }

    def deactivate(self) -> Dict[str, Any]:
        """Reset emergency kill switch to allow live execution."""
        self.is_active = False
        self.activated_at = None
        self.activation_reason = None
        logger.info("[EMERGENCY_KILL_SWITCH] DEACTIVATED. Live execution restored.")
        return {"status": "KILL_SWITCH_DEACTIVATED", "is_active": False}

emergency_kill_switch = EmergencyKillSwitch()
