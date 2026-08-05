import sys
import os
sys.path.insert(0, os.path.abspath("."))

import main
from main import app

def get_all_flat_routes(router_or_app):
    flat_routes = []
    routes = getattr(router_or_app, "routes", [])
    for r in routes:
        if hasattr(r, "routes"):
            flat_routes.extend(get_all_flat_routes(r))
        else:
            methods = getattr(r, "methods", None)
            path = getattr(r, "path", None)
            name = getattr(r, "name", None)
            flat_routes.append((methods, path, name, r))
    return flat_routes

all_routes = get_all_flat_routes(app)
print(f"Total Flat Routes in app: {len(all_routes)}")

auth_login_found = False
for methods, path, name, route_obj in all_routes:
    methods_str = ",".join(methods) if methods else "WS/MOUNT"
    print(f"{methods_str:<12} {str(path):<35} [{name}]")
    if path == "/api/auth/login" and methods and "POST" in methods:
        auth_login_found = True

print(f"\nPOST /api/auth/login present in flattened app.routes: {auth_login_found}")
