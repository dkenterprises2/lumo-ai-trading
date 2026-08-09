import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_kubernetes_manifests_exist():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "deploy", "k8s"))
    assert os.path.exists(os.path.join(base_dir, "deployment.yaml"))
    assert os.path.exists(os.path.join(base_dir, "service.yaml"))
    assert os.path.exists(os.path.join(base_dir, "ingress.yaml"))
    assert os.path.exists(os.path.join(base_dir, "hpa.yaml"))
