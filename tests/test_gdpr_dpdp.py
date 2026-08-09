import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.compliance.gdpr_dpdp import gdpr_dpdp_tooling

def test_gdpr_dpdp_tooling():
    consents = gdpr_dpdp_tooling.get_consents(1)
    assert consents["data_processing_consent"] is True

    dsr = gdpr_dpdp_tooling.process_data_subject_request("EXPORT_PERSONAL_DATA", 1)
    assert dsr["request_id"].startswith("DSR-")
