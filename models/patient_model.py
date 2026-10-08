from datetime import datetime

from extensions import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    abha_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    full_name = db.Column(db.String(150), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    age = db.Column(db.Integer, nullable=True)

    gender = db.Column(
        db.Enum(
            "MALE",
            "FEMALE",
            "OTHER",
            "PREFER_NOT_TO_SAY"
        ),
        nullable=True
    )

    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(191), nullable=True)
    address = db.Column(db.Text, nullable=True)

    preferred_language = db.Column(
        db.String(50),
        nullable=True,
        default="English"
    )

    emergency_contact_name = db.Column(
        db.String(150),
        nullable=True
    )

    emergency_contact_phone = db.Column(
        db.String(20),
        nullable=True
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
        back_populates="patient",
        foreign_keys=[user_id]
    )

    visits = db.relationship(
        "Visit",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    timeline_events = db.relationship(
        "MedicalTimeline",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    consents = db.relationship(
        "Consent",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "abha_id": self.abha_id,
            "date_of_birth": (
                self.date_of_birth.isoformat()
                if self.date_of_birth else None
            ),
            "age": self.age,
            "gender": self.gender,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "preferred_language": self.preferred_language,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
        }

    def __repr__(self):
        return f"<Patient {self.full_name}>"