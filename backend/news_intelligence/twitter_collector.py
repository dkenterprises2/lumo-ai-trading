import time
from typing import List
from .crypto_news_feed import NewsItem
from .news_normalizer import NewsNormalizer

class TwitterNewsCollector:
    """Collects Social & Twitter News Items."""

    def __init__(self):
        self.normalizer = NewsNormalizer()

    def fetch_social_tweets(self) -> List[NewsItem]:
        now = time.time()
        return [
            NewsItem(
                title="BlackRock Analyst Hints at Impending Solana Spot ETF Filing",
                summary="Social sentiment spiking around $SOL ETF rumors.",
                source="Twitter/X",
                normalized_timestamp=now,
                extracted_symbols=self.normalizer.extract_symbols("SOL/USDT"),
                confidence_score=0.75
            )
        ]
