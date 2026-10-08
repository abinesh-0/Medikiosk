from pathlib import Path
import uuid
from utils.validators import safe_filename

def save_upload(file, folder):
    original = safe_filename(file.filename or "document")
    ext = Path(original).suffix.lower()
    stored = f"{uuid.uuid4().hex}{ext}"
    path = Path(folder) / stored
    file.save(path)
    return original, stored, str(path), path.stat().st_size
