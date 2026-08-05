import urllib.request
import urllib.error
import json

url = "http://127.0.0.1:8000/api/auth/login"
payload = json.dumps({"email": "test@example.com", "password": "Password123!"}).encode('utf-8')
headers = {"Content-Type": "application/json"}

req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as resp:
        print(f"Status Code: {resp.status}")
        print(f"Response Body: {resp.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"HTTPError Status Code: {e.code}")
    print(f"HTTPError Response Body: {e.read().decode()}")
except Exception as ex:
    print(f"Exception: {ex}")
