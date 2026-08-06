import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai_strategy import AITradingStrategy


def test_ai_strategy_evaluation_long():
    strategy = AITradingStrategy()
    ta_data = {
        "rsi": 28.0,
        "trend": "STRONG_BULLISH",
        "macd": 25.0,
        "macd_signal": 10.0,
        "macd_hist": 15.0,
        "vwap": 64500.0,
        "atr": 500.0,
        "ema_20": 64800.0,
        "ema_50": 63800.0,
        "ema_200": 61200.0,
        "adx": 35.0,
        "plus_di": 32.0,
        "minus_di": 12.0,
        "trend_strength": "STRONG",
        "obv": 50000.0,
        "obv_ema": 40000.0,
        "volume_spike_ratio": 2.3,
        "is_volume_spike": True
    }
    sentiment = {
        "combined_score": 80.0,
        "label": "BULLISH",
        "fear_greed_score": 75
    }

    signal = strategy.evaluate_trading_signal(
        symbol="BTC/USDT",
        current_price=65000.0,
        technical_data=ta_data,
        sentiment_summary=sentiment,
        strategy_name="AI Hybrid",
        risk_mode="Moderate"
    )

    assert signal["symbol"] == "BTC/USDT"
    assert signal["action"] in ["BUY", "STRONG_BUY"]
    assert signal["direction"] == "LONG"
    assert 0.0 <= signal["confidence_score"] <= 100.0
    assert signal["stop_loss_price"] < 65000.0
    assert signal["take_profit_price"] > 65000.0
    assert "score_breakdown" in signal
    assert "explainable_reasons" in signal
    assert len(signal["explainable_reasons"]) >= 3

def test_ai_strategy_evaluation_short():
    strategy = AITradingStrategy()
    ta_data = {
        "rsi": 78.0,
        "trend": "STRONG_BEARISH",
        "macd": -25.0,
        "macd_signal": -10.0,
        "macd_hist": -15.0,
        "vwap": 66000.0,
        "atr": 500.0,
        "ema_20": 64200.0,
        "ema_50": 65500.0,
        "ema_200": 67000.0,
        "adx": 38.0,
        "plus_di": 10.0,
        "minus_di": 35.0,
        "trend_strength": "STRONG",
        "obv": 20000.0,
        "obv_ema": 35000.0,
        "volume_spike_ratio": 2.1,
        "is_volume_spike": True
    }
    sentiment = {
        "combined_score": 20.0,
        "label": "BEARISH",
        "fear_greed_score": 25
    }

    signal = strategy.evaluate_trading_signal(
        symbol="BTC/USDT",
        current_price=65000.0,
        technical_data=ta_data,
        sentiment_summary=sentiment,
        strategy_name="AI Hybrid",
        risk_mode="Moderate"
    )

    assert signal["action"] in ["SELL", "STRONG_SELL"]
    assert signal["direction"] == "SHORT"
    assert signal["stop_loss_price"] > 65000.0
    assert signal["take_profit_price"] < 65000.0
    assert "score_breakdown" in signal
    assert "explainable_reasons" in signal

def test_ai_engine_2_score_breakdown_weights():
    strategy = AITradingStrategy()
    ta_data = {
        "rsi": 50.0,
        "trend": "NEUTRAL",
        "macd": 0.0,
        "macd_signal": 0.0,
        "macd_hist": 0.0,
        "vwap": 65000.0,
        "atr": 500.0,
        "ema_20": 65000.0,
        "ema_50": 65000.0,
        "ema_200": 65000.0,
        "adx": 15.0,
        "plus_di": 20.0,
        "minus_di": 20.0,
        "trend_strength": "WEAK",
        "obv": 1000.0,
        "obv_ema": 1000.0,
        "volume_spike_ratio": 1.0,
        "is_volume_spike": False
    }
    sentiment = {"combined_score": 50.0, "label": "NEUTRAL"}

    signal = strategy.evaluate_trading_signal(
        symbol="ETH/USDT",
        current_price=2000.0,
        technical_data=ta_data,
        sentiment_summary=sentiment
    )

    breakdown = signal["score_breakdown"]
    total_weight = sum(item["weight"] for item in breakdown.values() if "weight" in item)
    assert round(total_weight, 2) == 1.00

    assert "ema_trend" in breakdown
    assert "macd_momentum" in breakdown
    assert "rsi_oscillator" in breakdown
    assert "adx_trend_strength" in breakdown
    assert "vwap_position" in breakdown
    assert "obv_flow" in breakdown
    assert "volume_spike" in breakdown
    assert "atr_volatility" in breakdown

