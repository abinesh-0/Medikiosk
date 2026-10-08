from datetime import datetime

from extensions import db


class ConversationSession(db.Model):
    __tablename__ = "conversation_sessions"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    case_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "cases.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    language = db.Column(
        db.String(50),
        nullable=False,
        default="English"
    )

    mode = db.Column(
        db.Enum(
            "VOICE",
            "TOUCH",
            "HYBRID"
        ),
        nullable=False,
        default="HYBRID"
    )

    started_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    ended_at = db.Column(
        db.DateTime,
        nullable=True
    )

    status = db.Column(
        db.Enum(
            "ACTIVE",
            "COMPLETED",
            "ABANDONED"
        ),
        nullable=False,
        default="ACTIVE"
    )

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    # Case <-> ConversationSession
    case = db.relationship(
        "Case",
        back_populates="conversations"
    )

    # ConversationSession <-> ConversationMessage
    messages = db.relationship(
        "ConversationMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.sequence_number"
    )

    # =========================================================
    # TO DICT
    # =========================================================

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "language": self.language,
            "mode": self.mode,
            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),
            "ended_at": (
                self.ended_at.isoformat()
                if self.ended_at
                else None
            ),
            "status": self.status
        }

    def __repr__(self):
        return f"<ConversationSession {self.id}>"


class ConversationMessage(db.Model):
    __tablename__ = "conversation_messages"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    session_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "conversation_sessions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    sender = db.Column(
        db.Enum(
            "PATIENT",
            "AI",
            "SYSTEM"
        ),
        nullable=False
    )

    message_text = db.Column(
        db.Text,
        nullable=False
    )

    input_type = db.Column(
        db.Enum(
            "VOICE",
            "TEXT",
            "TOUCH"
        ),
        nullable=False,
        default="TEXT"
    )

    sequence_number = db.Column(
        db.Integer,
        nullable=False
    )

    confidence_score = db.Column(
        db.Numeric(5, 4),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # =========================================================
    # RELATIONSHIP
    # =========================================================

    session = db.relationship(
        "ConversationSession",
        back_populates="messages"
    )

    # =========================================================
    # TO DICT
    # =========================================================

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "sender": self.sender,
            "message_text": self.message_text,
            "input_type": self.input_type,
            "sequence_number": self.sequence_number,
            "confidence_score": (
                float(self.confidence_score)
                if self.confidence_score is not None
                else None
            ),
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            )
        }

    def __repr__(self):
        return f"<ConversationMessage {self.id}>"