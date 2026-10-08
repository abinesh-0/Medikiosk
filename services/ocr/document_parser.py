from pathlib import Path
def extract_text(path):
    ext=Path(path).suffix.lower()
    if ext==".pdf":
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    if ext==".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(path).paragraphs)
    if ext==".txt":
        return Path(path).read_text(encoding="utf-8",errors="ignore")
    return ""
