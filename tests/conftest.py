import os
import sys

# Ensure pytest tests run against isolated test_lumo_trading.db database
os.environ["LUMO_TESTING"] = "1"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_lumo_trading.db'))}"
os.environ["ASYNC_DATABASE_URL"] = os.environ["DATABASE_URL"]

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
