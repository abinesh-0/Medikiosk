from datetime import datetime

from extensions import db


class AISummary(db.Model):
    __tablename__ = "ai_summaries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    summary_text = db.Column(
        db.Text,
        nullable=False
    )

    summary_json = db.Column(
        db.Text,
        nullable=True
    )

    language = db.Column(
        db.String(50),
        default="English"
    )

    ai_confidence = db.Column(
        db.Numeric(5, 4),
        nullable=True
    )

    doctor_status = db.Column(
        db.Enum(
            "PENDING_REVIEW",
            "EDITED",
            "CONFIRMED",
            "REJECTED"
        ),
        default="PENDING_REVIEW"
    )

    doctor_notes = db.Column(
        db.Text,
        nullable=True
    )

    reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    reviewed_at = db.Column(
        db.DateTime,
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

    case = db.relationship(
        "Case",
        back_populates="ai_summary"
    )

    reviewer = db.relationship(
        "User",
        back_populates="reviewed_summaries",
        foreign_keys=[reviewed_by]
    )

    def confirm(self, doctor_id, notes=None):
        self.doctor_status = "CONFIRMED"
        self.reviewed_by = doctor_id
        self.doctor_notes = notes
        self.reviewed_at = datetime.utcnow()

    def edit(self, doctor_id, notes=None):
        self.doctor_status = "EDITED"
        self.reviewed_by = doctor_id
        self.doctor_notes = notes
        self.reviewed_at = datetime.utcnow()

    def reject(self, doctor_id, notes=None):
        self.doctor_status = "REJECTED"
        self.reviewed_by = doctor_id
        self.doctor_notes = notes
        self.reviewed_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "summary_text": self.summary_text,
            "summary_json": self.summary_json,
            "language": self.language,
            "ai_confidence": (
                float(self.ai_confidence)
                if self.ai_confidence is not None
                else None
            ),
            "doctor_status": self.doctor_status,
            "doctor_notes": self.doctor_notes,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": (
                self.reviewed_at.isoformat()
                if self.reviewed_at else None
            ),
        }