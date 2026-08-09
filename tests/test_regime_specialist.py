import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_agents.regime_specialist import regime_specialist

def test_regime_specialist_routing():
    assert regime_specialist.route_to_specialist(0.05, 0.2) == "VOLATILITY_BREAKOUT"
    assert regime_specialist.route_to_specialist(0.01, 0.8) == "TREND_FOLLOWING"
    assert regime_specialist.route_to_specialist(0.01, 0.0) == "MEAN_REVERSION"
