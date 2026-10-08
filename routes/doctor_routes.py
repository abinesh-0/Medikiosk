from flask import Blueprint,jsonify,request
from flask_jwt_extended import get_jwt
from services.security.access_control import roles_required,current_user_id
from models.case_model import Case
from models.summary_model import AISummary
from models.queue_model import DoctorAssignment
from models.doctor_model import Doctor
from models.user_model import User
from extensions import db
doctor_bp=Blueprint("doctor",__name__)

@doctor_bp.get("/profile")
@roles_required("DOCTOR","ADMIN")
def profile():
    role=get_jwt().get("role")
    if role=="ADMIN":
        return jsonify(success=True,doctor=None,role=role)
    d=Doctor.query.filter_by(user_id=current_user_id()).first()
    if not d:return jsonify(success=False,error="Doctor profile not found"),404
    return jsonify(success=True,doctor=d.to_dict(),role=role)

@doctor_bp.get("/notifications")
@roles_required("DOCTOR","ADMIN")
def notifications():
    from models.notification_model import CaseNotification
    role=get_jwt().get("role")
    if role=="DOCTOR":
        rows=CaseNotification.query.filter_by(recipient_user_id=current_user_id()).order_by(CaseNotification.created_at.desc()).limit(50).all()
    else:
        rows=CaseNotification.query.order_by(CaseNotification.created_at.desc()).limit(50).all()
    return jsonify(success=True,notifications=[{
        "id":x.id,"case_id":x.case_id,"channel":x.channel,"subject":x.subject,
        "message":x.message,"status":x.status,"created_at":x.created_at.isoformat() if x.created_at else None
    } for x in rows])
@doctor_bp.get("/cases")
@roles_required("DOCTOR","ADMIN")
def cases():
    role=get_jwt().get("role")
    if role=="DOCTOR":
        d=Doctor.query.filter_by(user_id=current_user_id()).first()
        cs=Case.query.join(DoctorAssignment,DoctorAssignment.case_id==Case.id).filter(DoctorAssignment.doctor_id==d.id,DoctorAssignment.assignment_status.in_(["ASSIGNED","IN_PROGRESS"])).order_by(Case.priority.desc(),Case.created_at.asc()).all() if d else []
    else:
        cs=Case.query.filter(Case.status.in_(["READY_FOR_REVIEW","ASSIGNED"])).order_by(Case.created_at.desc()).all()
    return jsonify(success=True,cases=[c.to_dict() for c in cs])
@doctor_bp.get("/case/<int:case_id>")
@roles_required("DOCTOR","ADMIN")
def case_detail(case_id):
    c=Case.query.get_or_404(case_id)
    if get_jwt().get("role")=="DOCTOR":
        me=Doctor.query.filter_by(user_id=current_user_id()).first()
        if not me or not any(a.doctor_id==me.id and a.assignment_status in ["ASSIGNED","IN_PROGRESS"] for a in c.doctor_assignments):
            return jsonify(success=False,error="This case is not assigned to you"),403
    assignments=[a for a in c.doctor_assignments if a.assignment_status in ["ASSIGNED","IN_PROGRESS"]]
    assignment=None
    if assignments:
        a=sorted(assignments,key=lambda x:x.assigned_at or __import__("datetime").datetime.min)[-1]
        assignment={"doctor_id":a.doctor_id,"doctor_name":a.doctor.user.full_name if a.doctor and a.doctor.user else None,"doctor_email":a.doctor.user.email if a.doctor and a.doctor.user else None,"department":a.doctor.department.name if a.doctor and a.doctor.department else None,"status":a.assignment_status}
    return jsonify(success=True,case=c.to_dict(),assignment=assignment,
      patient=c.visit.patient.to_dict(),history=c.clinical_history.to_dict() if c.clinical_history else {},
      ayush=c.ayush_history.to_dict() if c.ayush_history else {},summary=c.ai_summary.to_dict() if c.ai_summary else None,
      flags=[f.to_dict() for f in c.red_flags],documents=[dict(d.to_dict(),extraction=(d.extraction.to_dict() if getattr(d,"extraction",None) else None)) for d in c.documents],
      timeline=[t.to_dict() for t in sorted(c.timeline_events,key=lambda x:x.event_date or __import__("datetime").date.min)])
@doctor_bp.patch("/case/<int:case_id>/review")
@roles_required("DOCTOR","ADMIN")
def review(case_id):
    c=Case.query.get_or_404(case_id)
    if get_jwt().get("role")=="DOCTOR":
        me=Doctor.query.filter_by(user_id=current_user_id()).first()
        if not me or not any(a.doctor_id==me.id and a.assignment_status in ["ASSIGNED","IN_PROGRESS"] for a in c.doctor_assignments):
            return jsonify(success=False,error="This case is not assigned to you"),403
    d=request.get_json(silent=True) or {}
    if not c.ai_summary:return jsonify(success=False,error="Summary not generated"),404
    s=c.ai_summary;s.summary_text=str(d.get("summary_text",s.summary_text));s.doctor_notes=str(d.get("doctor_notes",""));s.doctor_status=d.get("status","CONFIRMED") if d.get("status") in ["EDITED","CONFIRMED","REJECTED"] else "CONFIRMED";s.reviewed_by=current_user_id();s.reviewed_at=__import__("datetime").datetime.utcnow()
    c.status="COMPLETED" if s.doctor_status=="CONFIRMED" else c.status;c.visit.status="COMPLETED" if s.doctor_status=="CONFIRMED" else c.visit.status
    db.session.commit();return jsonify(success=True,summary=s.to_dict())
