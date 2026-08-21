"""
Automated unit tests for Gated Paper Validation Engine.
Verifies that only coins passing the research & risk gates can be executed.
"""

import pytest
import time
from backend.spot_research.coin_discovery_engine import DiscoveredCoin
from backend.spot_research.coin_ai_researcher import CoinAIResearchDossier
from backend.spot_research.paper_validation_engine import PaperValidationEngine

def test_paper_validation_rejected_when_not_approved():
    engine = PaperValidationEngine()
    coin = DiscoveredCoin(
        symbol="JUNK/USDT",
        base_asset="JUNK",
        quote_asset="USDT",
        exchange="BINANCE",
        current_price=0.50,
        source="BINANCE_REST_24HR"
    )
    
    # Dossier with REJECT recommendation
    dossier = CoinAIResearchDossier(
        symbol="JUNK/USDT",
        category="NEW",
        opportunity_score=35.0,
        risk_score=85.0,
        research_confidence=0.5,
        recommendation="REJECT",
        summary="High risk rejected asset."
    )
    
    res = engine.execute_paper_validation(coin, dossier, allocation_usd=250.0)
    assert res["status"] == "REJECTED"
    assert "failed research gate" in res["reason"].lower()

def test_paper_validation_success_when_approved():
    engine = PaperValidationEngine()
    coin = DiscoveredCoin(
        symbol="ALPHA/USDT",
        base_asset="ALPHA",
        quote_asset="USDT",
        exchange="BINANCE",
        current_price=2.50,
        source="BINANCE_REST_24HR"
    )
    
    # Dossier with PAPER_TEST recommendation
    dossier = CoinAIResearchDossier(
        symbol="ALPHA/USDT",
        category="NEW",
        opportunity_score=82.0,
        risk_score=40.0,
        research_confidence=0.9,
        recommendation="PAPER_TEST",
        summary="High potential new momentum breakout."
    )
    
    res = engine.execute_paper_validation(coin, dossier, allocation_usd=500.0)
    assert res["status"] == "SUCCESS"
    assert res["trade"]["trade_id"].startswith("PV-")
    assert res["trade"]["position_size_usd"] == 500.0
    assert res["trade"]["status"] == "OPEN"
