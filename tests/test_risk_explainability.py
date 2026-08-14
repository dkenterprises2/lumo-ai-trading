import pytest
from backend.portfolio_risk.risk_explainability import RiskExplainabilityEngine

def test_explainability_formatting():
    engine = RiskExplainabilityEngine()
    exp = engine.format_explanation(
        decision="BLOCKED",
        symbol="BTC/USDT",
        side="LONG",
        requested_alloc=1000.0,
        approved_alloc=0.0,
        effective_limit=6,
        open_positions=6,
        rem_budget_pct=0.5,
        primary_factor="DYNAMIC_LIMIT_REACHED",
        reasons=["Effective trade limit of 6 reached."]
    )

    assert exp.decision == "BLOCKED"
    assert exp.primary_factor == "DYNAMIC_LIMIT_REACHED"
    assert len(exp.detailed_reasons) > 0
