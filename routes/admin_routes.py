from flask import Blueprint,jsonify,request
import re
from datetime import datetime
from services.security.access_control import roles_required
from models.department_model import Department
from models.doctor_model import Doctor
from models.user_model import User
from models.audit_model import AuditLog
from extensions import db
from services.security.password_service import hash_password
admin_bp=Blueprint("admin",__name__)
@admin_bp.get("/dashboard")
@admin_bp.get("/overview")
@roles_required("ADMIN")
def dashboard():
    return jsonify(success=True,stats={"patients":User.query.filter_by(role="PATIENT").count(),"doctors":User.query.filter_by(role="DOCTOR").count(),"departments":Department.query.count()})
@admin_bp.get("/departments")
@roles_required("ADMIN","DOCTOR","TRIAGE")
def departments():return jsonify(success=True,departments=[d.to_dict() for d in Department.query.all()])
@admin_bp.get("/doctors")
@roles_required("ADMIN","DOCTOR","TRIAGE")
def doctors():return jsonify(success=True,doctors=[d.to_dict() for d in Doctor.query.all()])
@admin_bp.get("/audit")
@roles_required("ADMIN")
def audit():return jsonify(success=True,logs=[x.to_dict() for x in AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()])


@admin_bp.post('/department')
@roles_required('ADMIN')
def create_department():
    d=request.get_json(silent=True) or {}; name=str(d.get('name','')).strip(); email=str(d.get('email','')).strip().lower(); password=str(d.get('password',''))
    if not name or not email or len(password)<8:return jsonify(success=False,error='Department name, email and 8+ character password are required'),400
    if Department.query.filter_by(name=name).first() or User.query.filter_by(email=email).first():return jsonify(success=False,error='Department name or email already exists'),409
    now=datetime.utcnow(); code=re.sub(r'[^A-Z0-9]+','',name.upper())[:12] or 'DEPT'; base=code; i=2
    while Department.query.filter_by(code=code).first():code=f'{base}{i}';i+=1
    dep=Department(name=name,code=code,description=f'{name} department',is_active=True,created_at=now);db.session.add(dep);db.session.flush()
    u=User(full_name=str(d.get('doctor_name') or f'{name} Doctor'),email=email,password_hash=hash_password(password),role='DOCTOR',is_active=True,created_at=now,updated_at=now);db.session.add(u);db.session.flush()
    db.session.add(Doctor(user_id=u.id,department_id=dep.id,doctor_code=f'DOC-{code}',specialization=name,qualification=str(d.get('qualification') or 'MBBS'),is_available=True,created_at=now,updated_at=now));db.session.commit()
    return jsonify(success=True,department=dep.to_dict(),doctor_email=email),201

@admin_bp.patch('/department/<int:department_id>')
@roles_required('ADMIN')
def update_department(department_id):
    dep=Department.query.get_or_404(department_id);d=request.get_json(silent=True) or {};doctor=Doctor.query.filter_by(department_id=dep.id).first();u=doctor.user if doctor else None
    if d.get('name'):dep.name=str(d['name']).strip()
    if u and d.get('email'):
        email=str(d['email']).strip().lower();other=User.query.filter(User.email==email,User.id!=u.id).first()
        if other:return jsonify(success=False,error='Email already in use'),409
        u.email=email
    if u and d.get('password'):u.password_hash=hash_password(str(d['password']))
    db.session.commit();return jsonify(success=True,department=dep.to_dict(),doctor=(doctor.to_dict() if doctor else None))

@admin_bp.patch('/staff')
@roles_required('ADMIN')
def update_staff():
    d=request.get_json(silent=True) or {};u=User.query.filter_by(role='TRIAGE').first()
    if not u:return jsonify(success=False,error='Staff account not found'),404
    if d.get('email'):
        email=str(d['email']).strip().lower();other=User.query.filter(User.email==email,User.id!=u.id).first()
        if other:return jsonify(success=False,error='Email already in use'),409
        u.email=email
    if d.get('password'):u.password_hash=hash_password(str(d['password']))
    if d.get('name'):u.full_name=str(d['name']).strip()
    db.session.commit();return jsonify(success=True,staff=u.to_dict())


@admin_bp.get('/state')
@roles_required('ADMIN')
def state():
    from models.patient_model import Patient
    from models.case_model import Case
    from models.audit_model import AuditLog
    return jsonify(success=True,stats={'departments':Department.query.count(),'patients':Patient.query.count(),'cases':Case.query.count()},departments=[d.to_dict() for d in Department.query.order_by(Department.name).all()],audit=[x.to_dict() for x in AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()])
