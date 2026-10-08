from datetime import datetime, timedelta
import hashlib, secrets
from flask import current_app
from flask_jwt_extended import create_access_token
from sqlalchemy import text
from extensions import db
from services.security.password_service import hash_password, verify_password
from utils.validators import normalize_email

def user_exists(email):
    email = normalize_email(email)
    return db.session.execute(text("SELECT 1 FROM users WHERE email=:email LIMIT 1"), {"email":email}).first() is not None

def _otp_hash(otp):
    return hashlib.sha256(otp.encode()).hexdigest()

def create_otp(email, purpose="register"):
    email = normalize_email(email)
    otp = f"{secrets.randbelow(1000000):06d}"
    now = datetime.utcnow()
    expires = now + timedelta(seconds=current_app.config["OTP_SECONDS"])
    db.session.execute(text("""
        UPDATE otp_tokens SET consumed_at=:now
        WHERE email=:email AND purpose=:purpose AND consumed_at IS NULL
    """), {"now":now,"email":email,"purpose":purpose})
    db.session.execute(text("""
        INSERT INTO otp_tokens(email,purpose,otp_hash,expires_at,attempts,consumed_at,created_at)
        VALUES(:email,:purpose,:otp_hash,:expires_at,0,NULL,:created_at)
    """), {"email":email,"purpose":purpose,"otp_hash":_otp_hash(otp),"expires_at":expires,"created_at":now})
    db.session.commit()
    return otp

def verify_otp(email, otp, purpose="register", consume=True):
    email = normalize_email(email)
    record = db.session.execute(text("""
        SELECT id,otp_hash,expires_at,attempts,consumed_at FROM otp_tokens
        WHERE email=:email AND purpose=:purpose ORDER BY id DESC LIMIT 1
    """), {"email":email,"purpose":purpose}).mappings().first()
    if not record or record["consumed_at"] is not None:
        return False, "OTP not found or already used"
    if datetime.utcnow() > record["expires_at"]:
        return False, "OTP expired"
    if record["attempts"] >= current_app.config["MAX_OTP_ATTEMPTS"]:
        return False, "Too many OTP attempts"
    if not secrets.compare_digest(record["otp_hash"], _otp_hash(otp)):
        db.session.execute(text("UPDATE otp_tokens SET attempts=attempts+1 WHERE id=:id"), {"id":record["id"]})
        db.session.commit()
        return False, "Invalid OTP"
    if consume:
        db.session.execute(text("UPDATE otp_tokens SET consumed_at=:now WHERE id=:id"), {"now":datetime.utcnow(),"id":record["id"]})
        db.session.commit()
    return True, "OTP verified successfully"

def register_patient(full_name,email,password):
    email=normalize_email(email)
    if user_exists(email): return None,"Email already registered"
    now=datetime.utcnow()
    try:
        result=db.session.execute(text("""
            INSERT INTO users(full_name,email,password_hash,role,is_active,created_at,updated_at)
            VALUES(:full_name,:email,:password_hash,'PATIENT',1,:created_at,:updated_at)
        """), {"full_name":full_name.strip(),"email":email,"password_hash":hash_password(password),"created_at":now,"updated_at":now})
        uid=result.lastrowid
        db.session.execute(text("""
            INSERT INTO patients(user_id,full_name,email,preferred_language,created_at,updated_at)
            VALUES(:uid,:name,:email,'English',:now,:now)
        """), {"uid":uid,"name":full_name.strip(),"email":email,"now":now})
        db.session.commit()
        return uid,"Registration successful"
    except Exception:
        db.session.rollback(); raise

def login_user(email,password):
    email=normalize_email(email)
    user=db.session.execute(text("""
        SELECT id,full_name,email,password_hash,role,is_active FROM users WHERE email=:email LIMIT 1
    """), {"email":email}).mappings().first()
    if not user or not user["is_active"] or not verify_password(password,user["password_hash"]):
        return None,"Invalid email or password"
    now=datetime.utcnow()
    db.session.execute(text("UPDATE users SET last_login_at=:now,updated_at=:now WHERE id=:id"),{"now":now,"id":user["id"]})
    db.session.commit()
    token=create_access_token(identity=str(user["id"]),additional_claims={"role":user["role"],"email":user["email"]})
    return {"access_token":token,"user":{"id":user["id"],"full_name":user["full_name"],"email":user["email"],"role":user["role"]}},"Login successful"


# Compatibility helpers used by route layer.
normalize = normalize_email

def issue(user):
    """Issue a JWT and return the standard auth response for a User model instance."""
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email},
    )
    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
        },
    }
