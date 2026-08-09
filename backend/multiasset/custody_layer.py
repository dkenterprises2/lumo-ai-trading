from typing import Dict, Any, List

class CustodyLayer:
    """Custody Account & Settlement Vault Abstraction Layer."""

    @staticmethod
    def get_custody_accounts() -> List[Dict[str, Any]]:
        return [
            {"custodian": "Fireblocks", "account_type": "MPC_VAULT", "balance_usd": 3200000.0},
            {"custodian": "BitGo", "account_type": "COLD_STORAGE", "balance_usd": 1800000.0}
        ]

custody_layer = CustodyLayer()
