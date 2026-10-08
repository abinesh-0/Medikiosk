from datetime import datetime

from extensions import db


class Consent(db.Model):
    __tablename__ = "consents"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "patients.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    case_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "cases.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    consent_type = db.Column(
        db.Enum(
            "DATA_COLLECTION",
            "AI_PROCESSING",
            "ABHA_SHARING",
            "HIS_SHARING",
            "DOCUMENT_PROCESSING"
        ),
        nullable=False
    )

    consent_given = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    consent_text = db.Column(
        db.Text,
        nullable=False
    )

    given_at = db.Column(
        db.DateTime,
        nullable=True
    )

    revoked_at = db.Column(
        db.DateTime,
        nullable=True
    )

    ip_address = db.Column(
        db.String(45),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    patient = db.relationship(
        "Patient",
        back_populates="consents"
    )

    case = db.relationship(
        "Case",
        back_populates="consents"
    )

    def give(self):
        self.consent_given = True
        self.given_at = datetime.utcnow()
        self.revoked_at = None

    def revoke(self):
        self.consent_given = False
        self.revoked_at = datetime.utcnow()

    def is_valid(self):
        return (
            bool(self.consent_given)
            and self.revoked_at is None
        )

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "case_id": self.case_id,
            "consent_type": self.consent_type,
            "consent_given": bool(self.consent_given),
            "consent_text": self.consent_text,
            "given_at": (
                self.given_at.isoformat()
                if self.given_at else None
            ),
            "revoked_at": (
                self.revoked_at.isoformat()
                if self.revoked_at else None
            ),
        }