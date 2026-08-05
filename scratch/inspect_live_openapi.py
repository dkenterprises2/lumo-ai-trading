import urllib.request
import json

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/openapi.json") as resp:
        data = json.loads(resp.read().decode())
        print("Live OpenAPI Title:", data.get("info", {}).get("title"))
        print("Live OpenAPI Routes Registered:")
        paths = data.get("paths", {})
        for path, methods in paths.items():
            print(f"  {path}: {list(methods.keys())}")
except Exception as e:
    print(f"Error fetching live openapi.json: {e}")
