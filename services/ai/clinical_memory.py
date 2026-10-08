# services/ai/clinical_memory.py

from __future__ import annotations

import re
import time
from copy import deepcopy
from typing import Any, Dict, List, Optional, Set


# ============================================================
# SYMPTOM FACT ALIASES
# ============================================================

SYMPTOM_FACT_ALIASES = {
    "fever": "fever_duration",
    "cough": "resp_duration",
    "breathing_difficulty": "resp_duration",
    "headache": "head_duration",
    "abdominal_pain": "abd_duration",
    "chest_pain": "chest_duration",
    "back_pain": "back_duration",
}

SYMPTOM_LOCATION_ALIASES = {
    "fever": None,  # fever doesn't have a location
    "headache": "head_location",
    "abdominal_pain": "abd_location",
    "chest_pain": "chest_location",
    "back_pain": "back_location",
}

SYMPTOM_ONSET_ALIASES = {
    "fever": "fever_onset",
    "cough": "resp_onset",
    "breathing_difficulty": "resp_onset",
    "headache": "head_onset",
    "abdominal_pain": "abd_onset",
    "chest_pain": "chest_onset",
    "back_pain": "back_onset",
    "skin": "skin_onset",
    "pain": "pain_onset",
    "vomiting": "vomit_onset",
    "diarrhea": "dia_onset",
}


# ============================================================
# NORMALIZATION
# ============================================================

def norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    # Use word-boundary-safe replacements to avoid substring issues.
    # e.g. "vomit" -> "vomiting" would turn "vomiting" into "vomitinging".
    replacements = {
        "thala vali": "thalavali",
        "thala valikkuthu": "thalavali",
        "thalai vali": "thalavali",
        "vayiru vali": "vayiruvali",
        "vayithu vali": "vayiruvali",
        "vayithula vali": "vayiruvali",
        "vayithil vali": "vayiruvali",
        "nenju vali": "nenjuvali",
        "marbu vali": "marbuvali",
        "kai vali": "kaivali",
        "kaal vali": "kaalvali",
        "muguthu vali": "mudhuguvli",
        "muthugu vali": "mudhuguvli",
        "joram": "fever",
        "kaichal": "fever",
        "kaichchal": "fever",
        "fevr": "fever",
        "moochu kashtam": "breathing difficulty",
        "moochu vidave kashtam": "breathing difficulty",
        "moochu vida kashtam": "breathing difficulty",
    }
    for old, new in replacements.items():
        # Replace only whole-word matches (with optional surrounding whitespace).
        pattern = r'\b' + re.escape(old) + r'\b'
        text = re.sub(pattern, new, text)
    # Handle standalone synonyms that could overlap:
    # "vomit" -> "vomiting" but NOT if already "vomiting"
    text = re.sub(r'\bvomit\b(?!ing)', 'vomiting', text)
    text = re.sub(r'\bvaandhi\b', 'vomiting', text)
    text = re.sub(r'\bloose motions?\b', 'diarrhea', text)
    text = re.sub(r'\bfevr\b', 'fever', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ============================================================
# EMPTY MEMORY (Full structure per requirement #3)
# ============================================================

def empty_memory() -> Dict[str, Any]:
    return {
        "patient": {
            "name": None,
            "age": None,
            "gender": None,
        },
        "chief_complaint": [],
        "symptoms": {},
        "facts": {},
        "negatives": {},
        "timeline": {},
        "past_medical_history": {},
        "past_surgical_history": {},
        "medications": [],
        "allergies": [],
        "family_history": {},
        "social_history": {},
        "investigations": [],
        "previous_diagnoses": [],
        "previous_treatments": [],
        "uploaded_documents": [],
        "ocr_facts": [],
        "safety_flags": [],
        "asked_questions": [],
        "answered_concepts": [],
        "unresolved_concepts": [],
        "conversation_turns": [],
        "_meta": {
            "created_at": None,
            "updated_at": None,
            "mode": "NORMAL",
            "language": "English",
            "debug": False,
        },
    }


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        return value
    return value


def _is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _status_for_value(value: Any) -> str:
    if value is True or value == "present":
        return "known"
    if value is False or value == "absent":
        return "denied"
    if value is None or value == "unknown":
        return "unknown"
    return "known"


# ============================================================
# FACT SET
# ============================================================

def set_fact(
    memory: Dict[str, Any],
    key: str,
    value: Any,
    source: str = "patient",
    confidence: float = 1.0,
    evidence: str = "",
    status: str = "known",
) -> None:
    if not key:
        return
    value = _clean(value)
    if not _is_meaningful(value):
        return

    if status == "unknown" and value is not None and value != "unknown":
        status = "known"

    facts = memory.setdefault("facts", {})
    existing = facts.get(key)

    if existing and isinstance(existing, dict):
        old_value = existing.get("value")
        if _is_meaningful(old_value):
            if str(old_value).lower() == str(value).lower():
                existing["mentions"] = int(existing.get("mentions", 1)) + 1
                existing["confidence"] = max(
                    float(existing.get("confidence", 0.0)),
                    float(confidence),
                )
                if source and source != existing.get("source"):
                    existing["source"] = source
                if evidence and not existing.get("evidence"):
                    existing["evidence"] = evidence
                return

    facts[key] = {
        "value": value,
        "status": status,
        "confidence": float(confidence),
        "source": source,
        "evidence": evidence or "",
        "source_turn": len(memory.get("conversation_turns", [])),
    }


def get_fact(memory: Dict[str, Any], key: str, default: Any = None) -> Any:
    item = memory.get("facts", {}).get(key)
    if isinstance(item, dict):
        return item.get("value", default)
    return item if item is not None else default


def get_fact_meta(memory: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
    return memory.get("facts", {}).get(key)


def has_fact(memory: Dict[str, Any], key: str) -> bool:
    value = get_fact(memory, key)
    return _is_meaningful(value)


# ============================================================
# SYMPTOM REGISTRATION
# ============================================================

def register_symptom(
    memory: Dict[str, Any],
    symptom: str,
    *,
    present: bool = True,
    location: Optional[str] = None,
    duration: Optional[str] = None,
    onset: Optional[str] = None,
    severity: Optional[str] = None,
    character: Optional[str] = None,
    pattern: Optional[str] = None,
    trigger: Optional[str] = None,
    associated: Optional[List[str]] = None,
    source: str = "patient",
    confidence: float = 1.0,
    evidence: str = "",
) -> None:
    symptom = norm(symptom)
    if not symptom:
        return

    symptoms = memory.setdefault("symptoms", {})
    item = symptoms.setdefault(
        symptom,
        {"present": True, "mentions": 0},
    )

    item["present"] = present
    item["mentions"] = int(item.get("mentions", 0)) + 1
    item["confidence"] = max(float(item.get("confidence", 0.0)), float(confidence))

    if location:
        item["location"] = location
    if duration:
        item["duration"] = duration
    if onset:
        item["onset"] = onset
    if severity:
        item["severity"] = severity
    if character:
        item["character"] = character
    if pattern:
        item["pattern"] = pattern
    if trigger:
        item["trigger"] = trigger

    if associated:
        existing = item.get("associated", [])
        if not isinstance(existing, list):
            existing = []
        for x in associated:
            if x and x not in existing:
                existing.append(x)
        item["associated"] = existing

    item["source"] = source

    if evidence and not item.get("evidence"):
        item["evidence"] = evidence


# ============================================================
# NEGATIVE FACT REGISTRATION
# ============================================================

def register_negative(memory: Dict[str, Any], symptom: str, evidence: str = "", source: str = "patient") -> None:
    symptom = norm(symptom)
    if not symptom:
        return
    negatives = memory.setdefault("negatives", {})
    negatives[symptom] = {
        "value": False,
        "status": "denied",
        "source": source,
        "evidence": evidence,
    }


# ============================================================
# PATIENT INFO
# ============================================================

def set_patient_info(memory: Dict[str, Any], name: Any = None, age: Any = None, gender: Any = None) -> None:
    if name and not memory["patient"]["name"]:
        memory["patient"]["name"] = str(name).strip()
    if age and memory["patient"]["age"] is None:
        try:
            memory["patient"]["age"] = int(str(age).strip())
        except (ValueError, TypeError):
            pass
    if gender and not memory["patient"]["gender"]:
        memory["patient"]["gender"] = str(gender).strip()


# ============================================================
# COVERED BY SEMANTIC ENGINE
# ============================================================

SEMANTIC_COVERAGE = {
    "head_location": {
        "covers": ["headache"],
        "must_be_present": True,
        "implied_by": ["thala vali", "headache", "head pain", "தலைவலி", "தலை வலி", "thalavali"],
    },
    "abd_location": {
        "covers": ["abdominal_pain"],
        "must_be_present": True,
        "implied_by": ["vayiru vali", "abdominal pain", "stomach pain", "வயிற்று வலி", "வயிற்றில் வலி", "vayiruvali"],
    },
    "chest_location": {
        "covers": ["chest_pain"],
        "must_be_present": True,
        "implied_by": ["chest pain", "marbu vali", "nenju vali", "மார்பு வலி", "நெஞ்சு வலி"],
    },
    "pain_location": {
        "covers": [],
        "must_be_present": False,
        "implied_by": [],
    },
    "fever_duration": {
        "covers": ["fever"],
        "must_be_present": True,
        "requires": {"fever": True},
    },
    "resp_duration": {
        "covers": ["cough", "breathing_difficulty"],
        "must_be_present": True,
        "requires": {"cough": True},
    },
    "head_duration": {
        "covers": ["headache"],
        "must_be_present": True,
        "requires": {"headache": True},
    },
    "abd_duration": {
        "covers": ["abdominal_pain"],
        "must_be_present": True,
        "requires": {"abdominal_pain": True},
    },
}


def _symptom_present(memory: Dict[str, Any], symptom_name: str) -> bool:
    symptom = memory.get("symptoms", {}).get(norm(symptom_name))
    if isinstance(symptom, dict):
        return bool(symptom.get("present"))
    return False


def _check_requires(memory: Dict[str, Any], requires: Dict[str, Any]) -> bool:
    for req_key, req_val in requires.items():
        if req_val is True:
            if not _symptom_present(memory, req_key):
                return False
        else:
            fact_val = get_fact(memory, req_key)
            if fact_val != req_val:
                return False
    return True


def _duration_present(memory: Dict[str, Any], symptom_name: str) -> bool:
    symptom = memory.get("symptoms", {}).get(norm(symptom_name))
    if isinstance(symptom, dict) and symptom.get("duration"):
        return True
    return False


def _symptom_has_location(memory: Dict[str, Any], symptom_name: str) -> bool:
    symptom = memory.get("symptoms", {}).get(norm(symptom_name))
    if isinstance(symptom, dict) and symptom.get("present"):
        return bool(symptom.get("location"))
    return False


def is_covered_by_semantic(memory: Dict[str, Any], key: str) -> bool:
    coverage = SEMANTIC_COVERAGE.get(key)
    if not coverage:
        return False

    if coverage.get("must_be_present"):
        covers = coverage.get("covers", [])
        if not any(_symptom_present(memory, c) for c in covers):
            return False

    requires = coverage.get("requires", {})
    if requires and not _check_requires(memory, requires):
        return False

    # Duration keys must check that the symptom actually HAS a duration.
    if key.endswith("_duration"):
        covers = coverage.get("covers", [])
        if not any(_duration_present(memory, c) for c in covers):
            return False

    # Location keys must check that the symptom has a location.
    if key.endswith("_location"):
        covers = coverage.get("covers", [])
        if not any(_symptom_has_location(memory, c) for c in covers):
            return False

    return True


# ============================================================
# COVERED BY SYMPTOM ATTRIBUTES
# ============================================================

def is_covered_by_symptom_attrs(memory: Dict[str, Any], key: str) -> bool:
    # Per-symptom attribute matching: "fever_duration" matches
    # only the fever symptom's duration, not any symptom's duration.
    SYMPTOM_ATTRS = [
        ("fever_duration", "fever", "duration"),
        ("head_duration", "headache", "duration"),
        ("abd_duration", "abdominal_pain", "duration"),
        ("resp_duration", ["cough", "breathing_difficulty"], "duration"),
        ("chest_onset", "chest_pain", "onset"),
        ("head_onset", "headache", "onset"),
        ("abd_onset", "abdominal_pain", "onset"),
        ("abd_food", "abdominal_pain", "trigger"),
        ("pain_onset", "pain", "onset"),
        ("skin_onset", "skin", "onset"),
        ("head_location", "headache", "location"),
        ("abd_location", "abdominal_pain", "location"),
        ("chest_location", "chest_pain", "location"),
        ("fever_severity", "fever", "severity"),
        ("head_severity", "headache", "severity"),
    ]

    for pattern_key, symptom_names, attr in SYMPTOM_ATTRS:
        if key == pattern_key:
            if symptom_names:
                if isinstance(symptom_names, str):
                    symptom_names = [symptom_names]
                for sn in symptom_names:
                    symptom = memory.get("symptoms", {}).get(norm(sn))
                    if isinstance(symptom, dict) and symptom.get("present"):
                        if symptom.get(attr):
                            return True
            else:
                # Generic: any present symptom with this attr
                for s_name, symptom in memory.get("symptoms", {}).items():
                    if isinstance(symptom, dict) and symptom.get("present"):
                        if symptom.get(attr):
                            return True
            return False

    # Generic suffix matching for symptoms registered by name.
    # e.g. key "vomiting" matches symptom "vomiting"
    if key in memory.get("symptoms", {}):
        symptom = memory["symptoms"][key]
        if isinstance(symptom, dict):
            return True

    return False


# ============================================================
# MAIN COVERED CHECK (Deterministic - NOT LLM)
# ============================================================

def is_covered(
    memory: Dict[str, Any],
    key: str,
    question_text: str = "",
) -> bool:
    if has_fact(memory, key):
        return True

    if is_covered_by_semantic(memory, key):
        return True

    if is_covered_by_symptom_attrs(memory, key):
        return True

    if key in memory.get("answered_concepts", []):
        return True

    if key in memory.get("answered_questions", {}):
        return True

    # Direct symptom name coverage (e.g., "vomiting", "cough").
    # A symptom is covered if it's registered in symptoms dict
    # OR if it's in the negatives list (explicitly denied = covered).
    if key in memory.get("symptoms", {}):
        return True

    if is_denied(memory, key):
        return True

    text = norm(question_text)
    if key == "head_location" and "headache" in text:
        if _symptom_present(memory, "headache"):
            return True

    if key == "abd_location" and "vayiru" in text:
        if _symptom_present(memory, "abdominal_pain"):
            return True

    return False


# ============================================================
# NEGATION CHECK
# ============================================================

def is_denied(memory: Dict[str, Any], symptom: str) -> bool:
    symptom = norm(symptom)
    negatives = memory.get("negatives", {})
    if symptom in negatives:
        return True
    fact_meta = get_fact_meta(memory, symptom)
    if isinstance(fact_meta, dict) and fact_meta.get("status") == "denied":
        return True
    return False


# ============================================================
# ADD SYMPTOM TO UNRESOLVED
# ============================================================

def add_unresolved(memory: Dict[str, Any], concept: str) -> None:
    if concept and concept not in memory.get("unresolved_concepts", []):
        memory.setdefault("unresolved_concepts", []).append(concept)


def remove_unresolved(memory: Dict[str, Any], concept: str) -> None:
    unresolved = memory.get("unresolved_concepts", [])
    if concept in unresolved:
        unresolved.remove(concept)


# ============================================================
# MERGE EXTRACTED FACTS INTO CLINICAL MEMORY
# ============================================================

def merge_extraction(
    memory: Dict[str, Any],
    extracted: Dict[str, Any],
    source: str = "patient",
    turn_index: int = 0,
) -> Dict[str, Any]:
    if not isinstance(extracted, dict):
        return {"merged": 0, "new_facts": 0, "symptoms_added": 0}

    stats = {"merged": 0, "new_facts": 0, "symptoms_added": 0}

    patient = extracted.get("patient", {})
    if isinstance(patient, dict):
        set_patient_info(
            memory,
            name=patient.get("name"),
            age=patient.get("age"),
            gender=patient.get("gender"),
        )

    facts = extracted.get("facts", {})
    if isinstance(facts, dict):
        for key, value in facts.items():
            if isinstance(value, dict):
                set_fact(
                    memory,
                    key,
                    value.get("value"),
                    source=value.get("source", source),
                    confidence=float(value.get("confidence", 0.9)),
                    evidence=value.get("evidence", ""),
                    status=value.get("status", "known"),
                )
            else:
                set_fact(
                    memory,
                    key,
                    value,
                    source=source,
                    confidence=0.9,
                )
            stats["merged"] += 1
            if not has_fact(memory, key) or stats["new_facts"] is not None:
                stats["new_facts"] = stats.get("new_facts", 0) + 1

    symptoms = extracted.get("symptoms", [])
    if isinstance(symptoms, list):
        for item in symptoms:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if not name:
                continue

            prior_present = None
            existing = memory.get("symptoms", {}).get(norm(name))
            if isinstance(existing, dict):
                prior_present = existing.get("present")

            register_symptom(
                memory,
                name,
                present=item.get("present", True),
                location=item.get("location"),
                duration=item.get("duration"),
                onset=item.get("onset"),
                severity=item.get("severity"),
                character=item.get("character"),
                pattern=item.get("pattern"),
                trigger=item.get("trigger"),
                associated=item.get("associated", []),
            )
            stats["symptoms_added"] += 1

            if item.get("duration"):
                # Per-symptom duration fact name mapping.
                dur_fact = SYMPTOM_FACT_ALIASES.get(norm(name), f"{norm(name)}_duration")
                set_fact(
                    memory,
                    dur_fact,
                    item["duration"],
                    source=source,
                    confidence=0.9,
                    evidence=item.get("evidence", ""),
                )
            if item.get("location"):
                # Per-symptom location fact name mapping.
                loc_fact = SYMPTOM_LOCATION_ALIASES.get(norm(name), None)
                if loc_fact:
                    set_fact(
                        memory,
                        loc_fact,
                        item["location"],
                        source=source,
                        confidence=0.9,
                        evidence=item.get("evidence", ""),
                    )
            if item.get("onset"):
                onset_fact = SYMPTOM_ONSET_ALIASES.get(norm(name), f"{norm(name)}_onset")
                set_fact(
                    memory,
                    onset_fact,
                    item["onset"],
                    source=source,
                    confidence=0.9,
                )

            if prior_present is None and item.get("present"):
                add_unresolved(memory, name)

    negatives = extracted.get("negatives", [])
    if isinstance(negatives, list):
        for neg in negatives:
            if isinstance(neg, dict):
                register_negative(
                    memory,
                    neg.get("symptom", ""),
                    evidence=neg.get("evidence", ""),
                    source=source,
                )
                remove_unresolved(memory, norm(neg.get("symptom", "")))
            elif isinstance(neg, str):
                register_negative(memory, neg, source=source)
                remove_unresolved(memory, norm(neg))

    ocr_facts = extracted.get("ocr_facts", [])
    if isinstance(ocr_facts, list):
        existing_ocr = memory.get("ocr_facts", [])
        for of in ocr_facts:
            if isinstance(of, dict) and of not in existing_ocr:
                existing_ocr.append(of)
        memory["ocr_facts"] = existing_ocr

    timeline = extracted.get("timeline", {})
    if isinstance(timeline, dict):
        existing_tl = memory.get("timeline", {})
        for k, v in timeline.items():
            if v is not None:
                existing_tl[k] = v
        memory["timeline"] = existing_tl

    return stats


# ============================================================
# RECORD CONVERSATION TURN
# ============================================================

def record_turn(
    memory: Dict[str, Any],
    patient_text: str,
    extracted: Dict[str, Any] = None,
    question: str = "",
    answer: str = "",
) -> None:
    turn = {
        "turn_number": len(memory.get("conversation_turns", [])),
        "patient_text": patient_text,
        "timestamp": _now_iso(),
    }
    if question:
        turn["question"] = question
    if answer:
        turn["answer"] = answer
    if extracted:
        turn["extracted"] = extracted
    memory.setdefault("conversation_turns", []).append(turn)


# ============================================================
# MARK QUESTION ASKED / ANSWERED
# ============================================================

def mark_asked(memory: Dict[str, Any], key: str, question: str) -> None:
    asked = memory.setdefault("asked_questions", [])
    entry = {"key": key, "question": question}
    if not any(a.get("key") == key for a in asked):
        asked.append(entry)


def mark_answered(memory: Dict[str, Any], key: str, answer: str) -> None:
    answered = memory.setdefault("answered_concepts", [])
    if key not in answered:
        answered.append(key)
    remove_unresolved(memory, key)


# ============================================================
# BUILD CONTEXT FOR LLM
# ============================================================

def build_context(memory: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "patient": deepcopy(memory.get("patient", {})),
        "chief_complaint": deepcopy(memory.get("chief_complaint", [])),
        "symptoms": deepcopy(memory.get("symptoms", {})),
        "facts": deepcopy(memory.get("facts", {})),
        "negatives": deepcopy(memory.get("negatives", {})),
        "timeline": deepcopy(memory.get("timeline", {})),
        "past_medical_history": deepcopy(memory.get("past_medical_history", {})),
        "past_surgical_history": deepcopy(memory.get("past_surgical_history", {})),
        "medications": deepcopy(memory.get("medications", [])),
        "allergies": deepcopy(memory.get("allergies", [])),
        "family_history": deepcopy(memory.get("family_history", {})),
        "social_history": deepcopy(memory.get("social_history", {})),
        "investigations": deepcopy(memory.get("investigations", [])),
        "ocr_facts": deepcopy(memory.get("ocr_facts", [])),
        "safety_flags": deepcopy(memory.get("safety_flags", [])),
        "asked_questions": deepcopy(memory.get("asked_questions", [])),
        "answered_concepts": deepcopy(memory.get("answered_concepts", [])),
        "unresolved_concepts": deepcopy(memory.get("unresolved_concepts", [])),
    }


# ============================================================
# FLATTEN FOR BACKWARD COMPATIBILITY
# ============================================================

def flatten_answers(memory: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key, value in memory.get("facts", {}).items():
        if isinstance(value, dict):
            result[key] = value.get("value")
        else:
            result[key] = value
    for symptom, value in memory.get("symptoms", {}).items():
        result[f"symptom:{symptom}"] = value
    return result
