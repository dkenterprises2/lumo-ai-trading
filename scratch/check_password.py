import sqlite3
import bcrypt

conn = sqlite3.connect('lumo_trading.db')
cursor = conn.cursor()

user = cursor.execute("SELECT id, name, email, password_hash, is_active FROM users WHERE email='annuysfavv@gmail.com'").fetchone()

print("=== DB RECORD FOR ANNUYSFAVV@GMAIL.COM ===")
if user:
    user_id, name, email, pwd_hash, is_active = user
    print(f"User ID: {user_id}")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Password Hash: {pwd_hash}")
    print(f"Is Active: {is_active}")
    
    # Test verify password
    test_pwd = "Password123!"
    match = bcrypt.checkpw(test_pwd.encode('utf-8'), pwd_hash.encode('utf-8'))
    print(f"\nPassword verification test for '{test_pwd}': {match}")
else:
    print("User annuysfavv@gmail.com not found in lumo_trading.db")

print("\n=== ALL USERS IN LUMO_TRADING.DB ===")
all_users = cursor.execute("SELECT id, name, email, password_hash FROM users").fetchall()
for u in all_users:
    print(u)
