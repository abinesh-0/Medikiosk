from datetime import datetime
from extensions import db


class CaseAnswer(db.Model):
    __tablename__ = 'case_answers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(
        db.Integer,
        db.ForeignKey('cases.id', ondelete='CASCADE'),
        nullable=False
    )
    question_key = db.Column(db.String(120), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), default='English')
    input_type = db.Column(db.Enum('VOICE','TEXT','TOUCH'), default='TEXT')
    sequence_number = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    def to_dict(self):
        return {'question_key': self.question_key, 'answer_text': self.answer_text, 'language': self.language, 'input_type': self.input_type, 'sequence_number': self.sequence_number}
