from datetime import datetime
from extensions import db
class Investigation(db.Model):
    __tablename__="investigations"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    case_id=db.Column(db.Integer,db.ForeignKey("cases.id",ondelete="CASCADE"),nullable=False)
    test_name=db.Column(db.String(255),nullable=False)
    test_date=db.Column(db.Date)
    result_value=db.Column(db.String(255))
    unit=db.Column(db.String(100))
    reference_range=db.Column(db.String(255))
    abnormal_flag=db.Column(db.Boolean,default=False)
    source_document_id=db.Column(db.Integer,db.ForeignKey("documents.id",ondelete="SET NULL"))
    created_at=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    case=db.relationship("Case",back_populates="investigations")
    source_document=db.relationship("Document",foreign_keys=[source_document_id],back_populates="investigations")
    def to_dict(self): return {"id":self.id,"case_id":self.case_id,"test_name":self.test_name,"test_date":self.test_date.isoformat() if self.test_date else None,
    "result_value":self.result_value,"unit":self.unit,"reference_range":self.reference_range,"abnormal_flag":bool(self.abnormal_flag),"source_document_id":self.source_document_id}
