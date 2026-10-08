from flask import Blueprint,jsonify,request,current_app
from models.user_model import User
from models.patient_model import Patient
from services.security.auth_service import normalize_email,create_otp,verify_otp,issue
normalize = normalize_email
from services.security.password_service import hash_password
from extensions import db
from datetime import datetime
import re

auth_bp=Blueprint('auth',__name__)
def valid_email(e): return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$',e))
def strong(p): return len(p)>=8 and any(c.isupper() for c in p) and any(c.islower() for c in p) and any(c.isdigit() for c in p)

@auth_bp.post('/register/send-otp')
def send_register_otp():
 d=request.get_json(silent=True) or {};name=str(d.get('full_name','')).strip();email=normalize(d.get('email',''))
 if not name or not valid_email(email):return jsonify(success=False,error='Enter a valid name and email'),400
 if User.query.filter_by(email=email).first():return jsonify(success=False,error='Email already registered'),409
 try:
  code=create_otp(email,'register');out={'success':True,'message':'OTP created','expires_in':current_app.config['OTP_SECONDS']}
  if current_app.config['ALLOW_DEV_OTP']:out['dev_otp']=code
  return jsonify(out)
 except Exception as e:
  db.session.rollback();return jsonify(success=False,error='Unable to create OTP',detail=str(e)),500

@auth_bp.post('/register/verify-otp')
def verify_register_otp():
 d=request.get_json(silent=True) or {};ok,msg=verify_otp(d.get('email'),str(d.get('otp','')),'register',False);return jsonify(success=ok,message=msg),(200 if ok else 400)

@auth_bp.post('/register')
def register():
 d=request.get_json(silent=True) or {};name=str(d.get('full_name','')).strip();email=normalize(d.get('email',''));password=str(d.get('password',''));otp=str(d.get('otp',''));language=d.get('language','English')
 if not name or not valid_email(email) or not strong(password):return jsonify(success=False,error='Enter name, valid email and strong password'),400
 if language not in ['Tamil','English']:language='English'
 if User.query.filter_by(email=email).first():return jsonify(success=False,error='Email already registered'),409
 ok,msg=verify_otp(email,otp,'register',True)
 if not ok:return jsonify(success=False,error=msg),400
 try:
  now=datetime.utcnow();u=User(full_name=name,email=email,password_hash=hash_password(password),role='PATIENT',is_active=True,created_at=now,updated_at=now);db.session.add(u);db.session.flush();db.session.add(Patient(user_id=u.id,full_name=name,email=email,preferred_language=language,created_at=now,updated_at=now));db.session.commit();return jsonify(success=True,message='Registration successful',**issue(u)),201
 except Exception as e:
  db.session.rollback();return jsonify(success=False,error='Registration failed',detail=str(e)),500

@auth_bp.post('/login')
def login():
 d=request.get_json(silent=True) or {};email=normalize(d.get('email',''));password=str(d.get('password',''));u=User.query.filter_by(email=email).first()
 if not u or not u.is_active or not u.check_password(password):return jsonify(success=False,error='Invalid email or password'),401
 requested_role=str(d.get('type','')).upper().strip()
 if requested_role in ['PATIENT','DOCTOR','STAFF','TRIAGE','ADMIN'] and u.role != ('TRIAGE' if requested_role=='STAFF' else requested_role):return jsonify(success=False,error='This account is not authorized for the selected portal'),403
 u.last_login_at=datetime.utcnow();u.updated_at=datetime.utcnow();db.session.commit();return jsonify(success=True,message='Login successful',**issue(u))

@auth_bp.post('/forgot-password/send-otp')
def forgot_send():
 email=normalize((request.get_json(silent=True) or {}).get('email',''));u=User.query.filter_by(email=email).first();out={'success':True,'message':'If the account exists, an OTP can be requested','expires_in':current_app.config['OTP_SECONDS']}
 if u:
  code=create_otp(email,'reset')
  if current_app.config['ALLOW_DEV_OTP']:out['dev_otp']=code
 return jsonify(out)

@auth_bp.post('/forgot-password/reset')
def forgot_reset():
 d=request.get_json(silent=True) or {};email=normalize(d.get('email',''));password=str(d.get('new_password',''))
 if not strong(password):return jsonify(success=False,error='Password must have 8+ chars, uppercase, lowercase and a number'),400
 ok,msg=verify_otp(email,str(d.get('otp','')),'reset',True)
 if not ok:return jsonify(success=False,error=msg),400
 u=User.query.filter_by(email=email).first()
 if not u:return jsonify(success=False,error='Account not found'),404
 u.password_hash=hash_password(password);u.updated_at=datetime.utcnow();db.session.commit();return jsonify(success=True,message='Password reset successful')
