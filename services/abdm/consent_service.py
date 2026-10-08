from datetime import datetime
from models.consent_model import Consent
from extensions import db
def grant(patient_id, case_id, consent_type, text, ip=None):
    c=Consent(patient_id=patient_id,case_id=case_id,consent_type=consent_type,consent_given=True,
              consent_text=text,given_at=datetime.utcnow(),ip_address=ip)
    db.session.add(c); return c
