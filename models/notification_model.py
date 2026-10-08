from datetime import datetime
from extensions import db


class CaseNotification(db.Model):
    __tablename__ = 'case_notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(
        db.Integer,
        db.ForeignKey('cases.id', ondelete='CASCADE'),
        nullable=False
    )
    recipient_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )
    channel = db.Column(db.Enum('EMAIL', 'DASHBOARD'), default='DASHBOARD')
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    status = db.Column(db.Enum('QUEUED', 'SENT', 'FAILED'), default='QUEUED')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
