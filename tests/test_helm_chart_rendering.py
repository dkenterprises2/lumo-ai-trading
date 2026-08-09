import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_helm_chart_exists():
    chart_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../infrastructure/helm/lumo-api/Chart.yaml"))
    assert os.path.exists(chart_path) is True
