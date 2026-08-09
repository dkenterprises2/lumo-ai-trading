from backend.ai_agents.base_agent import BaseAgent

class TrendFollowingAgent(BaseAgent):
    """Bull & Trend-Following RL Specialist Agent."""

    def __init__(self):
        super().__init__("AGENT-TREND-01", "Trend Following Specialist")

    def predict(self, observation: dict) -> str:
        return "BUY_SMALL"

trend_following_agent = TrendFollowingAgent()
