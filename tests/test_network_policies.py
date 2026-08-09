import os
import pytest

def test_network_policy_manifest():
    k8s_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "k8s", "microservices"))
    assert os.path.exists(os.path.join(k8s_dir, "network-policies.yaml"))
