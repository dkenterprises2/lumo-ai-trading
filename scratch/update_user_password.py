import sqlite3
import bcrypt

conn = sqlite3.connect('lumo_trading.db')
cursor = conn.cursor()

email = "annuysfavv@gmail.com"
new_password = "Annu@199500"

# Generate new bcrypt hash
salt = bcrypt.gensalt(12)
new_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

cursor.execute("UPDATE users SET password_hash=?, failed_login_attempts=0, locked_until=NULL WHERE email=?", (new_hash, email))
conn.commit()

print(f"=== UPDATED PASSWORD FOR {email} ===")
user = cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email=?", (email,)).fetchone()
print(f"User ID: {user[0]}")
print(f"Email: {user[2]}")
print(f"New Password Hash: {user[3]}")

# Verify password matches
verify_res = bcrypt.checkpw(new_password.encode('utf-8'), user[3].encode('utf-8'))
print(f"\nPassword verification test for '{new_password}': {verify_res}")
