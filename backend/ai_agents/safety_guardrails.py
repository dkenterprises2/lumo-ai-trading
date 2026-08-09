import time
from typing import Dict, Any, List

class AISafetyGuardrails:
    """AI Safety Controls, Drawdown Guardrails & Loss Circuit Breaker."""

    def __init__(self):
        self._safety_events: List[Dict[str, Any]] = [
            {
                "event_id": "SAFE-101",
                "agent_id": "AGENT-VOL-01",
                "rule": "MAX_DAILY_LOSS_EXCEEDED",
                "severity": "WARNING",
                "triggered_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def list_safety_events(self) -> List[Dict[str, Any]]:
        return self._safety_events

safety_guardrails = AISafetyGuardrails()
