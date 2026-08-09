from backend.ai_agents.base_agent import BaseAgent

class MomentumAgent(BaseAgent):
    """High-Momentum RL Specialist Agent."""

    def __init__(self):
        super().__init__("AGENT-MOM-01", "Momentum Specialist")

    def predict(self, observation: dict) -> str:
        return "BUY_LARGE"

momentum_agent = MomentumAgent()
