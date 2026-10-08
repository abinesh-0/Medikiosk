from datetime import datetime, timezone
def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)
def make_number(prefix):
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[-14:]}"
