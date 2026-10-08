import re
from utils.constants import DEPARTMENT_KEYWORDS

def extract(text):
    text=(text or "").strip(); low=text.lower()
    result={"chief_complaint":text[:1000],"symptoms":[],"medications":[],"allergies":[],"department":None,"duration":None,"severity":None}
    for dep,words in DEPARTMENT_KEYWORDS.items():
        if any(w.lower() in low for w in words): result["department"]=dep; break
    symptom_words=["fever","cough","pain","breathing","headache","vomiting","diarrhea","rash","weakness","numbness","காய்ச்சல்","இருமல்","வலி","மூச்சு","தலைவலி"]
    result["symptoms"]=[w for w in symptom_words if w.lower() in low]
    m=re.search(r"(\d+)\s*(day|days|நாள்|நாட்கள்)",low)
    if m: result["duration"] = f"{m.group(1)} days"
    for word in ["severe","moderate","mild","அதிகம்","மிதம்","லேசு"]:
        if word in low: result["severity"]=word; break
    return result
