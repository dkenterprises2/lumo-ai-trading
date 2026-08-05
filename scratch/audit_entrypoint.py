import sys
import os
sys.path.insert(0, os.path.abspath("."))

import main
from main import app

print("====================================================")
print("FASTAPI ENTRY POINT AUDIT")
print("====================================================")

print(f"Imported main module file path: {main.__file__}")
print(f"Absolute path: {os.path.abspath(main.__file__)}")
print(f"App Title: {app.title}")

print("\n--- REGISTERED FASTAPI ROUTES IN RUNNING APP ---")
routes_list = []
auth_login_found = False

for route in app.routes:
    methods = getattr(route, "methods", None)
    path = getattr(route, "path", "") or str(route)
    name = getattr(route, "name", "")
    methods_str = ",".join(methods) if methods else "WS/MOUNT"
    routes_list.append(f"{methods_str:<12} {path:<35} [{name}]")
    if getattr(route, "path", "") == "/api/auth/login" and methods and "POST" in methods:
        auth_login_found = True


for r in routes_list:
    print(r)

print(f"\nPOST /api/auth/login present in app.routes: {auth_login_found}")

print("\n--- IMPORTED ROUTERS IN MAIN.PY ---")
import inspect
routers_in_main = []
for name, obj in inspect.getmembers(main):
    if "APIRouter" in type(obj).__name__ or hasattr(obj, "routes"):
        routers_in_main.append((name, type(obj).__name__))

for r in routers_in_main:
    print(f"Router Variable: {r[0]} ({r[1]})")

print("\n--- INCLUDE_ROUTER EXECUTION IN MAIN.PY ---")
print("1. auth_router (prefix='/api/auth')")
print("2. ai_signal_router (prefix='/api/ai-signal')")
print("3. portfolio_router (prefix='/api/portfolio')")
print("4. sentiment_router (prefix='/api/sentiment')")
print("5. trade_router (prefix='/api/trade')")
print("6. bot_router (prefix='/api/bot')")
print("7. websocket_router")
