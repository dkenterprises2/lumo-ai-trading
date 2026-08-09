import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.rag.document_ingestion import rag_engine

def test_rag_retrieval():
    results = rag_engine.search_knowledge("risk limit")
    assert len(results) >= 1
    assert results[0]["relevance_score"] > 0.9
