from typing import List
from .crypto_news_feed import NewsItem

class NewsDeduplicator:
    """Eliminates Duplicate News Articles Across RSS & Social Feeds."""

    def deduplicate(self, news_items: List[NewsItem], similarity_threshold: float = 0.70) -> List[NewsItem]:
        unique_items = []
        seen_titles = []

        for item in news_items:
            clean_title = item.title.lower().strip()
            is_dup = False
            for seen in seen_titles:
                # Jaccard similarity check on words
                words1 = set(clean_title.split())
                words2 = set(seen.split())
                if not words1 or not words2:
                    continue
                intersection = words1.intersection(words2)
                union = words1.union(words2)
                jaccard = len(intersection) / float(len(union))
                if jaccard >= similarity_threshold:
                    is_dup = True
                    break

            if not is_dup:
                seen_titles.append(clean_title)
                unique_items.append(item)

        return unique_items
