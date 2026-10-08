from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS, cross_origin
from sqlalchemy import text
from config import Config
from extensions import db, jwt
from utils.logger import configure_logging

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app); jwt.init_app(app)
    rate_state = {}
    CORS(app,resources={r"/api/*":{"origins":app.config["CORS_ORIGINS"]}})
    root=Path(app.config["UPLOAD_FOLDER"])
    (root/"documents").mkdir(parents=True,exist_ok=True);(root/"audio").mkdir(parents=True,exist_ok=True)
    configure_logging(Path(__file__).resolve().parent)

    from routes.auth_routes import auth_bp
    from routes.patient_routes import patient_bp
    from routes.kiosk_routes import kiosk_bp
    from routes.conversation_routes import conversation_bp
    from routes.document_routes import document_bp
    from routes.triage_routes import triage_bp
    from routes.doctor_routes import doctor_bp
    from routes.admin_routes import admin_bp
    from routes.queue_routes import queue_bp
    from routes.integration_routes import integration_bp
    from routes.ai_routes import ai_bp
    for bp,prefix in [(auth_bp,"/api/auth"),(patient_bp,"/api/patient"),(kiosk_bp,"/api/kiosk"),
                      (conversation_bp,"/api/conversation"),(document_bp,"/api/documents"),
                      (triage_bp,"/api/triage"),(doctor_bp,"/api/doctor"),(admin_bp,"/api/admin"),
                      (queue_bp,"/api/queue"),(integration_bp,"/api/integration"),
                      (ai_bp,"/api/ai")]:
        app.register_blueprint(bp,url_prefix=prefix)

    @app.before_request
    def lightweight_rate_limit():
        if request.path.startswith("/api/auth/") and request.method=="POST":
            import time
            key=(request.remote_addr or "unknown", request.path)
            now=time.time()
            hits=[t for t in rate_state.get(key,[]) if now-t<60]
            if len(hits)>=12:
                return jsonify(success=False,error="Too many requests. Please wait a minute."),429
            hits.append(now); rate_state[key]=hits

    @app.after_request
    def security_headers(resp):
        resp.headers["X-Content-Type-Options"]="nosniff";resp.headers["X-Frame-Options"]="DENY"
        resp.headers["Referrer-Policy"]="no-referrer";resp.headers["Cache-Control"]="no-store" if request_path_is_api(resp) else resp.headers.get("Cache-Control","")
        return resp

    DEMO_UI = Path(__file__).resolve().parent / "demo_ui"

    @app.get("/")
    def home(): return send_from_directory(DEMO_UI, "index.html")

    @app.get("/demo/<path:filename>")
    def demo_assets(filename): return send_from_directory(DEMO_UI, filename)
    @app.get("/auth")
    def auth_page(): return render_template("auth/auth.html")
    @app.get("/login")
    def login_page(): return render_template("auth/auth.html")
    @app.get("/register")
    def register_page(): return render_template("auth/auth.html")
    @app.get("/forgot-password")
    def forgot_page(): return render_template("auth/forgot.html")
    @app.get("/kiosk")
    def kiosk_page(): return render_template("kiosk/intake.html")
    @app.get("/patient")
    def patient_page(): return render_template("patient/dashboard.html")
    @app.get("/doctor")
    def doctor_page(): return render_template("doctor/dashboard.html")
    @app.get("/triage")
    def triage_page(): return render_template("triage/dashboard.html")
    @app.get("/admin")
    def admin_page(): return render_template("admin/dashboard.html")
    @app.get("/api/health")
    def health():
        try: db.session.execute(text("SELECT 1"))
        except Exception: return jsonify(success=False,status="database_unavailable"),503
        return jsonify(success=True,service="MediKiosk API",status="healthy",version=app.config["APP_VERSION"])

    @app.errorhandler(413)
    def too_large(e): return jsonify(success=False,error="Uploaded file is too large"),413
    @app.errorhandler(404)
    def not_found(e):
        if __import__("flask").request.path.startswith("/api/"):return jsonify(success=False,error="Resource not found"),404
        return render_template("landing/index.html"),404
    @app.errorhandler(500)
    def internal(e):
        db.session.rollback()
        return jsonify(success=False,error="Internal server error"),500

    with app.app_context():
        import models
        from sqlalchemy.orm import configure_mappers
        configure_mappers()
        db.create_all()
        seed_demo_data()
    return app

def request_path_is_api(resp):
    return resp.headers.get("Content-Type","").startswith("application/json")

def seed_demo_data():
    from models.user_model import User
    from models.department_model import Department
    from models.doctor_model import Doctor
    from services.security.password_service import hash_password
    from datetime import datetime
    deps=[("General Medicine","GENMED"),("Orthopaedics","ORTHO"),("Cardiology","CARDIO"),("Pulmonology","PULMO"),
          ("Neurology","NEURO"),("Dermatology","DERMA"),("ENT","ENT"),("Gynaecology","GYNAE"),("Paediatrics","PAEDS"),("Ayurveda","AYUR")]
    for name,code in deps:
        if not Department.query.filter_by(code=code).first(): db.session.add(Department(name=name,code=code,description=f"{name} department",is_active=True,created_at=datetime.utcnow()))
    db.session.flush()
    demos=[
           ("Dr. Arun Kumar","generalmedicine@hospital.local","Dept@123","DOCTOR","GENMED","General Medicine","DOC-GEN-001","MBBS"),
           ("Dr. Meera Iyer","cardiology@hospital.local","Dept@123","DOCTOR","CARDIO","Cardiology","DOC-CARD-001","MD Cardiology"),
           ("Dr. Karthik Rao","pulmonology@hospital.local","Dept@123","DOCTOR","PULMO","Pulmonology","DOC-PUL-001","MD Pulmonology"),
           ("Dr. Nisha Devi","neurology@hospital.local","Dept@123","DOCTOR","NEURO","Neurology","DOC-NEU-001","MD Neurology"),
           ("Dr. Priya Shah","orthopaedics@hospital.local","Dept@123","DOCTOR","ORTHO","Orthopaedics","DOC-ORT-001","MS Orthopaedics"),
           ("Dr. Ananya Rao","dermatology@hospital.local","Dept@123","DOCTOR","DERMA","Dermatology","DOC-DER-001","MD Dermatology"),
           ("Dr. Hari Menon","ayurveda@hospital.local","Dept@123","DOCTOR","AYUR","Ayurveda","DOC-AYU-001","BAMS"),
           ("Demo Triage","staff@hospital.local","Staff@123","TRIAGE",None,None,None,None),
           ("Demo Admin","admin@hospital.local","Admin@123","ADMIN",None,None,None,None)]
    for name,email,pw,role,code,spec,doctor_code,qualification in demos:
        u=User.query.filter_by(email=email).first()
        if not u:
            u=User(full_name=name,email=email,password_hash=hash_password(pw),role=role,is_active=True,created_at=datetime.utcnow(),updated_at=datetime.utcnow());db.session.add(u);db.session.flush()
        else:
            u.full_name=name; u.password_hash=hash_password(pw); u.role=role; u.is_active=True; u.updated_at=datetime.utcnow()
        if role=="DOCTOR":
            dep=Department.query.filter_by(code=code).first()
            if dep and not Doctor.query.filter_by(user_id=u.id).first():
                db.session.add(Doctor(user_id=u.id,department_id=dep.id,doctor_code=doctor_code,specialization=spec,qualification=qualification,is_available=True,created_at=datetime.utcnow(),updated_at=datetime.utcnow()))
    db.session.commit()

def ensure_mysql_database():
    if Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
        return
    import pymysql
    conn=pymysql.connect(host=Config.MYSQL_HOST,port=Config.MYSQL_PORT,user=Config.MYSQL_USER,password=Config.MYSQL_PASSWORD,autocommit=True)
    try:
        conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    finally:
        conn.close()

app=None
if __name__=="__main__":
    try:
        ensure_mysql_database()
    except Exception as e:
        print("MySQL database auto-create skipped:",e)
    app=create_app()
    app.run(host="127.0.0.1",port=5000,debug=True)
