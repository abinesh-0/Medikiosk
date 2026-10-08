import re
from email_validator import validate_email, EmailNotValidError
from werkzeug.utils import secure_filename

def normalize_email(email):
    return email.strip().lower()

def valid_email(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

def strong_password(password):
    return (
        isinstance(password, str) and len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
    )

def safe_filename(name):
    return secure_filename(name)[:180]

def allowed_extension(name, allowed):
    return "." in name and name.rsplit(".",1)[1].lower() in allowed
