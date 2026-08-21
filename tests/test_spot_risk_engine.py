"""
Automated unit tests for Multi-Vector Risk Engine.
Verifies 8 risk vectors, data completeness scoring, and overall risk categorization.
"""

import pytest
import time
from backend.spot_research.coin_discovery_engine import DiscoveredCoin
from backend.spot_research.coin_risk_engine import CoinRiskEngine

def test_risk_engine_low_liquidity_high_risk():
    engine = CoinRiskEngine()
    micro_coin = DiscoveredCoin(
        symbol="MICRO/USD (SOLANA)",
        base_asset="MICRO",
        quote_asset="USD",
        exchange="RAYDIUM (SOLANA)",
        current_price=0.001,
        volume_24h_usd=50000.0,
        liquidity_usd=3500.0,  # Under $10k -> Extreme Liquidity Risk
        volatility_pct=45.0,  # > 40% -> Extreme Volatility Risk
        spread_bps=120.0,  # > 100 bps -> Wide Spread
        source="DEXSCREENER_API"
    )
    
    report = engine.evaluate_risk(micro_coin)
    assert report.overall_risk_level == "HIGH"
    assert report.overall_risk_score >= 60.0
    assert len(report.key_warnings) > 0
    assert len(report.risk_vectors) == 8

def test_risk_engine_established_low_risk():
    engine = CoinRiskEngine()
    solid_coin = DiscoveredCoin(
        symbol="SOL/USDT",
        base_asset="SOL",
        quote_asset="USDT",
        exchange="BINANCE",
        current_price=180.0,
        volume_24h_usd=800000000.0,
        liquidity_usd=50000000.0,
        volatility_pct=4.2,
        spread_bps=5.0,
        source="BINANCE_REST_24HR"
    )
    
    report = engine.evaluate_risk(solid_coin)
    assert report.overall_risk_level in ["LOW", "MEDIUM"]
    assert report.overall_risk_score < 50.0
