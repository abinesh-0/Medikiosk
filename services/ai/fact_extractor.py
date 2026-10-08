# services/ai/fact_extractor.py

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from services.ai.llm_service import generate_json
from services.ai.clinical_memory import norm, register_symptom, set_fact


# ============================================================
# LOCAL NORMALIZATION
# ============================================================

def local_norm(text: str) -> str:
    text = str(text or "").strip().lower()
    replacements = {
        "thala vali": "thalavali",
        "thalavali": "thalavali",
        "thalai vali": "thalavali",
        "thala valikkuthu": "thalavali",
        "vayiru vali": "vayiruvali",
        "vayithu": "vayiru",
        "vayithula": "vayiru",
        "vayithula vali": "vayiruvali",
        "nenju vali": "nenjuvali",
        "marbu vali": "marbuvali",
        "joram": "fever",
        "kaichal": "fever",
        "kaichchal": "fever",
        "fevr": "fever",
        "moochu kashtam": "breathing difficulty",
        "moochu vida kashtam": "breathing difficulty",
        "moochu vidave kashtam": "breathing difficulty",
    }
    for old, new in replacements.items():
        pattern = r'\b' + re.escape(old) + r'\b'
        text = re.sub(pattern, new, text)
    # Standalone synonyms (word-boundary to avoid overlap).
    text = re.sub(r'\bvaandhi\b', 'vomiting', text)
    text = re.sub(r'\bvomit\b(?!ing)', 'vomiting', text)
    text = re.sub(r'\bloose motions?\b', 'diarrhea', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ============================================================
# NEGATION DETECTION
# ============================================================

NEGATION_WORDS = [
    "illa",
    "illai",
    "illaam",
    "illaiya",
    "no",
    "not",
    "without",
    "none",
    "naan",
    "pavam",
    "pavanum",
    "povum",
    "pogum",
    "vedam",
    "venda",
    "veren",
    "verenum",
    "இல்லை",
    "இல்ல",
    "வட்டும்",
    "இல்லாம்",
]

DURATION_WORDS = [
    "naala",
    "nala",
    "naal",
    "rendu",
    "irandu",
    "moonru",
    "moonu",
    "naalu",
    "naangu",
    "anju",
    "ainthu",
    "aaru",
    "ezhu",
    "ettu",
    "onpathu",
    "pathu",
    "vaaram",
    "varam",
    "maasam",
    "masam",
    "aandu",
    "varusham",
    "day",
    "days",
    "week",
    "weeks",
    "month",
    "months",
    "year",
    "years",
    "நாட்கள்",
    "நாள்",
    "வாரங்கள்",
    "வாரம்",
    "மாதங்கள்",
    "மாதம்",
    "வருடங்கள்",
    "வருடம்",
]


def _has_negation(text: str) -> bool:
    tl = local_norm(text)
    return any(nw in tl for nw in NEGATION_WORDS)


def _has_duration(text: str) -> Optional[str]:
    text = local_norm(text)
    text = re.sub(r'\bnaalaa\b', 'naal', text)
    text = re.sub(r'\bnaala\b', 'naal', text)
    patterns = [
        r"(\d+)\s*(day|days|week|weeks|month|months|year|years)\b",
        r"(\d+)\s*(naal|nal|vaaram|varam|maasam|aandu|varusham)\b",
        r"\bfor\s+\d+\s*(day|days|week|weeks|month|months)\b",
        r"\bsince\s+\d+\s*(day|days|week|weeks|month|months)\b",
        r"\b(oru|rendu|irandu|moon[u]?|naalu|naangu|anju|aaru|ezhu|ettu|pathu)\s*(naala|nala|naal|vaarama|varama|vaaram|varam|maasama|masama|maasam)\b",
        r"(?:^|\s)(?:\d+|ஒன்று|ஒரு|இரண்டு|மூன்று|நான்கு|ஐந்து|ஆறு|ஏழு|எட்டு|தொன்னவரு|பத்து)\s*(நாட்கள|நாள|வாரங்கள|வாரம|மாதங்கள|மாதம|வருடங்கள|வருடம)",
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            groups = m.groups()
            number = groups[0]
            unit = groups[1] if len(groups) > 1 else ""
            return f"{number} {unit}".strip()
    return None


# ============================================================
# ONSET DETECTION
# ============================================================

ONSET_WORDS = [
    "today", "yesterday", "since yesterday", "morning", "evening",
    "night", "inniku", "nethu", "netru", "kaalai", "maalai",
    "இன்று", "நேற்று", "நேத்தி", "இன்னிக்கு", "அறிஞ்சிக்கு",
    "sudden", "gradual", "started", "started", "began",
    "தொடங்கியது", "முதல்", "இன்று முதல்", "நேற்று முதல்",
]


def _has_onset(text: str) -> bool:
    tl = local_norm(text)
    return any(ow in tl for ow in ONSET_WORDS)


# ============================================================
# SEVERITY DETECTION
# ============================================================

SEVERITY_WORDS = [
    "mild", "moderate", "severe", "very severe", "light", "heavy",
    "romba", "kadumai", "கடுமையான", "லேசான", "மிதம்", "அதிகம்",
]


def _has_severity(text: str) -> bool:
    tl = local_norm(text)
    return any(sw in tl for sw in SEVERITY_WORDS)


# ============================================================
# DURATION TO SPECIFIC SYMPTOM MAPPING
# ============================================================

def _duration_for_symptom(text: str, symptom_keywords: List[str]) -> Optional[str]:
    """Find duration that is associated with a specific symptom keyword.

    Uses comma/punctuation-aware segmentation so that '2 days fever, headache'
    does NOT give the headache a duration of '2 days'.
    """
    text_lower = local_norm(text)

    # Split text into segments by punctuation + comma.
    segments = re.split(r'[,;]', text_lower)
    original_segments = re.split(r'[,;]', local_norm(text))

    for seg in original_segments:
        # Find the symptom keyword in this segment.
        kw_found = None
        kw_pos = -1
        for kw in symptom_keywords:
            pos = seg.find(kw)
            if pos != -1 and (kw_found is None or pos < kw_pos):
                kw_found = kw
                kw_pos = pos

        if kw_found is not None:
            duration = _has_duration(seg)
            if duration:
                return duration

    return None


# ============================================================
# LOCAL HIGH-CONFIDENCE EXTRACTION
# ============================================================

def _has_negation_for(text: str, symptom_keywords: List[str]) -> bool:
    """Check if a symptom is negated using comma/punctuation-aware scoping.

    'fever illa, thala vali' should negate fever but NOT thalavali.
    """
    tl = local_norm(text)
    # Split by punctuation and iterate over segments.
    segments = re.split(r'[,;]', tl)
    for seg in segments:
        for kw in symptom_keywords:
            if kw in seg:
                if any(nw in seg for nw in NEGATION_WORDS):
                    return True
    return False


def local_extract(text: str) -> Dict[str, Any]:
    original = str(text or "")
    value = local_norm(original)

    symptoms: List[Dict[str, Any]] = []
    negatives: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # FEVER
    # --------------------------------------------------------
    fever_kws_original = ["fever", "kaichal", "fevr", "காய்ச்சல்", "சூடு"]
    fever_kws_normed = ["fever", "kaichal", "fevr", "காய்ச்சல்", "சூடு"]
    is_fever = any(kw in value for kw in fever_kws_normed)
    if is_fever:
        dur = _duration_for_symptom(original, fever_kws_original)
        present = not _has_negation_for(original, fever_kws_original)
        if present:
            symptoms.append({
                "name": "fever",
                "present": True,
                "duration": dur,
                "onset": "today" if _has_onset(original) else None,
                "severity": "severe" if _has_severity(original) else None,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "fever", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # HEADACHE
    # --------------------------------------------------------
    headache_kws_original = ["headache", "head pain", "thala vali", "thalavali",
                             "தலைவலி", "தலை வலி"]
    is_headache = any(kw in value for kw in ["headache", "thalavali", "head",
                                              "தலைவலி", "தலை வலி"]) \
        or "thalavali" in value
    if is_headache:
        dur = _duration_for_symptom(original, headache_kws_original)
        present = not _has_negation_for(original, headache_kws_original)
        if present:
            symptoms.append({
                "name": "headache",
                "present": True,
                "location": "head",
                "duration": dur,
                "onset": "today" if _has_onset(original) else None,
                "severity": "severe" if _has_severity(original) else None,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "headache", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # ABDOMINAL PAIN
    # --------------------------------------------------------
    abd_kws_original = ["stomach pain", "stomach ache", "abdominal pain", "abdomen",
                        "vayiru vali", "vayir vali", "vayiru", "வயிற்று வலி",
                        "வயிற்றில் வலி", "வயிறுவலி", "stomach"]
    is_abd = any(kw in value for kw in ["vayiru", "vayiruvali", "stomach", "வயிறு",
                                         "வயிற்று", "abdomen"])
    if is_abd:
        dur = _duration_for_symptom(original, abd_kws_original)
        present = not _has_negation_for(original, abd_kws_original)
        if present:
            symptoms.append({
                "name": "abdominal_pain",
                "present": True,
                "location": "abdomen",
                "duration": dur,
                "onset": "today" if _has_onset(original) else None,
                "severity": "severe" if _has_severity(original) else None,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "abdominal_pain", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # CHEST PAIN
    # --------------------------------------------------------
    chest_kws_original = ["chest pain", "chest discomfort", "marbu vali", "nenju vali",
                          "மார்பு வலி", "நெஞ்சு வலி", "chest"]
    is_chest = any(kw in value for kw in ["chest pain", "chest discomfort", "marbuvali",
                                          "nenjuvali", "மார்பு வலி", "நெஞ்சு வலி", "chest"])
    if is_chest:
        dur = _duration_for_symptom(original, chest_kws_original)
        present = not _has_negation_for(original, chest_kws_original)
        if present:
            symptoms.append({
                "name": "chest_pain",
                "present": True,
                "location": "chest",
                "duration": dur,
                "onset": "today" if _has_onset(original) else None,
                "severity": "severe" if _has_severity(original) else None,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "chest_pain", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # COUGH
    # --------------------------------------------------------
    cough_kws = ["cough", "irumal", "இருமல்", "சளி"]
    is_cough = any(kw in value for kw in cough_kws)
    if is_cough:
        dur = _duration_for_symptom(original, cough_kws)
        present = not _has_negation_for(original, cough_kws)
        if present:
            symptoms.append({
                "name": "cough",
                "present": True,
                "duration": dur,
                "onset": "today" if _has_onset(original) else None,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "cough", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # BREATHING DIFFICULTY
    # --------------------------------------------------------
    breath_kws = ["breathing difficulty", "breathless", "breathing problem",
                  "மூச்சுத்திணறல்", "மூச்சு விட சிரமம்"]
    is_breath = any(kw in value for kw in breath_kws) or "moochu" in value
    if is_breath:
        present = not _has_negation_for(original, breath_kws)
        if present:
            symptoms.append({
                "name": "breathing_difficulty",
                "present": True,
                "duration": None,
                "onset": "today" if _has_onset(original) else None,
                "severity": "severe" if _has_severity(original) else None,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "breathing_difficulty", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # VOMITING
    # --------------------------------------------------------
    vomit_kws = ["vomiting", "வாந்தி"]
    is_vomit = any(kw in value for kw in vomit_kws)
    if is_vomit:
        present = not _has_negation_for(original, vomit_kws)
        if present:
            symptoms.append({
                "name": "vomiting",
                "present": True,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "vomiting", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # DIARRHEA
    # --------------------------------------------------------
    dia_kws = ["loose motion", "loose stool", "diarrhea", "diarrhoea", "வயிற்றுப்போக்கு"]
    is_dia = any(kw in value for kw in dia_kws)
    if is_dia:
        present = not _has_negation_for(original, dia_kws)
        if present:
            symptoms.append({
                "name": "diarrhea",
                "present": True,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "diarrhea", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # URINARY
    # --------------------------------------------------------
    urine_kws = ["burning urine", "urine burning", "siruneer", "சிறுநீர்", "urinary"]
    is_urine = any(kw in value for kw in urine_kws)
    if is_urine:
        present = not _has_negation_for(original, urine_kws)
        if present:
            symptoms.append({
                "name": "urinary",
                "present": True,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "urinary", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # SKIN
    # --------------------------------------------------------
    skin_kws = ["rash", "itch", "itching", "skin problem", "thol", "தோல்", "அரிப்பு", "சொறி"]
    is_skin = any(kw in value for kw in skin_kws)
    if is_skin:
        present = not _has_negation_for(original, skin_kws)
        if present:
            symptoms.append({
                "name": "skin",
                "present": True,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "skin", "evidence": original.strip()[:200]})

    # --------------------------------------------------------
    # BACK PAIN
    # --------------------------------------------------------
    back_kws = ["back pain", "mudhugula vali", "muthugula vali", "முதுகு வலி", "முதுகு"]
    is_back = any(kw in value for kw in back_kws)
    if is_back:
        dur = _duration_for_symptom(original, back_kws)
        present = not _has_negation_for(original, back_kws)
        if present:
            symptoms.append({
                "name": "back_pain",
                "present": True,
                "location": "back",
                "duration": dur,
                "onset": "today" if _has_onset(original) else None,
                "source": "local",
                "evidence": original.strip()[:200],
            })
        else:
            negatives.append({"symptom": "back_pain", "evidence": original.strip()[:200]})

    return {
        "symptoms": symptoms,
        "negatives": negatives,
        "duration": None,
        "has_negation": len(negatives) > 0,
        "has_onset": _has_onset(original),
        "has_severity": _has_severity(original),
        "_local": True,
    }


# ============================================================
# JSON PARSER
# ============================================================

def _parse_json(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    raw = str(raw or "").strip()
    raw = re.sub(r"^```json\s*", "", raw, flags=re.I)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


# ============================================================
# LLM FACT EXTRACTION
# ============================================================

def extract_facts(
    *,
    patient_text: str,
    previous_context: Dict[str, Any] = None,
    language: str = "English",
) -> Dict[str, Any]:
    patient_text = str(patient_text or "").strip()
    local = local_extract(patient_text)

    previous_context = previous_context or {}

    prompt = f"""You are the clinical information extraction layer for MediKiosk.

You are NOT diagnosing the patient.

Your ONLY task is to understand what the patient actually said and convert it into structured history facts.

The patient may speak:
- English
- Tamil
- Tanglish
- mixed Tamil + English
- misspelled Tanglish
- speech-to-text with errors
- informal conversational language

Understand MEANING, not spelling.

IMPORTANT RULES:
1. Extract ALL useful information from the CURRENT patient message.
2. Do NOT lose information merely because it was not asked.
3. Each symptom's duration must ONLY be attached to that symptom.
4. "2 naala fever" means fever_duration=2 days, NOT headache_duration=2 days.
5. Do NOT infer facts the patient did not state.
6. If a symptom is explicitly denied, mark present=false.
7. Tamil/Tanglish meaning must be understood.
8. A symptom that inherently identifies location should carry that location.
9. "fever" alone does NOT mean duration is known.
10. "thala vali" means headache present AND head location = head.
11. "vayiru vali" means abdominal pain present AND abdomen location = abdomen.
12. "vomiting illa" means vomiting = absent (denied).
13. Do NOT invent severity, location, onset, duration, pattern, associated symptoms, examination findings, diagnosis, test results, or treatment response.
14. If uncertain, mark as unknown/uncertain.

PATIENT MESSAGE:
{patient_text}

LOCAL HIGH-CONFIDENCE EXTRACTION (deterministic, do not override these):
{json.dumps(local, ensure_ascii=False, indent=2)}

PREVIOUS CONTEXT:
{json.dumps(previous_context, ensure_ascii=False, indent=2)}

OUTPUT (RETURN ONLY VALID JSON):
{{
  "patient": {{
    "name": null,
    "age": null,
    "gender": null
  }},
  "facts": {{}},
  "symptoms": [
    {{
      "name": "",
      "present": true,
      "location": null,
      "duration": null,
      "onset": null,
      "severity": null,
      "character": null,
      "pattern": null,
      "trigger": null,
      "associated": [],
      "source": "llm",
      "confidence": 0.9,
      "evidence": ""
    }}
  ],
  "negatives": [],
  "timeline": {{}},
  "ocr_facts": [],
  "safety_flags": [],
  "uncertain_information": []
}}

Rules:
1. Extract everything explicitly stated.
2. Preserve information from previous context conceptually.
3. Do not remove an old fact merely because it is absent from the current answer.
4. Do not infer a diagnosis.
5. Do NOT invent severity, location, onset, duration, pattern, associated symptoms.
6. Duration must be attached ONLY to the symptom it refers to.
7. Symptom names normalized to English clinical terms.
8. Tamil/Tanglish meaning must be understood.
"""

    # If deterministic local extraction found symptoms/negatives, or text is a concise answer,
    # use local extraction directly to avoid duplicate LLM latency during questioning turns.
    if local.get("symptoms") or local.get("negatives") or len(patient_text.split()) <= 12:
        local["_ai_source"] = "LOCAL_RULES"
        return local

    try:
        raw, source = generate_json(prompt, json.dumps(local, ensure_ascii=False), max_tokens=150)
        result = _parse_json(raw)
        if not result:
            result = local
        result["_ai_source"] = source
        return result
    except Exception:
        local["_ai_source"] = "LOCAL_RULES"
        return local


def extract_from_ocr_document(
    document_text: str,
    document_type: str = "MEDICAL_RECORD",
) -> Dict[str, Any]:
    from services.ocr.clinical_document_extractor import extract as doc_extract
    extraction = doc_extract(document_text)

    ocr_facts = []
    for cond in extraction.get("diagnoses", []):
        ocr_facts.append({
            "type": "diagnosis",
            "value": str(cond),
            "source": "ocr",
            "document_type": document_type,
            "confidence": float(extraction.get("medical_document_confidence", 0.7)),
            "uncertain": extraction.get("medical_document_confidence", 0.7) < 0.85,
        })
    for med in extraction.get("medications", []):
        ocr_facts.append({
            "type": "medication",
            "value": str(med),
            "source": "ocr",
            "document_type": document_type,
            "confidence": float(extraction.get("medical_document_confidence", 0.7)),
            "uncertain": extraction.get("medical_document_confidence", 0.7) < 0.85,
        })
    for inv in extraction.get("investigations", []):
        ocr_facts.append({
            "type": "investigation",
            "value": str(inv),
            "source": "ocr",
            "document_type": document_type,
            "confidence": float(extraction.get("medical_document_confidence", 0.7)),
            "uncertain": extraction.get("medical_document_confidence", 0.7) < 0.85,
        })

    return {
        "ocr_facts": ocr_facts,
        "document_type": document_type,
        "is_medical_document": extraction.get("is_medical_document", False),
        "medical_document_confidence": extraction.get("medical_document_confidence", 0.0),
        "clinical_summary": extraction.get("clinical_summary", ""),
        "uncertain_items": extraction.get("uncertain_items", []),
        "_ai_source": extraction.get("ai_source", "LOCAL_RULES"),
    }
