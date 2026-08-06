import time
from typing import Dict, Any, List, Optional
from backend.ai.research_agents import (
    MarketResearchAgent,
    StrategyGeneratorAgent,
    FeatureEngineeringAgent,
    BacktestAgent,
    RiskEvaluationAgent,
    PerformanceEvaluationAgent,
    DeploymentRecommendationAgent
)

class AIRecommendationEngine:
    """AI Recommendation Engine orchestrating end-to-end multi-agent research workflow."""

    def __init__(self):
        self.market_agent = MarketResearchAgent()
        self.strategy_agent = StrategyGeneratorAgent()
        self.feature_agent = FeatureEngineeringAgent()
        self.backtest_agent = BacktestAgent()
        self.risk_agent = RiskEvaluationAgent()
        self.perf_agent = PerformanceEvaluationAgent()
        self.recom_agent = DeploymentRecommendationAgent()

    def run_full_research_workflow(self, symbol: str = "BTC/USDT", hypothesis: str = "Multi-Factor Momentum Alpha") -> Dict[str, Any]:
        """Execute full 7-agent quantitative research pipeline."""
        mkt_res = self.market_agent.run(symbol)
        strat_res = self.strategy_agent.run(hypothesis)
        feat_res = self.feature_agent.run(symbol)
        bt_res = self.backtest_agent.run(symbol)
        risk_res = self.risk_agent.run(bt_res)
        perf_res = self.perf_agent.run(bt_res)
        recom_res = self.recom_agent.run(risk_res, perf_res)

        exp_id = f"EXP_{int(time.time())}"

        return {
            "experiment_id": exp_id,
            "symbol": symbol,
            "hypothesis": hypothesis,
            "market_research": mkt_res,
            "strategy_rules": strat_res["proposed_rules"],
            "features_used": feat_res["selected_features"],
            "backtest_summary": {
                "win_rate_pct": bt_res["win_rate_pct"],
                "total_return_pct": bt_res["total_return_pct"]
            },
            "risk_metrics": risk_res,
            "performance_metrics": perf_res,
            "recommendation": recom_res,
            "timestamp": time.time()
        }

ai_recommendation_engine = AIRecommendationEngine()
