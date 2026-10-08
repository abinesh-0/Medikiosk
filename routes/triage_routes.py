from flask import Blueprint,jsonify
from services.security.access_control import roles_required,current_user_id
from models.red_flag_model import RedFlag
from models.case_model import Case
from extensions import db
from datetime import datetime
triage_bp=Blueprint("triage",__name__)
@triage_bp.get("/alerts")
@roles_required("TRIAGE","DOCTOR","ADMIN")
def alerts():
    flags=RedFlag.query.filter_by(status="ACTIVE").order_by(RedFlag.created_at.desc()).all()
    return jsonify(success=True,alerts=[f.to_dict() for f in flags])
@triage_bp.post("/alerts/<int:flag_id>/acknowledge")
@roles_required("TRIAGE","DOCTOR","ADMIN")
def acknowledge(flag_id):
    f=RedFlag.query.get_or_404(flag_id);f.acknowledge(current_user_id());db.session.commit();return jsonify(success=True,alert=f.to_dict())


@triage_bp.get('/cases')
@roles_required('TRIAGE','ADMIN')
def cases():
    cs=Case.query.order_by(Case.created_at.desc()).limit(100).all()
    return jsonify(success=True,cases=[dict(c.to_dict(),recommended_department=(c.recommended_department.name if c.recommended_department else None)) for c in cs])
