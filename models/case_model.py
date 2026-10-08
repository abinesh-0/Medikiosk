from datetime import datetime
from extensions import db
class Case(db.Model):
    __tablename__="cases"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    visit_id=db.Column(db.Integer,db.ForeignKey("visits.id",ondelete="CASCADE"),nullable=False,unique=True)
    case_number=db.Column(db.String(50),unique=True,nullable=False)
    intake_mode=db.Column(db.Enum("NORMAL","AYUSH"),nullable=False,default="NORMAL")
    language=db.Column(db.String(50),default="English")
    chief_complaint=db.Column(db.Text)
    recommended_department_id=db.Column(db.Integer,db.ForeignKey("departments.id",ondelete="SET NULL"))
    status=db.Column(db.Enum("DRAFT","IN_PROGRESS","READY_FOR_REVIEW","ASSIGNED","COMPLETED"),default="DRAFT")
    priority=db.Column(db.Enum("LOW","NORMAL","HIGH","URGENT"),default="NORMAL")
    created_at=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,nullable=False,default=datetime.utcnow,onupdate=datetime.utcnow)
    visit=db.relationship("Visit",back_populates="case",uselist=False)
    recommended_department=db.relationship("Department",back_populates="recommended_cases")
    clinical_history=db.relationship("ClinicalHistory",back_populates="case",uselist=False,cascade="all,delete-orphan")
    ayush_history=db.relationship("AyushHistory",back_populates="case",uselist=False,cascade="all,delete-orphan")
    medications=db.relationship("Medication",back_populates="case",cascade="all,delete-orphan")
    allergies=db.relationship("Allergy",back_populates="case",cascade="all,delete-orphan")
    investigations=db.relationship("Investigation",back_populates="case",cascade="all,delete-orphan")
    documents=db.relationship("Document",back_populates="case",cascade="all,delete-orphan")
    timeline_events=db.relationship("MedicalTimeline",back_populates="case",cascade="all,delete-orphan")
    ai_summary=db.relationship("AISummary",back_populates="case",uselist=False,cascade="all,delete-orphan")
    red_flags=db.relationship("RedFlag",back_populates="case",cascade="all,delete-orphan")
    conversations=db.relationship("ConversationSession",back_populates="case",cascade="all,delete-orphan")
    queue_entries=db.relationship("Queue",back_populates="case",cascade="all,delete-orphan")
    doctor_assignments=db.relationship("DoctorAssignment",back_populates="case",cascade="all,delete-orphan")
    consents=db.relationship("Consent",back_populates="case",cascade="all,delete-orphan")
    @property
    def patient(self):
        return self.visit.patient if self.visit else None

    def to_dict(self):
        return {"id":self.id,"visit_id":self.visit_id,"case_number":self.case_number,"intake_mode":self.intake_mode,
        "language":self.language,"chief_complaint":self.chief_complaint,"recommended_department_id":self.recommended_department_id,
        "recommended_department":self.recommended_department.name if self.recommended_department else None,
        "status":self.status,"priority":self.priority,"created_at":self.created_at.isoformat() if self.created_at else None,
        "updated_at":self.updated_at.isoformat() if self.updated_at else None}
