from pathlib import Path
BASE=Path(__file__).resolve().parents[2]/"prompts"
def load(name):
    p=BASE/name
    return p.read_text(encoding="utf-8") if p.exists() else ""
