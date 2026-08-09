import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_gitops_app_exists():
    app_yaml = os.path.abspath(os.path.join(os.path.dirname(__file__), "../infrastructure/gitops/argocd/application.yaml"))
    assert os.path.exists(app_yaml) is True
