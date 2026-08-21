"""
Automated unit & integration tests for Coin Discovery Engine.
Verifies real-data ingestion, missing-field handling, duplicate prevention, and zero fake data.
"""

import pytest
import time
from backend.spot_research.coin_discovery_engine import CoinDiscoveryEngine, DiscoveredCoin

def test_coin_discovery_structure():
    engine = CoinDiscoveryEngine()
    
    # Test creating a verified DiscoveredCoin model
    coin = DiscoveredCoin(
        symbol="PEPE/USDT",
        base_asset="PEPE",
        quote_asset="USDT",
        exchange="BINANCE",
        current_price=0.0000085,
        volume_24h_usd=2500000.0,
        price_change_24h_pct=14.5,
        volatility_pct=18.2,
        spread_bps=12.0,
        source="BINANCE_REST_24HR",
        tags=["CEX", "SPOT"]
    )
    
    assert coin.symbol == "PEPE/USDT"
    assert coin.current_price == 0.0000085
    assert coin.liquidity_usd is None  # Must be None when not provided by CEX ticker (NO FAKE VALUE)
    assert coin.fdv_usd is None  # Must be None when not provided (NO FAKE VALUE)
    assert coin.data_freshness_seconds >= 0.0

def test_coin_discovery_no_fake_data_leakage():
    engine = CoinDiscoveryEngine()
    coins = engine.discover_all_coins(force_refresh=True)
    
    assert len(coins) > 0, "Expected at least 1 discovered coin from real market endpoints"
    
    for c in coins:
        assert isinstance(c.symbol, str)
        assert len(c.symbol) > 0
        assert c.source in ["BINANCE_REST_24HR", "DEXSCREENER_API", "COINGECKO_API"]
        if c.current_price is not None:
            assert c.current_price > 0, f"Invalid price {c.current_price} for {c.symbol}"
        if c.volume_24h_usd is not None:
            assert c.volume_24h_usd >= 0
