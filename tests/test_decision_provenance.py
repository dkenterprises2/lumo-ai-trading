import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ai_copilot.memory.session_memory import memory_provenance

def test_provenance_chain_length():
    mem = memory_provenance.get_workspace_memory("ws_quant_team")
    assert mem["provenance_chain_length"] > 0
