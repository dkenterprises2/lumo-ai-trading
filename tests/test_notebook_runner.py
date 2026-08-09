import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.research.notebook_runner import notebook_runner

def test_notebook_runner():
    res = notebook_runner.execute_notebook("test_nb.ipynb")
    assert res["status"] == "COMPLETED"
    assert res["job_id"].startswith("JOB-NB-")
