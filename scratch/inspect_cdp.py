import urllib.request
import json

try:
    with urllib.request.urlopen("http://127.0.0.1:6986/json") as response:
        data = json.loads(response.read().decode())
        print(f"Active Browser Tabs ({len(data)}):")
        for tab in data:
            print(f"ID: {tab.get('id')} | Title: {tab.get('title')} | URL: {tab.get('url')} | Type: {tab.get('type')}")
except Exception as e:
    print(f"Error connecting to CDP: {e}")
