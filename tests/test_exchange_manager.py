import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.exchange.exchange_manager import exchange_manager_v21

def test_exchange_manager_connect_and_status():
    user_id = 701
    adapter = exchange_manager_v21.connect_exchange(
        user_id=user_id,
        exchange_name="BINANCE_SPOT",
        api_key="test_api_key_12345",
        secret_key="test_secret_key_67890",
        testnet=True
    )

    assert adapter.get_exchange_name() == "BINANCE_TESTNET"
    status_info = exchange_manager_v21.get_exchange_status(user_id)
    assert status_info["user_id"] == user_id
    assert len(status_info["exchanges"]) >= 1
