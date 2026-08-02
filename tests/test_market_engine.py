import pytest
import pandas as pd
from market_data import MarketDataEngine

def test_market_data_engine_instantiation():
    engine = MarketDataEngine()
    assert engine is not None

def test_fetch_current_price():
    engine = MarketDataEngine()
    price = engine.fetch_current_price("BTC/USDT")
    assert isinstance(price, float)
    assert price > 0.0

def test_fetch_ohlcv():
    engine = MarketDataEngine()
    df = engine.fetch_ohlcv("BTC/USDT", timeframe="1h", limit=50)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 50
    assert "close" in df.columns
    assert "volume" in df.columns

def test_calculate_technical_indicators():
    engine = MarketDataEngine()
    df = engine.fetch_ohlcv("BTC/USDT", timeframe="1h", limit=60)
    ta = engine.calculate_technical_indicators(df)

    assert "current_price" in ta
    assert "rsi" in ta
    assert "macd" in ta
    assert "sma_20" in ta
    assert "vwap" in ta
    assert "atr" in ta
    assert "bb_upper" in ta
    assert "bb_lower" in ta
    assert "technical_score" in ta
    assert 0.0 <= ta["technical_score"] <= 100.0
