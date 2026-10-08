from flask import request
from extensions import db
from models.audit_model import AuditLog
def audit(user_id, action, entity_type, entity_id=None, description=None):
    db.session.add(AuditLog(
        user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id,
        description=description, ip_address=request.remote_addr,
        user_agent=(request.headers.get("User-Agent","")[:1000])
    ))
