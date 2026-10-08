from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required
from services.security.access_control import current_user_id
from services.security.password_service import hash_password
from services.security.auth_service import issue
from models.user_model import User
import secrets
from services.abdm.consent_service import grant
from models.patient_model import Patient
from models.visit_model import Visit
from models.case_model import Case
from models.clinical_history_model import ClinicalHistory
from models.ayush_model import AyushHistory
from extensions import db
from datetime import datetime
from utils.date_utils import make_number
kiosk_bp=Blueprint("kiosk",__name__)

@kiosk_bp.post('/patient-start')
def patient_start():
    d=request.get_json(silent=True) or {}; name=str(d.get('name','')).strip(); age=d.get('age'); gender=str(d.get('gender','')).strip().upper()
    if not name or not str(age).isdigit() or not gender:return jsonify(success=False,error='Name, age and gender are required'),400
    gender=gender if gender in ['MALE','FEMALE','OTHER','PREFER_NOT_TO_SAY'] else 'OTHER'; pid=str(d.get('patient_id','')).strip(); p=None
    if pid.isdigit():p=Patient.query.get(int(pid))
    if not p and d.get('phone'):p=Patient.query.filter_by(phone=str(d.get('phone')).strip()).first()
    now=datetime.utcnow()
    if not p:
        email=f'kiosk-{secrets.token_hex(8)}@medikiosk.local'; u=User(full_name=name,email=email,password_hash=hash_password(secrets.token_urlsafe(18)),role='PATIENT',is_active=True,created_at=now,updated_at=now); db.session.add(u); db.session.flush(); p=Patient(user_id=u.id,full_name=name,age=int(age),gender=gender,phone=str(d.get('phone','')).strip(),address=str(d.get('address','')).strip(),preferred_language=d.get('language','English'),created_at=now,updated_at=now); db.session.add(p)
    else:p.full_name=name;p.age=int(age);p.gender=gender;p.phone=str(d.get('phone',p.phone or '')).strip();p.address=str(d.get('address',p.address or '')).strip();p.updated_at=now
    db.session.commit(); return jsonify(success=True,token=issue(p.user),patient=p.to_dict())


@kiosk_bp.get("/departments")
@jwt_required()
def departments():
    from models.department_model import Department
    return jsonify(success=True,departments=[d.to_dict() for d in Department.query.filter_by(is_active=True).all()])

@kiosk_bp.post("/start")
@jwt_required()
def start():
    p=Patient.query.filter_by(user_id=current_user_id()).first()
    if not p:return jsonify(success=False,error="Patient profile not found"),404
    d=request.get_json(silent=True) or {}; lang=d.get("language","English"); mode=d.get("mode","NORMAL")
    if lang not in ["English","Tamil"] or mode not in ["NORMAL","AYUSH"]:return jsonify(success=False,error="Invalid language or intake mode"),400
    now=datetime.utcnow()
    visit=Visit(patient_id=p.id,visit_number=make_number("VIS"),visit_date=now,visit_type="OPD",status="INTAKE",priority="NORMAL")
    db.session.add(visit); db.session.flush()
    case=Case(visit_id=visit.id,case_number=make_number("CASE"),intake_mode=mode,language=lang,status="IN_PROGRESS",priority="NORMAL")
    db.session.add(case); db.session.flush()
    grant(p.id,case.id,"DATA_COLLECTION","I consent to digital clinical history collection for this visit.",request.remote_addr)
    grant(p.id,case.id,"AI_PROCESSING","I consent to AI-assisted structuring of the information I provide.",request.remote_addr)
    if d.get("abha_consent"):
        grant(p.id,case.id,"ABHA_SHARING","I consent to prototype ABHA-linked sharing workflow.",request.remote_addr)
    db.session.commit()
    return jsonify(success=True,case=case.to_dict(),patient=p.to_dict())

@kiosk_bp.patch("/case/<int:case_id>")
@jwt_required()
def update_case(case_id):
    p=Patient.query.filter_by(user_id=current_user_id()).first()
    case=Case.query.get_or_404(case_id)
    if not p or case.visit.patient_id!=p.id:return jsonify(success=False,error="Access denied"),403
    d=request.get_json(silent=True) or {}
    if "chief_complaint" in d: case.chief_complaint=str(d["chief_complaint"])[:5000]
    if "language" in d and d["language"] in ["English","Tamil"]:
        case.language=d["language"]
        p.preferred_language=d["language"]
    if "mode" in d and d["mode"] in ["NORMAL","AYUSH"]:case.intake_mode=d["mode"]
    db.session.commit();return jsonify(success=True,case=case.to_dict())
