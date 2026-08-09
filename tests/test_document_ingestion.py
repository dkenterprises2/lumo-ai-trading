import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.rag.document_ingestion import rag_engine

def test_document_ingestion():
    doc = rag_engine.ingest_document("Risk Policy", "Policy content", "RISK_POLICY")
    assert doc["status"] == "INDEXED"
    assert doc["chunks_indexed"] == 4
