import os

next_dir = r"c:\Users\kpdkd\Downloads\lumo trading bot\frontend\.next"
matches = []

for root, dirs, files in os.walk(next_dir):
    for f in files:
        filepath = os.path.join(root, f)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "localhost:8000" in content:
                    matches.append((filepath, "localhost:8000"))
                if "127.0.0.1:8000" in content:
                    matches.append((filepath, "127.0.0.1:8000"))
                if "api.lumo.example.com" in content:
                    matches.append((filepath, "api.lumo.example.com"))
        except Exception:
            pass

print(f"Total Bundle Matches: {len(matches)}")
for match in matches:
    rel_path = os.path.relpath(match[0], next_dir)
    print(f"  File: {rel_path} -> Found: {match[1]}")
