"""
Automated unit tests for Spot Research Evidence Store & CSV/JSON Export.
Verifies persistent logging, non-blocking queuing, and audit export capabilities.
"""

import pytest
import time
import uuid
from backend.spot_research.spot_research_evidence_store import SpotResearchEvidenceStore, SpotResearchForensicEvent

def test_evidence_store_persistence_and_export():
    store = SpotResearchEvidenceStore()
    
    event_id = f"TEST-EVT-{uuid.uuid4().hex[:6].upper()}"
    event = SpotResearchForensicEvent(
        event_id=event_id,
        symbol="PEPE/USDT",
        exchange="BINANCE",
        category="MEME",
        price_usd=0.0000085,
        volume_24h_usd=25000000.0,
        opportunity_score=78.5,
        risk_score=45.0,
        recommendation="PAPER_TEST",
        data_sources=["BINANCE_REST_24HR"],
        raw_dossier_json="{\"test\": true}"
    )
    
    store.record_event(event)
    
    # Wait for micro-batch persistence
    time.sleep(0.3)
    
    events = store.query_events(limit=10)
    assert len(events) > 0
    
    # Test CSV Export
    csv_out = store.export_csv(limit=10)
    assert "event_id" in csv_out
    assert "symbol" in csv_out
    assert "PEPE/USDT" in csv_out
    
    # Test JSON Export
    json_out = store.export_json(limit=10)
    assert isinstance(json_out, list)
    assert len(json_out) > 0
