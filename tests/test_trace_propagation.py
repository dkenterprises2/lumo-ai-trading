import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.shared.tracing import trace_propagator

def test_trace_id_propagation():
    headers = {"X-Trace-Id": "trace-abc123xyz"}
    trace_id = trace_propagator.get_or_create_trace_id(headers)
    assert trace_id == "trace-abc123xyz"

    new_trace_id = trace_propagator.get_or_create_trace_id({})
    assert new_trace_id.startswith("trace-")
