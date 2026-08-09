import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution_algos.slippage_predictor import slippage_predictor

def test_slippage_prediction():
    pred = slippage_predictor.predict_slippage(10.0, 10000.0)
    assert "predicted_slippage_bps" in pred
    assert pred["predicted_slippage_bps"] > 0
