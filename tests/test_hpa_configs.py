import os
import pytest

def test_hpa_manifests_exist():
    k8s_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "k8s", "microservices"))
    assert os.path.exists(os.path.join(k8s_dir, "hpa-trading.yaml"))
    assert os.path.exists(os.path.join(k8s_dir, "hpa-websocket.yaml"))
