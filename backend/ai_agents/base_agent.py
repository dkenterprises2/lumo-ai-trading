from typing import Dict, Any

class BaseAgent:
    """Base Reinforcement Learning Trading Agent Contract."""

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name

    def predict(self, observation: Dict[str, Any]) -> str:
        return "HOLD"

    def get_info(self) -> Dict[str, Any]:
        return {"agent_id": self.agent_id, "name": self.name, "status": "ACTIVE"}
