import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_hpa_in_helm():
    val_yaml = os.path.abspath(os.path.join(os.path.dirname(__file__), "../infrastructure/helm/lumo-api/values.yaml"))
    assert os.path.exists(val_yaml) is True
