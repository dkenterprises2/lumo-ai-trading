import pytest
from ai_strategy import AITradingStrategy

def test_ai_strategy_evaluation_long():
    strategy = AITradingStrategy()
    ta_data = {
        "technical_score": 85.0,
        "rsi": 32.0,
        "trend": "BULLISH",
        "macd_hist": 15.0,
        "vwap": 64500.0,
        "atr": 500.0,
        "bb_upper": 66000.0,
        "bb_lower": 63000.0
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
    assert signal["confidence_score"] >= 65.0
    assert signal["stop_loss_price"] < 65000.0
    assert signal["take_profit_price"] > 65000.0

def test_ai_strategy_evaluation_short():
    strategy = AITradingStrategy()
    ta_data = {
        "technical_score": 15.0,
        "rsi": 78.0,
        "trend": "BEARISH",
        "macd_hist": -25.0,
        "vwap": 66000.0,
        "atr": 500.0,
        "bb_upper": 67000.0,
        "bb_lower": 64000.0
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
