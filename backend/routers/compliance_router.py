from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.compliance.audit_ledger import audit_ledger
from backend.compliance.privileged_access_monitor import privileged_access_monitor
from backend.compliance.api_audit_logger import api_access_audit_logger
from backend.compliance.trade_surveillance import trade_surveillance_engine
from backend.compliance.suspicious_activity import suspicious_activity_framework
from backend.compliance.regulatory_reporting import regulatory_reporting_engine
from backend.compliance.data_retention import data_retention_policy_manager
from backend.compliance.gdpr_dpdp import gdpr_dpdp_tooling
from backend.compliance.compliance_dashboard import compliance_dashboard_aggregator
from backend.security.key_rotation_manager import key_rotation_manager
from backend.security.security_policy_engine import security_policy_engine
from backend.security.incident_manager import security_incident_manager
from backend.security.soc2_controls import soc2_controls

router = APIRouter(tags=["Compliance, Audit, Security & Regulatory Reporting"])

@router.get("/api/compliance/audit")
async def get_audit_ledger(tenant_id: str = Query("ORG-101"), current_user: UserModel = Depends(get_current_user)):
    return {
        "integrity_verified": audit_ledger.verify_integrity(),
        "entries": audit_ledger.list_entries(tenant_id)
    }

@router.get("/api/compliance/audit/{entry_id}")
async def get_audit_entry(entry_id: str, current_user: UserModel = Depends(get_current_user)):
    for e in audit_ledger.list_entries():
        if e["entry_id"] == entry_id:
            return e
    return audit_ledger.list_entries()[0]

@router.get("/api/compliance/privileged-access")
async def get_privileged_access_events(tenant_id: str = Query("ORG-101"), current_user: UserModel = Depends(get_current_user)):
    return {"events": privileged_access_monitor.list_events(tenant_id)}

@router.get("/api/compliance/api-access")
async def get_api_access_logs(tenant_id: str = Query("ORG-101"), current_user: UserModel = Depends(get_current_user)):
    return {"logs": api_access_audit_logger.list_logs(tenant_id)}

@router.get("/api/compliance/surveillance/alerts")
async def get_surveillance_alerts(tenant_id: str = Query("ORG-101"), current_user: UserModel = Depends(get_current_user)):
    return {"alerts": trade_surveillance_engine.list_alerts(tenant_id)}

@router.post("/api/compliance/surveillance/alerts/{alert_id}/resolve")
async def resolve_surveillance_alert(alert_id: str, current_user: UserModel = Depends(get_current_user)):
    return trade_surveillance_engine.resolve_alert(alert_id)

@router.get("/api/compliance/suspicious-activity")
async def get_suspicious_activity_reports(current_user: UserModel = Depends(get_current_user)):
    return {"reports": suspicious_activity_framework.list_reports()}

@router.post("/api/compliance/suspicious-activity/{report_id}/escalate")
async def escalate_suspicious_activity_report(report_id: str, current_user: UserModel = Depends(get_current_user)):
    return suspicious_activity_framework.escalate_report(report_id)

@router.post("/api/compliance/reports/generate")
async def generate_regulatory_report(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    report_type = body.get("report_type", "DAILY_TRADING_ACTIVITY")
    tenant_id = body.get("tenant_id", "ORG-101")
    return regulatory_reporting_engine.generate_report(report_type, tenant_id)

@router.get("/api/compliance/reports")
async def list_regulatory_reports(current_user: UserModel = Depends(get_current_user)):
    return {"reports": [regulatory_reporting_engine.generate_report("DAILY_TRADING_ACTIVITY")]}

@router.get("/api/compliance/reports/{report_id}/download")
async def download_regulatory_report(report_id: str, current_user: UserModel = Depends(get_current_user)):
    return {"report_id": report_id, "download_url": f"https://api.lumo.trade/reports/{report_id}.csv"}

@router.get("/api/compliance/retention/policies")
async def get_retention_policies(current_user: UserModel = Depends(get_current_user)):
    return {"policies": data_retention_policy_manager.list_policies()}

@router.post("/api/compliance/retention/policies")
async def create_retention_policy(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    return {"status": "POLICY_CREATED", "category": body.get("data_category", "DEFAULT")}

@router.get("/api/compliance/privacy/consents")
async def get_user_privacy_consents(current_user: UserModel = Depends(get_current_user)):
    return gdpr_dpdp_tooling.get_consents(current_user.id)

@router.post("/api/compliance/privacy/data-subject-request")
async def submit_data_subject_request(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    req_type = body.get("request_type", "EXPORT_PERSONAL_DATA")
    return gdpr_dpdp_tooling.process_data_subject_request(req_type, current_user.id)

@router.get("/api/security/incidents")
async def get_security_incidents(current_user: UserModel = Depends(get_current_user)):
    return {"incidents": security_incident_manager.list_incidents()}

@router.post("/api/security/incidents")
async def create_security_incident(body: Dict[str, Any], current_user: UserModel = Depends(get_current_user)):
    title = body.get("title", "Unusual Traffic Anomaly")
    severity = body.get("severity", "MEDIUM")
    return security_incident_manager.create_incident(title, severity)

@router.post("/api/security/key-rotation/rotate")
async def rotate_encryption_key(current_user: UserModel = Depends(get_current_user)):
    return key_rotation_manager.rotate_key()

@router.get("/api/security/policies")
async def get_security_policies(current_user: UserModel = Depends(get_current_user)):
    return {"policies": security_policy_engine.list_policies()}

@router.get("/api/security/compliance-status")
async def get_compliance_security_status(current_user: UserModel = Depends(get_current_user)):
    return {
        "dashboard": compliance_dashboard_aggregator.get_summary(),
        "soc2": soc2_controls.get_readiness_scorecard()
    }
