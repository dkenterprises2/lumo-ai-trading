import sqlite3

conn = sqlite3.connect('lumo_trading.db')
cursor = conn.cursor()

print("=== USERS IN LUMO_TRADING.DB ===")
users = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until, created_at FROM users").fetchall()
for u in users:
    print(u)

print("\n=== PORTFOLIOS IN LUMO_TRADING.DB ===")
portfolios = cursor.execute("SELECT id, user_id, usdt_balance, initial_balance, auto_bot_enabled FROM portfolio").fetchall()
for p in portfolios:
    print(p)

print("\n=== POSITIONS IN LUMO_TRADING.DB ===")
positions = cursor.execute("SELECT id, user_id, symbol, side, amount, margin_usd FROM open_positions").fetchall()
for pos in positions:
    print(pos)

print("\n=== RECENT TRADES IN LUMO_TRADING.DB ===")
trades = cursor.execute("SELECT id, user_id, symbol, side, amount, pnl_usd, status FROM trade_history LIMIT 10").fetchall()
for t in trades:
    print(t)
