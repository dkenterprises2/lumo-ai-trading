import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.memory.session_memory import memory_provenance

def test_purge_long_term_memory():
    p = memory_provenance.purge_memory("ws_old")
    assert p["status"] == "PURGED"
