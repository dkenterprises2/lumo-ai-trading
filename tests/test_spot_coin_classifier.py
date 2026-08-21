"""
Automated unit tests for Coin Classifier.
Verifies transparent categorization into MEME, NEW, ESTABLISHED, UNKNOWN with factual evidence.
"""

import pytest
import time
from backend.spot_research.coin_discovery_engine import DiscoveredCoin
from backend.spot_research.coin_classifier import CoinClassifier

def test_coin_classifier_established_asset():
    classifier = CoinClassifier()
    btc_coin = DiscoveredCoin(
        symbol="BTC/USDT",
        base_asset="BTC",
        quote_asset="USDT",
        exchange="BINANCE",
        current_price=65000.0,
        source="BINANCE_REST_24HR"
    )
    
    res = classifier.classify(btc_coin)
    assert res.category == "ESTABLISHED"
    assert res.confidence >= 0.9
    assert "BTC" in res.reasons[0]

def test_coin_classifier_meme_token():
    classifier = CoinClassifier()
    pepe_coin = DiscoveredCoin(
        symbol="PEPE/USDT",
        base_asset="PEPE",
        quote_asset="USDT",
        exchange="BINANCE",
        current_price=0.000008,
        description="The most memeable memecoin in existence",
        source="DEXSCREENER_API"
    )
    
    res = classifier.classify(pepe_coin)
    assert res.category == "MEME"
    assert res.confidence >= 0.5
    assert any("meme" in r.lower() for r in res.reasons)

def test_coin_classifier_new_token():
    classifier = CoinClassifier()
    now = time.time()
    new_coin = DiscoveredCoin(
        symbol="XYZ/USD (SOLANA)",
        base_asset="XYZ",
        quote_asset="USD",
        exchange="RAYDIUM (SOLANA)",
        listing_ts=now - (86400 * 3),  # 3 days old
        current_price=1.25,
        source="DEXSCREENER_API"
    )
    
    res = classifier.classify(new_coin)
    assert res.category == "NEW"
    assert res.confidence >= 0.8
    assert any("listed within last" in r.lower() for r in res.reasons)
