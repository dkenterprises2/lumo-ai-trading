import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_strategy import AITradingStrategy, MarketRegimeDetector

def test_market_regime_detection_bull_trend():
    tech = {
        "adx": 32.0,
        "plus_di": 30.0,
        "minus_di": 15.0,
        "ema_20": 64000.0,
        "ema_50": 62000.0,
        "ema_200": 58000.0,
        "atr": 1000.0,
        "volume_spike_ratio": 1.2
    }
    sent = {"fear_greed": {"value": 55}}
    regime, desc = MarketRegimeDetector.detect_regime(65000.0, tech, sent)
    assert regime == "BULL_TREND"

def test_market_regime_detection_high_volatility():
    tech = {
        "adx": 20.0,
        "plus_di": 20.0,
        "minus_di": 20.0,
        "atr": 3500.0,  # 3500/65000 = 5.38% > 4.0%
        "volume_spike_ratio": 3.5
    }
    sent = {"fear_greed": {"value": 50}}
    regime, desc = MarketRegimeDetector.detect_regime(65000.0, tech, sent)
    assert regime == "HIGH_VOLATILITY"

def test_market_regime_adaptive_weights():
    ai = AITradingStrategy()
    tech = {
        "adx": 35.0,
        "plus_di": 32.0,
        "minus_di": 12.0,
        "ema_20": 64000.0,
        "ema_50": 62000.0,
        "ema_200": 58000.0,
        "atr": 1000.0
    }
    res = ai.evaluate_trading_signal("BTC/USDT", 65000.0, tech, {"fear_greed": {"value": 60}})
    assert res["market_regime"] == "BULL_TREND"
    assert "score_breakdown" in res
    assert "total" in res["score_breakdown"]
    assert res["score_breakdown"]["total"]["max"] == 100
