import urllib.request
import urllib.error
import json
import subprocess
import time
import sys
import os

# Launch Lumo Trading Bot uvicorn server on port 8001
cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"]
env = os.environ.copy()
env["TESTING"] = "true"

proc = subprocess.Popen(cmd, env=env, cwd=os.path.abspath("."))
print("Starting Lumo Trading Bot on port 8001 (PID:", proc.pid, ")...")
time.sleep(4)

try:
    with urllib.request.urlopen("http://127.0.0.1:8001/openapi.json") as resp:
        data = json.loads(resp.read().decode())
        print("\nLumo Trading Bot OpenAPI Title:", data.get("info", {}).get("title"))
        print("Lumo Trading Bot Registered Routes:")
        for path in data.get("paths", {}).keys():
            print(f"  - {path}")

    url = "http://127.0.0.1:8001/api/auth/register"
    payload = json.dumps({
        "name": "Port Test User",
        "email": "port_test@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    }).encode('utf-8')
    headers = {"Content-Type": "application/json"}

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        print("\nPOST /api/auth/register Status:", resp.status)
        print("POST /api/auth/register Response:", resp.read().decode())

finally:
    proc.terminate()
    proc.wait()
    print("\nServer on port 8001 stopped cleanly.")
