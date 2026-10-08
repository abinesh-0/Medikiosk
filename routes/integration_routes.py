from flask import Blueprint,jsonify
from flask_jwt_extended import jwt_required
from services.security.access_control import roles_required
from models.patient_model import Patient
from models.case_model import Case
from integrations.mock_fhir.fhir_adapter import case_bundle
from integrations.mock_his.mock_his import push_case
integration_bp=Blueprint("integration",__name__)
@integration_bp.get("/case/<int:case_id>/fhir")
@roles_required("DOCTOR","ADMIN")
def fhir(case_id):
    c=Case.query.get_or_404(case_id);return jsonify(success=True,resource=case_bundle(c.visit.patient,c))
@integration_bp.post("/case/<int:case_id>/his")
@roles_required("DOCTOR","ADMIN")
def his(case_id):
    c=Case.query.get_or_404(case_id);return jsonify(push_case(c,c.ai_summary.summary_text if c.ai_summary else ""))
