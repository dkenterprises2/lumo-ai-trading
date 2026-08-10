import os
import pytest
import asyncio
from backend.learning.performance_dataset_builder import performance_dataset_builder
from backend.database.session import init_db

@pytest.mark.asyncio
async def test_performance_dataset_building():
    await init_db()
    res = await performance_dataset_builder.build_dataset()
    assert res["status"] == "success"
    assert "file_path" in res
    assert os.path.exists(res["file_path"])
    assert res["records_count"] >= 1
