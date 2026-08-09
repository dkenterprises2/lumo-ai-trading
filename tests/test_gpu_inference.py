import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.mlops.gpu_inference import gpu_inference_pipeline

def test_gpu_inference_status():
    status = gpu_inference_pipeline.get_gpu_status()
    assert status["cuda_available"] is True
    assert status["status"] == "ACCELERATED"
