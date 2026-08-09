from backend.ai_agents.base_agent import BaseAgent

class MeanReversionAgent(BaseAgent):
    """Sideways & Mean-Reversion RL Specialist Agent."""

    def __init__(self):
        super().__init__("AGENT-MEANREV-01", "Mean Reversion Specialist")

    def predict(self, observation: dict) -> str:
        return "HOLD"

mean_reversion_agent = MeanReversionAgent()
