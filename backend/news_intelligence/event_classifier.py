import re
from typing import Tuple
from .event_taxonomy import CryptoEventType, EventImpactSeverity

class EventClassifier:
    """Classifies Raw Text Headlines into Crypto Event Taxonomies."""

    KEYWORD_PATTERNS = [
        (r'\b(ETF APPROVAL|SPOT ETF APPROVED|ETFS APPROVED|ETF INFLOWS|ETF TRADING)\b', CryptoEventType.ETF_APPROVAL, EventImpactSeverity.HIGH),
        (r'\b(ETF REJECTED|REJECTION|DENIED|ETF DELAY)\b', CryptoEventType.ETF_REJECTION, EventImpactSeverity.HIGH),
        (r'\b(HACK|EXPLOIT|DRAINED|ATTACK|VULNERABILITY|ROGUE AGENT)\b', CryptoEventType.EXCHANGE_HACK, EventImpactSeverity.CRITICAL),
        (r'\b(OUTAGE|MAINTENANCE|SUSPENDED|DOWN|HALTED)\b', CryptoEventType.EXCHANGE_OUTAGE, EventImpactSeverity.HIGH),
        (r'\b(LISTING|LISTED|SUPPORT SPOT|TRADING OPEN|NEW TOKEN)\b', CryptoEventType.TOKEN_LISTING, EventImpactSeverity.MODERATE),
        (r'\b(DELISTING|DELIST|REMOVED|DISCONTINUED)\b', CryptoEventType.TOKEN_DELISTING, EventImpactSeverity.HIGH),
        (r'\b(PARTNERSHIP|PARTNER|COLLABORATION|ALLIANCE)\b', CryptoEventType.PARTNERSHIP, EventImpactSeverity.MODERATE),
        (r'\b(SUED|LAWSUIT|SEC CHARGES|REGULATORY|DOJ|CONGRESS|TRUMP|CLARITY ACT|LEGAL|COURT)\b', CryptoEventType.POLICY_REGULATORY, EventImpactSeverity.HIGH),
        (r'\b(WHALE|TRANSFERRED|TRANSFERS|LARGE MOVEMENT|INFLOW|OUTFLOW|COLD STORAGE)\b', CryptoEventType.WHALE_MOVEMENT, EventImpactSeverity.MODERATE),
        (r'\b(DEPEG|DEPEGGED|STABLECOIN LOSS|USDT|USDC)\b', CryptoEventType.STABLECOIN_DEPEG, EventImpactSeverity.CRITICAL),
        (r'\b(BANKRUPTCY|CHAPTER 11|INSOLVENT|LIQUIDATION)\b', CryptoEventType.BANKRUPTCY, EventImpactSeverity.CRITICAL),
        (r'\b(TOKENIZED|TOKENIZATION|INSTITUTIONAL|IPO|PRE-IPO|TRADFI|UBS|WALL STREET|GOLDMAN|BLACKROCK)\b', CryptoEventType.INSTITUTIONAL_ADOPTION, EventImpactSeverity.HIGH),
        (r'\b(AI|MODEL|CHATGPT|ANTHROPIC|OPENAI|ALIBABA|METAVERSE|DEEPSEEK|INTELLIGENCE|AGENT)\b', CryptoEventType.AI_CRYPTO_INNOVATION, EventImpactSeverity.MODERATE),
        (r'\b(DEFI|BRIDGE|TVL|YIELD|STAKING|LIQUIDITY|DEX|UNISWAP|AAVE|SOLANA DEFI)\b', CryptoEventType.DEFI_INTELLIGENCE, EventImpactSeverity.MODERATE),
        (r'\b(MINING|RIGS|HASHRATE|MINERS|BITCOIN MINING|HALVING|RIOT)\b', CryptoEventType.MINING_INFRASTRUCTURE, EventImpactSeverity.HIGH),
        (r'\b(SURGE|RALLY|CRASH|PLUNGE|BULL|BEAR|ALL-TIME HIGH|ATH|RECORD HIGH|PRICE UPDATE)\b', CryptoEventType.MARKET_MOMENTUM, EventImpactSeverity.MODERATE),
        (r'\b(DERIVATIVES|PERPETUALS|FUTURES|OPTIONS|BYBIT|BINANCE|COINBASE|OKX)\b', CryptoEventType.EXCHANGE_DERIVATIVES, EventImpactSeverity.MODERATE)
    ]

    def classify_text(self, text: str) -> Tuple[CryptoEventType, EventImpactSeverity]:
        text_upper = text.upper()
        for pattern, event_type, severity in self.KEYWORD_PATTERNS:
            if re.search(pattern, text_upper):
                return event_type, severity

        return CryptoEventType.MARKET_ANALYSIS, EventImpactSeverity.MODERATE
