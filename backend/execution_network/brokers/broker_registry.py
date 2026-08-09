from typing import Dict, Any, List

class MultiBrokerRegistry:
    """Multi-Broker Gateway & Connectivity Registry."""

    def __init__(self):
        self._brokers = [
            {"broker_id": "binance_main", "name": "Binance Institutional", "protocol": "REST_WS", "status": "CONNECTED"},
            {"broker_id": "bybit_main", "name": "Bybit Prime", "protocol": "REST_WS", "status": "CONNECTED"},
            {"broker_id": "okx_main", "name": "OKX Institutional", "protocol": "FIX_4_4", "status": "CONNECTED"},
            {"broker_id": "paper_sim", "name": "Lumo Paper Trading Simulator", "protocol": "INTERNAL", "status": "ACTIVE"}
        ]

    def list_brokers(self) -> List[Dict[str, Any]]:
        return self._brokers

    def connect_broker(self, broker_id: str) -> Dict[str, Any]:
        return {"broker_id": broker_id, "status": "CONNECTED", "latency_ms": 12.4}

broker_registry = MultiBrokerRegistry()
