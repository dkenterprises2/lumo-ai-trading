import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import sqlite3
import json

conn = sqlite3.connect('lumo_trading.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== POSITIONS TABLE ===")
cursor.execute("SELECT id, symbol, side, entry_price, amount, margin_usd, leverage, user_id FROM positions")
positions = cursor.fetchall()
print(f"Total open positions in DB: {len(positions)}")
total_margin = sum(p['margin_usd'] for p in positions)
print(f"Total Margin in open positions: ${total_margin:.2f}")
for p in positions:
    print(dict(p))

print("\n=== CLOSED TRADES / REALIZED PNL ===")
cursor.execute("SELECT symbol, side, entry_price, exit_price, pnl_usd, pnl_pct, close_reason FROM trades WHERE close_reason != 'OPEN'")
closed_trades = cursor.fetchall()
total_realized_pnl = sum(t['pnl_usd'] for t in closed_trades)
print(f"Total closed trades: {len(closed_trades)}")
print(f"Total Realized PnL from DB trades: ${total_realized_pnl:.2f}")
for t in closed_trades:
    print(dict(t))

conn.close()

print("\n=== PAPER TRADER (User ID 1) LIVE BALANCE ===")
try:
    from backend.trader_manager import trader_manager
    t = trader_manager.get_default_trader()
    print(f"Cash Balance: ${t.balance:.2f}")
    print(f"Initial Balance: ${t.initial_balance:.2f}")
    print(f"Realized PnL: ${getattr(t, 'realized_pnl', 0.0):.2f}")
    
    summary = t.get_portfolio_summary()
    print("Full Portfolio Summary:")
    print(json.dumps(summary, indent=2))
except Exception as e:
    print(f"Error loading trader: {e}")

print("\n=== SHADOW TRADING STATS ===")
try:
    from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker
    m = ArbitrageMetricsTracker.get_summary()
    print(f"Captured Shadow Arbitrage Profit: ${m.total_captured_shadow_profit_usd:.2f}")
    print(f"Total Scanned Routes: {m.total_scanned_routes}")
except Exception as e:
    print(f"Error loading arbitrage metrics: {e}")
