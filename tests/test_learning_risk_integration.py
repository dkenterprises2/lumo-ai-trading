import pytest
from backend.portfolio_risk.risk_governance import RiskGovernanceEngine

def test_learning_loop_governance_rejection():
    engine = RiskGovernanceEngine()

    # Scenario I: Learning system proposes unsafe parameters (e.g. attempting to expand trade limit beyond safe ceiling or disable kill switch)
    unsafe_params = {
        "dynamic_trade_limit_multiplier": 1.5,
        "disable_kill_switch": True,
        "max_leverage": 25
    }
    user_hard_limits = {"max_leverage": 10}

    eval_res = engine.evaluate_candidate_parameters("cand_123", unsafe_params, user_hard_limits)
    assert eval_res.approved is False
    assert eval_res.status == "REJECTED"
    assert len(eval_res.safety_violations) >= 2
