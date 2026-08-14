import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

@dataclass
class WhaleTransfer:
    symbol: str
    amount: float
    amount_usd: float
    from_address: str
    to_address: str
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class WhaleTracker:
    """Tracks Large On-Chain Whale Transfers & Exchange Inflows/Outflows."""

    def fetch_recent_whale_transfers(self) -> List[WhaleTransfer]:
        now = time.time()
        return [
            WhaleTransfer(
                symbol="BTC/USDT",
                amount=5000.0,
                amount_usd=592250000.0,
                from_address="Unknown Wallet",
                to_address="Binance Deposit Wallet",
                timestamp=now
            ),
            WhaleTransfer(
                symbol="ETH/USDT",
                amount=25000.0,
                amount_usd=105000000.0,
                from_address="Coinbase Custody",
                to_address="Unknown Institutional Wallet",
                timestamp=now - 300.0
            )
        ]
