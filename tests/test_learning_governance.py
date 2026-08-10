import pytest
import asyncio
from backend.learning.weight_optimizer import weight_optimizer
from backend.learning.learning_governance import learning_governance
from backend.database.session import init_db

@pytest.mark.asyncio
async def test_learning_governance_flow():
    await init_db()
    exp = await weight_optimizer.run_optimization(strategy_name="AI_HYBRID", market_regime="NEUTRAL", n_trials=20)
    exp_id = exp["experiment_id"]

    sub = await learning_governance.submit_for_review(exp_id)
    assert sub["status"] == "success"
    assert sub["governance_status"] == "UNDER_REVIEW"

    # Reject without human approval
    unauth_res = await learning_governance.approve_and_deploy(exp_id, "admin@lumo.trade", human_approval=False)
    assert unauth_res["status"] == "error"

    # Deploy with human approval
    deploy = await learning_governance.approve_and_deploy(exp_id, "admin@lumo.trade", human_approval=True)
    assert deploy["status"] == "success"
    assert deploy["governance_status"] == "PRODUCTION_APPROVED"
    assert deploy["deployed_version"] >= 1

    approvals = await learning_governance.get_approvals(limit=5)
    assert len(approvals) > 0
