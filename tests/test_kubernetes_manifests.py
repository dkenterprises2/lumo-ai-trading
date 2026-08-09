import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_k8s_manifest_exists():
    manifest = os.path.abspath(os.path.join(os.path.dirname(__file__), "../infrastructure/kubernetes/base/deployment.yaml"))
    assert os.path.exists(manifest) is True
