from datetime import datetime

from extensions import db


class Queue(db.Model):
    __tablename__ = "queues"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False
    )

    department_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "departments.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    queue_number = db.Column(
        db.Integer,
        nullable=False
    )

    priority = db.Column(
        db.Enum(
            "LOW",
            "NORMAL",
            "HIGH",
            "URGENT"
        ),
        default="NORMAL"
    )

    status = db.Column(
        db.Enum(
            "WAITING",
            "CALLED",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED"
        ),
        default="WAITING"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    called_at = db.Column(
        db.DateTime,
        nullable=True
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    case = db.relationship(
        "Case",
        back_populates="queue_entries"
    )

    department = db.relationship(
        "Department",
        back_populates="queues"
    )

    def call_patient(self):
        self.status = "CALLED"
        self.called_at = datetime.utcnow()

    def start_consultation(self):
        self.status = "IN_PROGRESS"

    def complete(self):
        self.status = "COMPLETED"
        self.completed_at = datetime.utcnow()

    def cancel(self):
        self.status = "CANCELLED"

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "department_id": self.department_id,
            "queue_number": self.queue_number,
            "priority": self.priority,
            "status": self.status,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            ),
            "called_at": (
                self.called_at.isoformat()
                if self.called_at else None
            ),
        }


class DoctorAssignment(db.Model):
    __tablename__ = "doctor_assignments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "cases.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "doctors.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    assigned_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    assignment_status = db.Column(
        db.Enum(
            "ASSIGNED",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED"
        ),
        default="ASSIGNED"
    )

    assigned_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    case = db.relationship(
        "Case",
        back_populates="doctor_assignments"
    )

    doctor = db.relationship(
        "Doctor",
        back_populates="assignments"
    )

    assigner = db.relationship(
        "User",
        back_populates="assigned_cases",
        foreign_keys=[assigned_by]
    )

    def complete(self):
        self.assignment_status = "COMPLETED"
        self.completed_at = datetime.utcnow()

    def cancel(self):
        self.assignment_status = "CANCELLED"

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "doctor_id": self.doctor_id,
            "assigned_by": self.assigned_by,
            "assignment_status": self.assignment_status,
            "assigned_at": (
                self.assigned_at.isoformat()
                if self.assigned_at else None
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at else None
            ),
        }