from datetime import datetime

from extensions import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False
    )

    doctor_code = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    specialization = db.Column(
        db.String(150),
        nullable=False
    )

    qualification = db.Column(
        db.String(255),
        nullable=True
    )

    is_available = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

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

    user = db.relationship(
        "User",
        back_populates="doctor",
        foreign_keys=[user_id]
    )

    department = db.relationship(
        "Department",
        back_populates="doctors"
    )

    assignments = db.relationship(
        "DoctorAssignment",
        back_populates="doctor"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "doctor_code": self.doctor_code,
            "name": self.user.full_name if self.user else None,
            "email": self.user.email if self.user else None,
            "specialization": self.specialization,
            "qualification": self.qualification,
            "department": (
                self.department.name
                if self.department else None
            ),
            "is_available": bool(self.is_available),
        }

    def __repr__(self):
        return f"<Doctor {self.doctor_code}>"