import time
from typing import Dict, Any, List

class AIModelRegistry:
    """Versioned Checkpoint & Model Artifact Registry."""

    def __init__(self):
        self._entries: List[Dict[str, Any]] = [
            {
                "version_id": "ppo_bull_v1",
                "agent": "PPO_BULL_SPECIALIST",
                "status": "APPROVED",
                "sharpe_ratio": 2.45,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def list_entries(self) -> List[Dict[str, Any]]:
        return self._entries

    def promote_entry(self, version_id: str, status: str = "APPROVED") -> Dict[str, Any]:
        for e in self._entries:
            if e["version_id"] == version_id:
                e["status"] = status
                return e
        new_entry = {
            "version_id": version_id,
            "agent": "RL_AGENT",
            "status": status,
            "sharpe_ratio": 2.10,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._entries.append(new_entry)
        return new_entry

model_registry = AIModelRegistry()
