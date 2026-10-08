from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(191), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.Enum("PATIENT", "DOCTOR", "TRIAGE", "ADMIN"),
        nullable=False,
        default="PATIENT"
    )

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    patient = db.relationship(
        "Patient",
        back_populates="user",
        uselist=False,
        foreign_keys="Patient.user_id"
    )

    doctor = db.relationship(
        "Doctor",
        back_populates="user",
        uselist=False,
        foreign_keys="Doctor.user_id"
    )

    uploaded_documents = db.relationship(
        "Document",
        back_populates="uploader",
        foreign_keys="Document.uploaded_by"
    )

    reviewed_summaries = db.relationship(
        "AISummary",
        back_populates="reviewer",
        foreign_keys="AISummary.reviewed_by"
    )

    acknowledged_red_flags = db.relationship(
        "RedFlag",
        back_populates="acknowledger",
        foreign_keys="RedFlag.acknowledged_by"
    )

    assigned_cases = db.relationship(
        "DoctorAssignment",
        back_populates="assigner",
        foreign_keys="DoctorAssignment.assigned_by"
    )

    audit_logs = db.relationship(
        "AuditLog",
        back_populates="user",
        foreign_keys="AuditLog.user_id"
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=True):
        data = {
            "id": self.id,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": bool(self.is_active),
            "last_login_at": (
                self.last_login_at.isoformat()
                if self.last_login_at else None
            ),
        }

        if include_email:
            data["email"] = self.email

        return data

    def __repr__(self):
        return f"<User {self.email}>"