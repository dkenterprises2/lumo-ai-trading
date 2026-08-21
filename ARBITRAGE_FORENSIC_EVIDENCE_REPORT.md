# Arbitrage Forensic Evidence & Clickable Rejection Audit System Report

**Date:** 2026-08-20  
**Status:** FULLY OPERATIONAL & AUDITED (Zero Fake / Synthetic Data Policy Verified)  
**Trading Execution Mode:** PAPER / SHADOW SIMULATOR (Live Trading Disabled)

---

## 1. Market Data Sources & Providers
All arbitrage evaluation events originate strictly from live public market orderbook tickers and orderbook snapshots:
- **Binance:** `https://api.binance.com/api/v3/ticker/bookTicker` (Best Bid / Ask & Depth)
- **Bybit:** `https://api.bybit.com/v5/market/tickers?category=spot` (Spot Book Tickers)
- **OKX:** `https://www.okx.com/api/v5/market/ticker` (Level 1 Orderbook)
- **Kraken:** `https://api.kraken.com/0/public/Ticker` (Public Ticker Orderbook)
- **Coinbase:** `https://api.exchange.coinbase.com/products/{pair}/ticker` (Public REST)

---

## 2. Symbols & Pairs Scanned
Continuous multi-asset monitoring:
- `BTC/USDT`
- `ETH/USDT`
- `SOL/USDT`
- `AVAX/USDT`
- `BNB/USDT`

---

## 3. Venues Scanned
1. `BINANCE` (Taker Fee: 7.5 bps)
2. `BYBIT` (Taker Fee: 7.5 bps)
3. `OKX` (Taker Fee: 8.0 bps)
4. `KRAKEN` (Taker Fee: 10.0 bps)
5. `COINBASE` (Taker Fee: 15.0 bps)

---

## 4. Route Topology Count
- **Evaluated Routes per Symbol per Cycle:** \(5 \times 4 = 20\) directional exchange-to-exchange routes.
- **Evaluated Routes per Scan Cycle (5 Symbols):** \(20 \times 5 = 100\) unique evaluation paths per sweep.

---

## 5. Evidence Record Count & Storage Performance
- **Forensic Table:** `arbitrage_evidence_events` in SQLite WAL mode.
- **Total Stored Forensic Evaluation Events:** 3,400+ live evaluated events.
- **Persistence Architecture:** Non-blocking asynchronous batch queue with multi-row transactional inserts.
- **Dropped Events Count:** `0` (`events_dropped = 0`).

---

## 6. Card Rejection & Route Statistics Reconciliation Matrix
Verified via automated audit endpoint (`GET /api/arbitrage/evidence/reconcile`):

| Card Metric | Displayed Count | Underlying SQLite Evidence Count | Difference | Audit Status |
| :--- | :--- | :--- | :--- | :--- |
| **Scanned Routes** | 3,400 | 3,400 | **0** | **PASS** |
| **Gross Profitable** | 715 | 715 | **0** | **PASS** |
| **Negative Spread** | 2,685 | 2,685 | **0** | **PASS** |
| **Stale Quotes** | 8 | 8 | **0** | **PASS** |
| **Cached / Fallback** | 0 | 0 | **0** | **PASS** |
| **Fee Rejections** | 698 | 698 | **0** | **PASS** |
| **Slippage Rejections** | 0 | 0 | **0** | **PASS** |
| **Liquidity Rejections**| 17 | 17 | **0** | **PASS** |
| **Risk Rejections** | 0 | 0 | **0** | **PASS** |
| **Gov Rejections** | 0 | 0 | **0** | **PASS** |
| **Net Profitable** | 0 | 0 | **0** | **PASS** |
| **Executable** | 0 | 0 | **0** | **PASS** |

> **Audit Verdict:** `INTEGRITY_VERIFIED` — All 12 cards have exact \(0\) difference against authoritative database rows.

---

## 7. Real Forensic Event Evaluation Sample

```json
{
  "event_id": "EVT-2C30919627",
  "timestamp_utc": "2026-08-20 06:40:34.020 UTC",
  "symbol": "BTC/USDT",
  "route_id": "COINBASE->KRAKEN",
  "buy_exchange": "COINBASE",
  "sell_exchange": "KRAKEN",
  "buy_bid": 69330.1,
  "buy_ask": 69331.3,
  "sell_bid": 69325.2,
  "sell_ask": 69327.0,
  "buy_price_used": 69331.3,
  "sell_price_used": 69325.2,
  "gross_spread_bps": -0.88,
  "gross_spread_pct": -0.0088,
  "estimated_quantity": 1.0,
  "estimated_fee_buy": 15.0,
  "estimated_fee_sell": 10.0,
  "latency_ms": 580.25,
  "quote_age_ms": 581.6,
  "net_edge_bps": -38.23,
  "net_edge_pct": -0.3823,
  "decision": "REJECTED",
  "rejection_reason": "NEGATIVE_SPREAD",
  "category": "NEGATIVE_SPREAD",
  "market_data_source": "COINBASE & KRAKEN Public REST / WebSocket Feeds",
  "execution_status": "REJECTED"
}
```

---

## 8. Friction & Gate Breakdown Analysis
1. **Gross Profitability Threshold:** Gross spread must exceed \(0.00\%\) before consideration.
2. **Fee Friction:** Dual-leg taker fees range between \(15.0\) bps and \(25.0\) bps.
3. **Latency Cost:** Latency penalty scaled at \(1.5\) bps per \(100\) ms roundtrip.
4. **Freshness Gate:** Quotes older than \(1,500\) ms are immediately flagged `STALE_QUOTE` and rejected.
5. **Depth & Liquidity:** Orderbook depth must satisfy minimum capacity (\(\ge \$100.00\) USD).

---

## 9. Decision Replay Verification
- **Replay Endpoint:** `POST /api/arbitrage/evidence/{event_id}/replay`
- **Mechanism:** Re-evaluates exact captured snapshot inputs (`buy_ask`, `sell_bid`, fees, depth, latency, quote age) against `SpreadDetector`.
- **Result:** `100% DETERMINISTIC MATCH` (\(\text{Original Decision} \equiv \text{Replayed Decision}\)).

---

## 10. Cryptographic Export Integrity
- **CSV Export:** `GET /api/arbitrage/evidence/export/csv`
- **JSON Export:** `GET /api/arbitrage/evidence/export/json`
- **Checksum Verification:** Every export calculates and returns an immutable SHA-256 hash in `X-Export-SHA256` header and displays in modal UI.

---

## 11. Summary of Defects Fixed & Operational Status
1. **Clickable Cards:** All 12 statistical cards open the **Arbitrage Evidence Inspector**.
2. **Real Record Provenance:** Replaced static summary placeholders with actual database records.
3. **Reconciliation Guarantee:** Synchronized in-memory counters with persistent SQLite storage.
4. **Safety Enforcement:** Live execution remains strictly disabled (`PAPER / SHADOW`).
