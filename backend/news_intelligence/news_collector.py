from typing import List
from .crypto_news_feed import NewsItem
from .rss_collector import RSSNewsCollector
from .exchange_announcements import ExchangeAnnouncementCollector
from .news_deduplicator import NewsDeduplicator

class MasterNewsCollector:
    """Master Ingestion Collector Aggregating RSS & Exchange Announcements."""

    def __init__(self):
        self.rss_collector = RSSNewsCollector()
        self.ann_collector = ExchangeAnnouncementCollector()
        self.deduplicator = NewsDeduplicator()

    def collect_all_news(self) -> List[NewsItem]:
        rss_items = self.rss_collector.fetch_rss_news()
        ann_items = self.ann_collector.fetch_announcements()

        combined = rss_items + ann_items
        unique = self.deduplicator.deduplicate(combined)
        return unique
