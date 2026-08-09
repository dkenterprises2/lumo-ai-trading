import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.platform.service_mesh import service_mesh

def test_service_mesh():
    st = service_mesh.get_mesh_status()
    assert st["mesh_provider"] == "Istio"
    assert st["mtls_mode"] == "STRICT_ZERO_TRUST"
