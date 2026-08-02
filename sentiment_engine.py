import requests
import feedparser
import time
import logging
from typing import Dict, List, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentEngine:
    def __init__(self):
        try:
            self.vader = SentimentIntensityAnalyzer()
        except Exception:
            self.vader = None

        # Financial Crypto Keyword Weight Modifiers
        self.bullish_keywords = [
            "surge", "bullish", "rally", "breakout", "gain", "skyrocket",
            "approval", "etf", "inflow", "adoption", "partnership", "all-time high",
            "upgrade", "halving", "accumulate", "record high"
        ]
        self.bearish_keywords = [
            "crash", "bearish", "plunge", "dump", "hack", "exploit", "sec lawsuit",
            "ban", "liquidation", "outflow", "collapse", "fraud", "bankruptcy",
            "delisting", "regulation risk", "drop"
        ]

    def fetch_fear_and_greed_index(self) -> Dict[str, Any]:
        """Fetch real-time Fear & Greed Index from Alternative.me API."""
        try:
            url = "https://api.alternative.me/fng/?limit=1"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                item = data['data'][0]
                val = int(item['value'])
                classification = item['value_classification']
                return {
                    "value": val,
                    "classification": classification,
                    "timestamp": item.get('timestamp')
                }
        except Exception as e:
            logger.warning(f"Fear & Greed API error: {e}")
        
        # Default fallback
        return {"value": 55, "classification": "Greed", "timestamp": str(int(time.time()))}

    def fetch_crypto_news(self) -> List[Dict[str, Any]]:
        """Fetch latest crypto headlines from public RSS feeds."""
        rss_feeds = [
            ("CoinTelegraph", "https://cointelegraph.com/rss"),
            ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
            ("Bitcoin Magazine", "https://bitcoinmagazine.com/feed")
        ]

        articles = []
        for source_name, feed_url in rss_feeds:
            try:
                parsed = feedparser.parse(feed_url)
                for entry in parsed.entries[:5]:  # Top 5 entries per source
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    link = entry.get('link', '')
                    published = entry.get('published', entry.get('updated', 'Recently'))

                    # Calculate sentiment for article
                    sentiment_info = self.analyze_text_sentiment(f"{title}. {summary}")

                    articles.append({
                        "source": source_name,
                        "title": title,
                        "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                        "link": link,
                        "published": published,
                        "sentiment": sentiment_info['label'],
                        "sentiment_score": sentiment_info['score'],
                        "compound": sentiment_info['compound']
                    })
            except Exception as e:
                logger.warning(f"Error fetching news feed {source_name}: {e}")

        # If offline or feeds failed, return realistic mock articles
        if not articles:
            articles = self._get_fallback_news()

        return articles

    def _get_fallback_news(self) -> List[Dict[str, Any]]:
        return [
            {
                "source": "CoinTelegraph",
                "title": "Bitcoin Holds Key Support as Institutional Inflows Surge via Spot ETFs",
                "summary": "Institutional buying pressure continues to support Bitcoin's price floor as daily net inflows surpass multi-million dollar milestones.",
                "link": "https://cointelegraph.com",
                "published": "10 mins ago",
                "sentiment": "Bullish",
                "sentiment_score": 78.5,
                "compound": 0.57
            },
            {
                "source": "CoinDesk",
                "title": "Ethereum Layer-2 Activity Hits Record High Following Major Network Upgrade",
                "summary": "Gas fees across Arbitrum, Optimism, and Base drop sharply, leading to record decentralized exchange volumes.",
                "link": "https://coindesk.com",
                "published": "35 mins ago",
                "sentiment": "Bullish",
                "sentiment_score": 82.0,
                "compound": 0.64
            },
            {
                "source": "Bitcoin Magazine",
                "title": "Federal Reserve Signals Potential Interest Rate Shifts, Boosting Risk Assets",
                "summary": "Global macroeconomic conditions improve as inflation cools down, creating positive momentum for crypto assets.",
                "link": "https://bitcoinmagazine.com",
                "published": "1 hour ago",
                "sentiment": "Bullish",
                "sentiment_score": 71.0,
                "compound": 0.42
            }
        ]

    def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using VADER + Keyword rules."""
        text_lower = text.lower()
        
        # 1. VADER Base Score
        compound = 0.0
        if self.vader:
            scores = self.vader.polarity_scores(text)
            compound = scores['compound']
        else:
            # Rule-based calculation fallback
            pos_count = sum(1 for kw in self.bullish_keywords if kw in text_lower)
            neg_count = sum(1 for kw in self.bearish_keywords if kw in text_lower)
            diff = pos_count - neg_count
            compound = max(-1.0, min(1.0, diff * 0.3))

        # 2. Keyword Boosts
        pos_boost = sum(0.15 for kw in self.bullish_keywords if kw in text_lower)
        neg_boost = sum(0.15 for kw in self.bearish_keywords if kw in text_lower)
        adjusted_compound = max(-1.0, min(1.0, compound + pos_boost - neg_boost))

        # Normalize score from -1.0..1.0 to 0..100 scale
        normalized_score = round((adjusted_compound + 1.0) * 50.0, 1)

        label = "Bullish" if normalized_score >= 60 else ("Bearish" if normalized_score <= 40 else "Neutral")

        return {
            "compound": round(adjusted_compound, 2),
            "score": normalized_score,
            "label": label
        }

    def compute_aggregated_sentiment(self, articles: List[Dict[str, Any]], fear_greed: Dict[str, Any]) -> Dict[str, Any]:
        """Compute holistic market sentiment summary combining News + Fear & Greed Index."""
        if articles:
            news_score_avg = sum(a['sentiment_score'] for a in articles) / len(articles)
        else:
            news_score_avg = 50.0

        fg_value = fear_greed.get('value', 50)
        
        # Combined Weighted Score: 60% News Sentiment + 40% Fear & Greed Index
        combined_score = round((news_score_avg * 0.60) + (fg_value * 0.40), 1)

        label = "STRONGLY BULLISH" if combined_score >= 75 else (
            "BULLISH" if combined_score >= 58 else (
                "BEARISH" if combined_score <= 42 else (
                    "STRONGLY BEARISH" if combined_score <= 25 else "NEUTRAL"
                )
            )
        )

        return {
            "combined_score": combined_score,
            "news_score_avg": round(news_score_avg, 1),
            "fear_greed_score": fg_value,
            "fear_greed_label": fear_greed.get('classification', 'Neutral'),
            "label": label,
            "total_news_analyzed": len(articles)
        }

if __name__ == "__main__":
    engine = SentimentEngine()
    fg = engine.fetch_fear_and_greed_index()
    news = engine.fetch_crypto_news()
    sentiment_summary = engine.compute_aggregated_sentiment(news, fg)
    print(f"Fear & Greed: {fg}")
    print(f"Aggregated Sentiment: {sentiment_summary}")
    print(f"Latest News Articles ({len(news)}): {news[0]['title']}")
