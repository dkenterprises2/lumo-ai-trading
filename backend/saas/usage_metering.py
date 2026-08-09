from typing import Dict, Any

class UsageMeteringEngine:
    """Tenant Usage & Consumption Metering Engine."""

    def __init__(self):
        self._usage = {
            "api_calls": 142000,
            "websocket_messages": 850000,
            "backtest_runs": 120,
            "rl_training_hours": 45,
            "storage_gb": 25.4
        }

    def record_usage(self, category: str, amount: float = 1.0):
        self._usage[category] = self._usage.get(category, 0) + amount

    def get_usage(self) -> Dict[str, Any]:
        return self._usage

usage_metering = UsageMeteringEngine()
usage_metering_engine = usage_metering

