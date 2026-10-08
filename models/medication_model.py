from datetime import datetime
from extensions import db
class Medication(db.Model):
    __tablename__="medications"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    case_id=db.Column(db.Integer,db.ForeignKey("cases.id",ondelete="CASCADE"),nullable=False)
    medication_name=db.Column(db.String(255),nullable=False)
    dosage=db.Column(db.String(100))
    frequency=db.Column(db.String(100))
    duration=db.Column(db.String(100))
    route=db.Column(db.String(100))
    source_document_id=db.Column(db.Integer,db.ForeignKey("documents.id",ondelete="SET NULL"))
    created_at=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    case=db.relationship("Case",back_populates="medications")
    source_document=db.relationship("Document",foreign_keys=[source_document_id],back_populates="medications")
    def to_dict(self): return {c:getattr(self,c) for c in ["id","case_id","medication_name","dosage","frequency","duration","route","source_document_id"]}
