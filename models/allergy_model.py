from datetime import datetime
from extensions import db
class Allergy(db.Model):
    __tablename__="allergies"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    case_id=db.Column(db.Integer,db.ForeignKey("cases.id",ondelete="CASCADE"),nullable=False)
    allergen=db.Column(db.String(255),nullable=False)
    reaction=db.Column(db.Text)
    severity=db.Column(db.Enum("MILD","MODERATE","SEVERE","UNKNOWN"),default="UNKNOWN")
    created_at=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    case=db.relationship("Case",back_populates="allergies")
    def to_dict(self): return {"id":self.id,"case_id":self.case_id,"allergen":self.allergen,"reaction":self.reaction,"severity":self.severity}
