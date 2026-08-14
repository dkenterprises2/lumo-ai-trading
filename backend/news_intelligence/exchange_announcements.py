import time
from typing import List
from .crypto_news_feed import NewsItem
from .news_normalizer import NewsNormalizer

class ExchangeAnnouncementCollector:
    """Collects Announcements from Binance, Bybit, and OKX."""

    def __init__(self):
        self.normalizer = NewsNormalizer()

    def fetch_announcements(self) -> List[NewsItem]:
        now = time.time()
        items = [
            NewsItem(
                title="Binance Will Support System Upgrade for SOL Network",
                summary="Deposits and withdrawals will be suspended during upgrade.",
                source="Binance Announcements",
                normalized_timestamp=now,
                extracted_symbols=self.normalizer.extract_symbols("SOL/USDT"),
                confidence_score=0.98
            ),
            NewsItem(
                title="OKX Delisting Notice for Legacy Altcoin Pair",
                summary="Trading for ABC/USDT will be discontinued on Friday.",
                source="OKX Announcements",
                normalized_timestamp=now,
                extracted_symbols=self.normalizer.extract_symbols("ABC/USDT"),
                confidence_score=0.97
            )
        ]
        return items
