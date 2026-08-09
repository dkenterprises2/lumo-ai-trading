import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.websocket_gateway.gateway import websocket_gateway
from services.websocket_gateway.connection_registry import connection_registry

def test_websocket_gateway_cluster():
    websocket_gateway.handle_connect("ORG-101", "conn-1")
    conns = connection_registry.get_channel_connections("ORG-101")
    assert "conn-1" in conns

    websocket_gateway.handle_disconnect("ORG-101", "conn-1")
    conns_after = connection_registry.get_channel_connections("ORG-101")
    assert "conn-1" not in conns_after
