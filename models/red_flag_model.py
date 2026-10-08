from datetime import datetime

from extensions import db


class RedFlag(db.Model):
    __tablename__ = "red_flags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False
    )

    flag_code = db.Column(
        db.String(100),
        nullable=False
    )

    flag_title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    severity = db.Column(
        db.Enum(
            "LOW",
            "MEDIUM",
            "HIGH",
            "URGENT"
        ),
        nullable=False
    )

    detected_by = db.Column(
        db.Enum(
            "RULE_ENGINE",
            "AI",
            "STAFF"
        ),
        nullable=False
    )

    confidence_score = db.Column(
        db.Numeric(5, 4),
        nullable=True
    )

    status = db.Column(
        db.Enum(
            "ACTIVE",
            "ACKNOWLEDGED",
            "RESOLVED"
        ),
        default="ACTIVE"
    )

    acknowledged_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    acknowledged_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    case = db.relationship(
        "Case",
        back_populates="red_flags"
    )

    acknowledger = db.relationship(
        "User",
        back_populates="acknowledged_red_flags",
        foreign_keys=[acknowledged_by]
    )

    def acknowledge(self, user_id):
        self.status = "ACKNOWLEDGED"
        self.acknowledged_by = user_id
        self.acknowledged_at = datetime.utcnow()

    def resolve(self, user_id):
        self.status = "RESOLVED"
        self.acknowledged_by = user_id
        self.acknowledged_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "flag_code": self.flag_code,
            "flag_title": self.flag_title,
            "description": self.description,
            "severity": self.severity,
            "detected_by": self.detected_by,
            "confidence_score": (
                float(self.confidence_score)
                if self.confidence_score is not None
                else None
            ),
            "status": self.status,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": (
                self.acknowledged_at.isoformat()
                if self.acknowledged_at else None
            ),
        }