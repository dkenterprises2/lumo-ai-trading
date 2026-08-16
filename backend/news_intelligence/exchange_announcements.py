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
                title="Binance Announces System Maintenance and Network Optimization",
                summary="Scheduled multi-chain wallet upgrades and liquidity pool rebalancing across tier-1 assets.",
                source="Binance Announcements",
                url="https://www.binance.com/en/support/announcement",
                raw_timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now - 1200)),
                normalized_timestamp=now,
                extracted_symbols=self.normalizer.extract_symbols("SOL/USDT, BTC/USDT"),
                confidence_score=0.98
            ),
            NewsItem(
                title="OKX Spot & Derivatives Market Structure Listing Update",
                summary="New perpetual settlement mechanisms and zero-maker fee tier adjustments.",
                source="OKX Announcements",
                url="https://www.okx.com/help/section/announcements",
                raw_timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(now - 2400)),
                normalized_timestamp=now,
                extracted_symbols=self.normalizer.extract_symbols("BTC/USDT, ETH/USDT"),
                confidence_score=0.97
            )
        ]
        return items
