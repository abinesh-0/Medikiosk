from datetime import datetime

from extensions import db


class ClinicalHistory(db.Model):
    __tablename__ = "clinical_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    chief_complaint = db.Column(db.Text)
    history_present_illness = db.Column(db.Text)
    past_medical_history = db.Column(db.Text)
    past_surgical_history = db.Column(db.Text)
    medication_history = db.Column(db.Text)
    allergy_history = db.Column(db.Text)
    family_history = db.Column(db.Text)
    personal_history = db.Column(db.Text)
    social_history = db.Column(db.Text)
    review_of_systems = db.Column(db.Text)
    investigation_history = db.Column(db.Text)

    smoking_status = db.Column(db.String(100))
    alcohol_status = db.Column(db.String(100))
    occupation = db.Column(db.String(150))
    diet = db.Column(db.String(150))
    sleep_pattern = db.Column(db.String(150))

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    case = db.relationship(
        "Case",
        back_populates="clinical_history"
    )

    def to_dict(self):
        return {
            "chief_complaint": self.chief_complaint,
            "history_present_illness": self.history_present_illness,
            "past_medical_history": self.past_medical_history,
            "past_surgical_history": self.past_surgical_history,
            "medication_history": self.medication_history,
            "allergy_history": self.allergy_history,
            "family_history": self.family_history,
            "personal_history": self.personal_history,
            "social_history": self.social_history,
            "review_of_systems": self.review_of_systems,
            "investigation_history": self.investigation_history,
            "smoking_status": self.smoking_status,
            "alcohol_status": self.alcohol_status,
            "occupation": self.occupation,
            "diet": self.diet,
            "sleep_pattern": self.sleep_pattern,
        }