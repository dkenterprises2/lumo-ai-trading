import sqlite3

conn = sqlite3.connect('lumo_trading.db')
cursor = conn.cursor()
users = cursor.execute("SELECT id, name, email, password_hash, is_active, failed_login_attempts, locked_until, created_at FROM users").fetchall()
print(f"Total users in SQLite DB: {len(users)}")
for u in users:
    print(f"ID: {u[0]} | Name: {u[1]} | Email: {u[2]} | Hash: {u[3][:15]}... | Active: {u[4]} | FailedAttempts: {u[5]} | LockedUntil: {u[6]} | CreatedAt: {u[7]}")
