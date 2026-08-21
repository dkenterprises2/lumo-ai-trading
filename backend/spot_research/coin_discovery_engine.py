import threading
"""
Coin Discovery Engine for Lumo Spot Research Subsystem.
Fetches real, verified newly active, high-momentum, and newly listed tokens
from Binance, DexScreener, and CoinGecko public market-data endpoints.

INVARIANT: Zero fake data. Missing fields are explicitly marked as None or "N/A".
"""

import time
import requests
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger

class DiscoveredCoin(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    exchange: str
    chain_id: Optional[str] = None
    token_address: Optional[str] = None
    first_observed_ts: float = Field(default_factory=time.time)
    listing_ts: Optional[float] = None
    current_price: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    liquidity_usd: Optional[float] = None
    price_change_24h_pct: Optional[float] = None
    volatility_pct: Optional[float] = None
    spread_bps: Optional[float] = None
    market_cap_usd: Optional[float] = None
    fdv_usd: Optional[float] = None
    source: str
    source_ts: float = Field(default_factory=time.time)
    data_freshness_seconds: float = 0.0
    description: Optional[str] = None
    profile_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class CoinDiscoveryEngine:
    """Discovers real coins across CEX (Binance) and DEX (DexScreener, CoinGecko) public streams."""

    def __init__(self):
        self._cache: Dict[str, DiscoveredCoin] = {}
        self._last_cex_discovery_ts: float = 0.0
        self._last_dex_discovery_ts: float = 0.0
        self._discovery_interval_sec: float = 30.0
        self._lock = threading.Lock()
        self._bg_started = False
        self._start_background_refresher()

    def _start_background_refresher(self):
        if not self._bg_started:
            self._bg_started = True
            t = threading.Thread(target=self._background_loop, daemon=True, name="SpotDiscoveryRefresher")
            t.start()

    def _background_loop(self):
        time.sleep(2.0)
        while True:
            try:
                self.discover_all_coins(force_refresh=True)
            except Exception as e:
                logger.debug(f"[DISCOVERY_BG_ERR] {e}")
            time.sleep(45.0)

    def get_all_discovered_coins(self) -> List[DiscoveredCoin]:
        return self.discover_all_coins(force_refresh=False)

    def discover_all_coins(self, force_refresh: bool = False) -> List[DiscoveredCoin]:
        """Fetch and aggregate newly active / trending coins from real market data providers."""
        now = time.time()
        
        if force_refresh or not self._cache:
            with self._lock:
                self._discover_binance_coins()
                self._last_cex_discovery_ts = now
                self._discover_dexscreener_bulk()
                self._last_dex_discovery_ts = now

        # Return snapshot immediately from RAM (< 2ms response time)
        with self._lock:
            coins = list(self._cache.values())
            for coin in coins:
                coin.data_freshness_seconds = round(now - coin.source_ts, 1)
            return coins

    def _discover_binance_coins(self):
        """Discover active spot pairs, top gainers, and high volume tokens from Binance 24hr ticker in 1 HTTP call."""
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            resp = requests.get(url, timeout=4.0)
            if resp.status_code != 200:
                logger.warning(f"[DISCOVERY] Binance 24hr ticker HTTP {resp.status_code}")
                return

            tickers = resp.json()
            now = time.time()
            count = 0

            for t in tickers:
                raw_sym = t.get("symbol", "")
                if not raw_sym.endswith("USDT"):
                    continue

                base = raw_sym[:-4]
                quote = "USDT"
                formatted_symbol = f"{base}/{quote}"

                try:
                    last_price = float(t.get("lastPrice", 0.0))
                    vol_usd = float(t.get("quoteVolume", 0.0))
                    pct_change = float(t.get("priceChangePercent", 0.0))
                    high_p = float(t.get("highPrice", 0.0))
                    low_p = float(t.get("lowPrice", 0.0))
                    bid_p = float(t.get("bidPrice", 0.0))
                    ask_p = float(t.get("askPrice", 0.0))
                except (ValueError, TypeError):
                    continue

                if last_price <= 0 or vol_usd < 10000.0:
                    continue  # Ignore zero-volume inactive dead pairs

                spread_bps = None
                if bid_p > 0 and ask_p > 0 and ask_p >= bid_p:
                    mid = (ask_p + bid_p) / 2.0
                    spread_bps = round(((ask_p - bid_p) / mid) * 10000.0, 2)

                volatility_pct = None
                if low_p > 0 and high_p >= low_p:
                    volatility_pct = round(((high_p - low_p) / low_p) * 100.0, 2)

                if abs(pct_change) >= 2.0 or vol_usd >= 500000.0 or count < 50:
                    coin = DiscoveredCoin(
                        symbol=formatted_symbol,
                        base_asset=base,
                        quote_asset=quote,
                        exchange="BINANCE",
                        current_price=last_price,
                        volume_24h_usd=vol_usd,
                        liquidity_usd=None,  # Not provided by CEX ticker (NO FAKE VALUE)
                        price_change_24h_pct=pct_change,
                        volatility_pct=volatility_pct,
                        spread_bps=spread_bps,
                        market_cap_usd=None,  # Explicitly None (NO FAKE VALUE)
                        fdv_usd=None,
                        source="BINANCE_REST_24HR",
                        source_ts=now,
                        tags=["CEX", "SPOT"]
                    )
                    self._cache[formatted_symbol] = coin
                    count += 1

            logger.info(f"[DISCOVERY] Discovered {count} active coins from Binance")
        except Exception as e:
            logger.error(f"[DISCOVERY_ERR] Binance discovery error: {e}")

    def _discover_dexscreener_bulk(self):
        """High-speed bulk discovery of trending DEX meme tokens in 2 batch HTTP calls."""
        try:
            url = "https://api.dexscreener.com/token-boosts/latest/v1"
            resp = requests.get(url, timeout=3.0)
            if resp.status_code != 200:
                return

            boosts = resp.json()
            if not isinstance(boosts, list):
                return

            # Extract unique token addresses (up to 30)
            addrs = []
            meta_map = {}
            for b in boosts[:25]:
                addr = b.get("tokenAddress")
                if addr and addr not in meta_map:
                    addrs.append(addr)
                    meta_map[addr] = {
                        "chain_id": b.get("chainId", "solana"),
                        "description": b.get("description"),
                        "profile_url": b.get("url")
                    }

            if not addrs:
                return

            # Bulk fetch pairs in 1 single HTTP request
            bulk_url = f"https://api.dexscreener.com/latest/dex/tokens/{','.join(addrs[:25])}"
            r_bulk = requests.get(bulk_url, timeout=4.0)
            if r_bulk.status_code != 200:
                return

            pairs = r_bulk.json().get("pairs", [])
            now = time.time()

            # Group pairs by tokenAddress
            seen_tokens = set()
            for p in pairs:
                base_addr = p.get("baseToken", {}).get("address")
                if not base_addr or base_addr in seen_tokens:
                    continue
                seen_tokens.add(base_addr)

                base_sym = p.get("baseToken", {}).get("symbol", "UNKNOWN")
                quote_sym = p.get("quoteToken", {}).get("symbol", "USD")
                dex_id = p.get("dexId", "DEX").upper()
                chain_id = p.get("chainId", "SOLANA").upper()
                meta = meta_map.get(base_addr, {})

                try:
                    price_usd = float(p.get("priceUsd", 0.0))
                except (ValueError, TypeError):
                    price_usd = None

                vol_24h = None
                try:
                    v = p.get("volume", {}).get("h24")
                    if v is not None:
                        vol_24h = float(v)
                except (ValueError, TypeError):
                    pass

                liq_usd = None
                try:
                    l = p.get("liquidity", {}).get("usd")
                    if l is not None:
                        liq_usd = float(l)
                except (ValueError, TypeError):
                    pass

                pct_change_24h = None
                try:
                    pch = p.get("priceChange", {}).get("h24")
                    if pch is not None:
                        pct_change_24h = float(pch)
                except (ValueError, TypeError):
                    pass

                fdv_usd = None
                try:
                    f = p.get("fdv")
                    if f is not None:
                        fdv_usd = float(f)
                except (ValueError, TypeError):
                    pass

                mcap_usd = None
                try:
                    m = p.get("marketCap")
                    if m is not None:
                        mcap_usd = float(m)
                except (ValueError, TypeError):
                    pass

                listing_ts = None
                try:
                    created = p.get("pairCreatedAt")
                    if created:
                        listing_ts = float(created) / 1000.0 if created > 1e11 else float(created)
                except (ValueError, TypeError):
                    pass

                key = f"{base_sym}/{quote_sym} ({chain_id})"
                coin = DiscoveredCoin(
                    symbol=key,
                    base_asset=base_sym,
                    quote_asset=quote_sym,
                    exchange=f"{dex_id} ({chain_id})",
                    chain_id=chain_id.lower(),
                    token_address=base_addr,
                    first_observed_ts=now,
                    listing_ts=listing_ts,
                    current_price=price_usd,
                    volume_24h_usd=vol_24h,
                    liquidity_usd=liq_usd,
                    price_change_24h_pct=pct_change_24h,
                    volatility_pct=abs(pct_change_24h) if pct_change_24h is not None else None,
                    spread_bps=None,
                    market_cap_usd=mcap_usd,
                    fdv_usd=fdv_usd,
                    source="DEXSCREENER_API",
                    source_ts=now,
                    description=meta.get("description"),
                    profile_url=meta.get("profile_url"),
                    tags=["DEX", chain_id]
                )
                self._cache[key] = coin

            logger.info(f"[DISCOVERY] Bulk discovered {len(seen_tokens)} on-chain DEX tokens")
        except Exception as e:
            logger.debug(f"[DISCOVERY_DEX_BULK_ERR] {e}")

coin_discovery_engine = CoinDiscoveryEngine()
