import sqlite3
import json
import sys

# Ensure UTF-8 output encoding
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("lumo_trading.db")
conn.row_factory = sqlite3.Row

print("=== ALL EXPERIMENTS FOR TARGET AUDIT ===")
target_queries = [
    ("NEAR/USDT", "15m", 32.36),
    ("XRP/USDT", "1h", 901.60),
    ("SUI/USDT", "1d", 183.94)
]

for sym, tf, pnl in target_queries:
    print(f"\n--- AUDIT FOR {sym} {tf} (Target PnL: {pnl}) ---")
    row = conn.execute("""
        SELECT * FROM shadow_learning_experiments
        WHERE symbol = ? AND timeframe = ? AND net_pnl = ?
    """, (sym, tf, pnl)).fetchone()
    if row:
        d = dict(row)
        for k, v in d.items():
            print(f"  {k}: {v}")
    else:
        print("  Exact experiment row not found by PnL, searching by symbol & timeframe:")
        rows = conn.execute("""
            SELECT * FROM shadow_learning_experiments
            WHERE symbol = ? AND timeframe = ?
            ORDER BY timestamp DESC LIMIT 3
        """, (sym, tf)).fetchall()
        for r in rows:
            print("  Candidate:", dict(r))

print("\n=== TOTAL EXPERIMENTS COUNT IN DB ===")
c = conn.execute("SELECT count(*) as c FROM shadow_learning_experiments").fetchone()
print("Total experiments:", c["c"])

print("\n=== PERSISTED STATE ===")
state_row = conn.execute("SELECT * FROM shadow_learner_state WHERE id = 1").fetchone()
if state_row:
    print(dict(state_row))

conn.close()
