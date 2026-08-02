# Lumo API and stream contract

This map is derived from `main.py`. The Next.js dashboard consumes these existing routes; it does not introduce proxy endpoints or calculate portfolio accounting values locally.

| Method | Path | Input | Response |
| --- | --- | --- | --- |
| `GET` | `/` | None | Legacy static dashboard document. |
| `GET` | `/api/market-summary` | Query: `symbol` (default `BTC/USDT`), `timeframe` (default `1h`) | `symbol`, `timeframe`, `current_price`, `rsi`, `macd`, `vwap`, `atr`, `trend`, `technical_score`, `ta_summary`, and `chart_data[]` candles (`timestamp`, OHLCV, `sma_20`, `ema_9`). |
| `GET` | `/api/news-sentiment` | None | `fear_greed`, aggregated `sentiment_summary`, and `news_articles[]`. |
| `GET` | `/api/ai-signal/{symbol}` | Path: URL-encoded trading symbol. Query: `strategy` (default `AI Hybrid`), `risk_mode` (default `Moderate`). | Signal with `action`, `direction`, confidence, scores, price targets, percentages, reasoning, strategy, and risk mode. |
| `GET` | `/api/scanner/summary` | None | Scanner cache: `timestamp`, `top_buys[]`, `top_sells[]`, and `all_pairs[]` AI signals. The cache can be `{}` before the scanner's first cycle. |
| `GET` | `/api/portfolio` | None | Authoritative paper-trading state: wallet, margin, portfolio/PnL, win rate, bot/strategy state, active positions, orders, trades, equity history, ledger, and database/audit status. |
| `GET` | `/api/accounting/audit` | None | Accounting-specific projection: wallet reconciliation, ledger, equity, positions, trades, consistency check, audit status, and database sync status. |
| `POST` | `/api/trade/order` | JSON: `symbol`, `side` (`LONG`/`SHORT`), optional `order_type`, `allocation_usd`, `leverage`, `stop_loss_price`, `take_profit_price`, `trailing_stop_pct`. | `status`, `message`, and on success the created `position`. |
| `POST` | `/api/trade/position-action` | JSON: `symbol`, `action` (`CLOSE`, `PARTIAL_CLOSE`, `REVERSE`, `EDIT_SL_TP`), optional `ratio`, `new_stop_loss`, `new_take_profit`. | `status`, `message`, and on close the resulting `trade`. Invalid actions return HTTP 400. |
| `POST` | `/api/bot/strategy` | JSON: `strategy_name`, `risk_mode`. | `status` and `message`. |
| `POST` | `/api/bot/toggle` | Query: required boolean `enable`. | `status`, `message`, `auto_bot_enabled`. |

## WebSocket: `/ws/stream`

The client sends the text payload `ping` every 15 seconds. The server returns `{ "type": "pong", "timestamp": number }`; the dashboard measures round-trip latency from that exchange.

The background scanner broadcasts `{ "type": "TICKER_UPDATE", "timestamp": number, "prices": Record<string, number>, "portfolio": PortfolioState, "scanner": ScannerSummary }` approximately every two seconds. The dashboard uses this payload for live price, portfolio, and scanner rendering, with REST as the reconnect/offline fallback.
