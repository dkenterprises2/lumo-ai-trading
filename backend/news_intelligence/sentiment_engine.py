from typing import List
from .sentiment_models import SentimentSnapshot
from .crypto_news_feed import NewsItem

class NewsSentimentEngine:
    """Aggregates Multi-Source Headline, Article & Social Sentiment Scores."""

    POSITIVE_WORDS = ["APPROVE", "APPROVED", "BULLISH", "SURGE", "LISTING", "PARTNER", "GAIN", "RALLY", "RECORD"]
    NEGATIVE_WORDS = ["HACK", "EXPLOIT", "REJECT", "DELIST", "DROP", "DOWNTURN", "CRASH", "LAWSUIT", "SUED", "DEPEG", "BANKRUPT"]

    def compute_text_sentiment(self, text: str) -> float:
        text_upper = text.upper()
        pos_count = sum(1 for w in self.POSITIVE_WORDS if w in text_upper)
        neg_count = sum(1 for w in self.NEGATIVE_WORDS if w in text_upper)

        tot = pos_count + neg_count
        if tot == 0:
            return 0.0

        score = (pos_count - neg_count) / float(tot)
        return round(max(-1.0, min(1.0, score)), 2)

    def aggregate_sentiment(
        self,
        symbol: str = "BTC/USDT",
        news_items: List[NewsItem] = None,
        social_score: float = 0.50
    ) -> SentimentSnapshot:
        headline_scores = []
        if news_items:
            for item in news_items:
                if not symbol or symbol in item.extracted_symbols:
                    s = self.compute_text_sentiment(item.title)
                    headline_scores.append(s)

        avg_headline = sum(headline_scores) / float(len(headline_scores)) if headline_scores else 0.40
        avg_article = avg_headline * 0.90

        composite = (avg_headline * 0.40) + (avg_article * 0.30) + (social_score * 0.30)
        composite = round(max(-1.0, min(1.0, composite)), 2)

        label = "NEUTRAL"
        if composite >= 0.60:
            label = "VERY_BULLISH"
        elif composite >= 0.20:
            label = "BULLISH"
        elif composite <= -0.60:
            label = "VERY_BEARISH"
        elif composite <= -0.20:
            label = "BEARISH"

        return SentimentSnapshot(
            symbol=symbol,
            headline_sentiment=round(avg_headline, 2),
            article_sentiment=round(avg_article, 2),
            social_sentiment=round(social_score, 2),
            composite_sentiment=composite,
            label=label
        )
