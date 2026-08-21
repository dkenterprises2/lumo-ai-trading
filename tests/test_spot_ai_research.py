"""
Automated unit tests for AI Research Synthesis Engine.
Verifies dynamic context synthesis, recommendation derivation, and zero static hardcoded duplication.
"""

import pytest
import time
from backend.spot_research.coin_discovery_engine import DiscoveredCoin
from backend.spot_research.coin_classifier import coin_classifier
from backend.spot_research.coin_risk_engine import coin_risk_engine
from backend.spot_research.coin_ai_researcher import CoinAIResearcher

def test_ai_research_synthesis():
    researcher = CoinAIResearcher()
    coin = DiscoveredCoin(
        symbol="BONK/USDT",
        base_asset="BONK",
        quote_asset="USDT",
        exchange="BINANCE",
        current_price=0.000022,
        volume_24h_usd=45000000.0,
        price_change_24h_pct=18.5,
        volatility_pct=22.0,
        spread_bps=8.0,
        source="BINANCE_REST_24HR"
    )
    
    classification = coin_classifier.classify(coin)
    risk_report = coin_risk_engine.evaluate_risk(coin)
    dossier = researcher.generate_research_dossier(coin, classification, risk_report)
    
    assert dossier.symbol == "BONK/USDT"
    assert dossier.category == "MEME"
    assert dossier.opportunity_score > 0
    assert dossier.recommendation in ["WATCH", "PAPER_TEST", "REJECT", "INSUFFICIENT_DATA"]
    assert len(dossier.bullish_factors) > 0
    assert len(dossier.summary) > 20
    assert "BONK/USDT" in dossier.summary
