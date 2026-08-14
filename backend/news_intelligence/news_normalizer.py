import re
import time
from typing import List, Any

class NewsNormalizer:
    """Normalizes News Item Timestamps & Extracts Target Crypto Symbols."""

    KNOWN_SYMBOLS = [
        "BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "DOT", "LINK",
        "MATIC", "ATOM", "NEAR", "APT", "SUI", "OP", "ARB", "LTC", "ETC", "XLM",
        "FIL", "INJ", "TIA", "UNI", "ICP", "FET", "RNDR", "PEPE", "SHIB", "FLOKI"
    ]

    NAME_MAP = {
        "BITCOIN": "BTC/USDT",
        "ETHEREUM": "ETH/USDT",
        "SOLANA": "SOL/USDT",
        "RIPPLE": "XRP/USDT",
        "CARDANO": "ADA/USDT",
        "DOGECOIN": "DOGE/USDT",
        "AVALANCHE": "AVAX/USDT",
        "POLKADOT": "DOT/USDT",
        "CHAINLINK": "LINK/USDT",
        "POLYGON": "MATIC/USDT"
    }

    def extract_symbols(self, text: str) -> List[str]:
        found = set()
        text_upper = text.upper()

        # Check full coin names first
        for name, pair in self.NAME_MAP.items():
            if re.search(r'\b' + re.escape(name) + r'\b', text_upper):
                found.add(pair)
        
        # Check ticker symbol patterns
        for sym in self.KNOWN_SYMBOLS:
            pattern = r'\b(' + re.escape(sym) + r'|\$' + re.escape(sym) + r'|' + re.escape(sym) + r'/USDT)\b'
            if re.search(pattern, text_upper):
                found.add(f"{sym}/USDT")

        if not found:
            found.add("BTC/USDT")

        return sorted(list(found))

    def normalize_timestamp(self, ts_input: Any = None) -> float:
        if isinstance(ts_input, (int, float)) and ts_input > 0:
            return float(ts_input)
        return time.time()
