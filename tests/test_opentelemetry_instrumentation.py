import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.opentelemetry_tracer import opentelemetry_tracer

def test_opentelemetry_headers():
    headers = opentelemetry_tracer.inject_trace_context("abc123trace")
    assert "traceparent" in headers
    assert "abc123trace" in headers["traceparent"]
