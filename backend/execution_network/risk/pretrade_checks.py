from typing import Dict, Any

class PreTradeRiskController:
    """Pre-Trade & Post-Trade Risk Controls & Kill-Switch Engine."""

    def __init__(self):
        self._kill_switch_active = False

    def validate_pretrade(self, symbol: str, quantity: float, price: float) -> Dict[str, Any]:
        if self._kill_switch_active:
            return {"passed": False, "reason": "KILL_SWITCH_ACTIVE"}
        notional = quantity * price
        if notional > 5000000.0:  # Fat finger $5M threshold
            return {"passed": False, "reason": "FAT_FINGER_NOTIONAL_EXCEEDED"}
        return {"passed": True, "notional": notional}

    def trigger_kill_switch(self) -> Dict[str, Any]:
        self._kill_switch_active = True
        return {"status": "KILL_SWITCH_ACTIVATED", "active": True}

pretrade_risk_controller = PreTradeRiskController()
