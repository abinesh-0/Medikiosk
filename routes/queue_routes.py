from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required
from services.security.access_control import roles_required,current_user_id
from models.queue_model import Queue
from models.case_model import Case
from models.department_model import Department
from extensions import db
queue_bp=Blueprint("queue",__name__)
@queue_bp.post("/case/<int:case_id>")
@jwt_required()
def add(case_id):
    c=Case.query.get_or_404(case_id); dep=c.recommended_department
    if not dep:return jsonify(success=False,error="Department not selected"),400
    n=(db.session.query(db.func.max(Queue.queue_number)).filter_by(department_id=dep.id).scalar() or 0)+1
    q=Queue(case_id=case_id,department_id=dep.id,queue_number=n,priority=c.priority,status="WAITING")
    db.session.add(q);c.status="READY_FOR_REVIEW";c.visit.status="QUEUED";db.session.commit()
    return jsonify(success=True,queue=q.to_dict(),department=dep.name)
@queue_bp.get("/department/<int:department_id>")
@roles_required("DOCTOR","TRIAGE","ADMIN")
def department_queue(department_id):
    from sqlalchemy import case as sql_case
    priority_order=sql_case((Queue.priority=="URGENT",1),(Queue.priority=="HIGH",2),(Queue.priority=="NORMAL",3),(Queue.priority=="LOW",4),else_=5)
    qs=Queue.query.filter_by(department_id=department_id,status="WAITING").order_by(priority_order,Queue.created_at).all()
    return jsonify(success=True,queue=[q.to_dict() for q in qs])
