import pytest
import pandas as pd
import numpy as np
from backend.portfolio_risk.covariance_engine import CovarianceEngine

def test_covariance_and_risk_contribution():
    engine = CovarianceEngine()
    df = pd.DataFrame({
        "BTC/USDT": [0.01, -0.02, 0.015, -0.01],
        "ETH/USDT": [0.012, -0.022, 0.018, -0.012]
    })
    cov = engine.compute_covariance(df)
    assert not cov.empty

    mrc = engine.calculate_marginal_risk_contribution(cov, {"BTC/USDT": 0.6, "ETH/USDT": 0.4})
    assert "BTC/USDT" in mrc
    assert "ETH/USDT" in mrc
