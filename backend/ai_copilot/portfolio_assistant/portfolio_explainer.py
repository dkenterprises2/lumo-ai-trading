from typing import Dict, Any

class PortfolioRiskExplainer:
    """Conversational Portfolio, Exposure & Risk Narrator."""

    @staticmethod
    def explain_portfolio() -> Dict[str, Any]:
        return {
            "summary": "BTC exposure increased by 4.2% due to momentum strategy alpha_momentum_v12.",
            "risk_impact": "Portfolio VaR increased from 2.8% to 3.1%.",
            "execution_cost": "Average implementation shortfall was 3.4 bps.",
            "recommended_actions": ["Reduce SOL concentration by 1.5%"]
        }

portfolio_explainer = PortfolioRiskExplainer()
