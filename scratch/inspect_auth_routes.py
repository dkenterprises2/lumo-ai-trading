import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.routers.auth_router import router as auth_router
from main import app

print(f"auth_router type: {type(auth_router)}")
print(f"auth_router prefix: {auth_router.prefix}")
print(f"auth_router routes count: {len(auth_router.routes)}")

for r in auth_router.routes:
    methods = getattr(r, "methods", None)
    path = getattr(r, "path", None)
    name = getattr(r, "name", None)
    print(f"  - {methods} {auth_router.prefix}{path} [{name}]")
