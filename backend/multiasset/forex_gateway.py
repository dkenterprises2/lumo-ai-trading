from typing import Dict, Any

class ForexGateway:
    """Forex Spot & Forward Gateway Abstraction."""

    @staticmethod
    def get_status() -> Dict[str, Any]:
        return {"gateway": "FOREX", "status": "CONNECTED_SIMULATED"}

forex_gateway = ForexGateway()
