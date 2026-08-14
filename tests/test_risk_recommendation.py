import pytest
from backend.portfolio_risk.risk_recommendation import RiskRecommendationEngine

def test_risk_recommendation_generation():
    engine = RiskRecommendationEngine()

    p_state = {"overall_status": "HIGH"}
    conc = {"highest_concentrated_symbol": "BTC/USDT", "single_symbol_max_pct": 45.0}
    corr = {"correlation_risk_score": 0.75, "symbol_risks": {"BTC/USDT": {}, "ETH/USDT": {}}}

    recs = engine.generate_recommendations(p_state, conc, corr)
    assert len(recs) >= 2
    assert any(r.affected_symbols == ["BTC/USDT"] for r in recs)
