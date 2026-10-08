from utils.constants import DEPARTMENT_KEYWORDS

def recommend(text):
    low=(text or "").lower()
    scores={dep:sum(1 for w in words if w.lower() in low) for dep,words in DEPARTMENT_KEYWORDS.items()}
    dep=max(scores,key=scores.get) if scores and max(scores.values()) else "General Medicine"
    return dep, scores.get(dep,0)
