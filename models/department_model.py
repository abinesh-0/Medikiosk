from datetime import datetime

from extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )

    code = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    description = db.Column(db.Text, nullable=True)

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    doctors = db.relationship(
        "Doctor",
        back_populates="department"
    )

    recommended_cases = db.relationship(
        "Case",
        back_populates="recommended_department",
        foreign_keys="Case.recommended_department_id"
    )

    queues = db.relationship(
        "Queue",
        back_populates="department"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "is_active": bool(self.is_active),
        }

    def __repr__(self):
        return f"<Department {self.name}>"