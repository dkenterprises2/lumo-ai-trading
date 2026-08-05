import os

next_dir = r"c:\Users\kpdkd\Downloads\lumo trading bot\frontend\.next"
found_urls = set()

for root, dirs, files in os.walk(next_dir):
    for f in files:
        if f.endswith(".js"):
            filepath = os.path.join(root, f)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()
                    if "http://127.0.0.1:8000" in content:
                        found_urls.add("http://127.0.0.1:8000")
                    if "ws://127.0.0.1:8000/ws/stream" in content:
                        found_urls.add("ws://127.0.0.1:8000/ws/stream")
            except Exception:
                pass

print("Exact URL strings found in local .next JS bundle files:")
for url in found_urls:
    print(f"  - {url}")
