import re
from utils.constants import RED_FLAG_RULES


def detect(text):
    low=(text or "").lower()
    found=[]
    for code,words,title,desc,severity in RED_FLAG_RULES:
        hits=[w for w in words if w in low]
        if hits:
            found.append({"flag_code":code,"flag_title":title,"description":desc,"severity":severity,
                          "detected_by":"RULE_ENGINE","confidence_score":min(.99,.70+.08*len(hits)),"evidence":hits})
    return found


def highest(flags):
    """Return the highest-priority triage severity from detected flags."""
    if not flags:
        return "NORMAL"
    rank = {"NORMAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "URGENT": 4}
    return max((f.get("severity", "NORMAL") for f in flags), key=lambda x: rank.get(x, 0))


# ============================================================
# LLM SAFETY FLAG NORMALIZATION
# ============================================================
# The OpenRouter LLM returns safety flags as free-form strings or
# partial dicts. Normalize them into canonical RedFlag dicts so
# downstream code can safely call .get('flag_code') etc. without
# crashing on a bare string.


def _flag_key(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


# free-form LLM flag key -> canonical category
_LLM_FLAG_ALIASES = {
    # significant bleeding
    "hemoptysis": "severe_bleeding",
    "blood_in_sputum": "severe_bleeding",
    "sputum_blood": "severe_bleeding",
    "vomiting_blood": "severe_bleeding",
    "blood_in_vomit": "severe_bleeding",
    "hematemesis": "severe_bleeding",
    "melena": "severe_bleeding",
    "blood_in_stool": "severe_bleeding",
    "hematochezia": "severe_bleeding",
    "heavy_bleeding": "severe_bleeding",
    # consciousness
    "fainting": "loss_consciousness",
    "fainted": "loss_consciousness",
    "loss_of_consciousness": "loss_consciousness",
    "unconscious": "loss_consciousness",
    "syncope": "loss_consciousness",
    "giddiness": "loss_consciousness",
    # stroke / neuro
    "stroke": "stroke_like",
    "stroke_like": "stroke_like",
    "weakness": "stroke_like",
    "numbness": "stroke_like",
    "face_droop": "stroke_like",
    "facial_droop": "stroke_like",
    "speech_difficulty": "stroke_like",
    "difficulty_speaking": "stroke_like",
    "one_side_weakness": "stroke_like",
    # severe allergy
    "anaphylaxis": "severe_allergy",
    "severe_allergic_reaction": "severe_allergy",
    "allergic_reaction": "severe_allergy",
    "throat_swelling": "severe_allergy",
    "difficulty_swallowing": "severe_allergy",
    # chest / breathing
    "chest_pain": "chest_breathing",
    "chest_discomfort": "chest_breathing",
    "chest_tightness": "chest_breathing",
    "breathing_difficulty": "chest_breathing",
    "difficulty_breathing": "chest_breathing",
    "shortness_of_breath": "chest_breathing",
    "dyspnea": "chest_breathing",
}

# canonical category -> (code, title, severity)
_FLAG_CATEGORIES = {
    "severe_bleeding": ("SEVERE_BLEEDING", "Potential significant bleeding", "HIGH"),
    "loss_consciousness": ("LOSS_CONSCIOUSNESS", "Potential loss of consciousness", "HIGH"),
    "stroke_like": ("STROKE_LIKE", "Potential sudden neurological warning symptom", "URGENT"),
    "severe_allergy": ("SEVERE_ALLERGY", "Potential severe allergic reaction", "URGENT"),
    "chest_breathing": ("CHEST_BREATHING", "Potential urgent chest/breathing symptom", "URGENT"),
}

_VALID_SEVERITIES = {"HIGH", "URGENT", "MEDIUM", "LOW"}


def normalize_llm_safety_flags(flags, default_severity="HIGH"):
    """Convert free-form LLM safety flags (strings or dicts) into canonical
    RedFlag dicts. Unknown flags become a generic HIGH alert (safety-first)."""
    if not isinstance(flags, list):
        flags = []
    out = []
    seen = set()
    for flag in flags:
        if isinstance(flag, str):
            key = _flag_key(flag)
            evidence = [flag]
            sev = ""
            raw_key = flag
        elif isinstance(flag, dict):
            raw_key = flag.get("flag_code") or flag.get("code") or flag.get("name") or flag.get("symptom") or ""
            key = _flag_key(raw_key)
            sev = str(flag.get("severity") or "").strip().upper()
            evidence = flag.get("evidence")
            if isinstance(evidence, str):
                evidence = [evidence]
            elif not isinstance(evidence, list):
                evidence = [str(raw_key) or "safety flag"]
        else:
            continue

        cat = _LLM_FLAG_ALIASES.get(key)
        if cat and cat in _FLAG_CATEGORIES:
            code, title, canon_sev = _FLAG_CATEGORIES[cat]
        else:
            code, title, canon_sev = "ALERT", "Potential safety signal", default_severity

        # Use an explicit LLM severity only if it is valid; otherwise fall
        # back to the canonical severity for this category (safety-first).
        if sev not in _VALID_SEVERITIES:
            sev = canon_sev

        # Dedup by canonical flag CODE (multiple aliases can map to the
        # same clinical signal), merging their evidence into one record.
        sig = code
        if sig in seen:
            for rec in out:
                if rec["flag_code"] == code:
                    for e in evidence:
                        if e not in rec["evidence"]:
                            rec["evidence"].append(e)
                    break
            continue
        seen.add(sig)

        out.append({
            "flag_code": code,
            "flag_title": title,
            "description": "AI safety screening evidence: " + ", ".join(evidence),
            "severity": sev,
            "detected_by": "AI",
            "confidence_score": 0.80,
            "evidence": evidence,
        })
    return out
