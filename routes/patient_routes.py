from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required
from services.security.access_control import current_user_id
from models.patient_model import Patient
from models.visit_model import Visit
from models.case_model import Case
from extensions import db
from datetime import datetime
from utils.date_utils import make_number
patient_bp=Blueprint("patient",__name__)

@patient_bp.get("/me")
@jwt_required()
def me():
    p=Patient.query.filter_by(user_id=current_user_id()).first()
    if not p:return jsonify(success=False,error="Patient profile not found"),404
    return jsonify(success=True,patient=p.to_dict())

@patient_bp.patch("/me")
@jwt_required()
def update_me():
    p=Patient.query.filter_by(user_id=current_user_id()).first()
    if not p:return jsonify(success=False,error="Patient profile not found"),404
    d=request.get_json(silent=True) or {}
    for key in ["phone","address","preferred_language","emergency_contact_name","emergency_contact_phone"]:
        if key in d:setattr(p,key,str(d[key])[:500])
    db.session.commit(); return jsonify(success=True,patient=p.to_dict())

@patient_bp.get("/cases")
@jwt_required()
def cases():
    p=Patient.query.filter_by(user_id=current_user_id()).first()
    if not p:return jsonify(success=False,error="Patient profile not found"),404
    return jsonify(success=True,cases=[v.case.to_dict() for v in p.visits if v.case])

@patient_bp.get('/case/<int:case_id>')
@jwt_required()
def case_detail(case_id):
    p=Patient.query.filter_by(user_id=current_user_id()).first(); c=Case.query.get_or_404(case_id)
    if not p or c.visit.patient_id!=p.id:return jsonify(success=False,error='Access denied'),403
    return jsonify(success=True,case=c.to_dict(),summary=c.ai_summary.to_dict() if c.ai_summary else None,flags=[f.to_dict() for f in c.red_flags],documents=[d.to_dict() for d in c.documents],timeline=[t.to_dict() for t in c.timeline_events])
