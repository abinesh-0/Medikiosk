from datetime import datetime

from extensions import db


class MedicalTimeline(db.Model):
    __tablename__ = "medical_timeline"

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

    case_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "cases.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    event_date = db.Column(
        db.Date,
        nullable=True
    )

    event_type = db.Column(
        db.String(100),
        nullable=False
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    source_document_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "documents.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    patient = db.relationship(
        "Patient",
        back_populates="timeline_events"
    )

    case = db.relationship(
        "Case",
        back_populates="timeline_events"
    )

    source_document = db.relationship(
        "Document",
        back_populates="timeline_events"
    )

    # =========================================================
    # TO DICT
    # =========================================================

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "case_id": self.case_id,
            "event_date": (
                self.event_date.isoformat()
                if self.event_date
                else None
            ),
            "event_type": self.event_type,
            "title": self.title,
            "description": self.description,
            "source_document_id": self.source_document_id,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            )
        }

    def __repr__(self):
        return f"<MedicalTimeline {self.title}>"