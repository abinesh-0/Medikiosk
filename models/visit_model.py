from datetime import datetime

from extensions import db


class Visit(db.Model):
    __tablename__ = "visits"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "patients.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    visit_number = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    visit_date = db.Column(
        db.DateTime,
        nullable=False
    )

    visit_type = db.Column(
        db.Enum(
            "OPD",
            "FOLLOW_UP",
            "EMERGENCY"
        ),
        nullable=False,
        default="OPD"
    )

    status = db.Column(
        db.Enum(
            "REGISTERED",
            "INTAKE",
            "TRIAGE",
            "QUEUED",
            "DOCTOR_REVIEW",
            "COMPLETED",
            "CANCELLED"
        ),
        nullable=False,
        default="REGISTERED"
    )

    priority = db.Column(
        db.Enum(
            "LOW",
            "NORMAL",
            "HIGH",
            "URGENT"
        ),
        nullable=False,
        default="NORMAL"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    patient = db.relationship(
        "Patient",
        back_populates="visits"
    )

    case = db.relationship(
        "Case",
        back_populates="visit",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # ---------------------------------------------------------
    # Convert object to dictionary
    # ---------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "visit_number": self.visit_number,
            "visit_date": (
                self.visit_date.isoformat()
                if self.visit_date
                else None
            ),
            "visit_type": self.visit_type,
            "status": self.status,
            "priority": self.priority,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            )
        }

    def __repr__(self):
        return f"<Visit {self.visit_number}>"