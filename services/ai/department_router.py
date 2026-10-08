# services/ai/department_router.py

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from services.ai.llm_service import generate_json
from services.ai.clinical_memory import norm, flatten_answers, has_fact, get_fact
from utils.constants import DEPARTMENT_KEYWORDS


DEPARTMENT_CONFIG: Dict[str, Dict[str, Any]] = {
    "General Medicine": {
        "keywords": ["fever", "cold", "vomit", "diarrhea", "stomach", "pain", "காய்ச்சல்", "வலி", "வாந்தி"],
        "symptom_patterns": ["fever", "cough", "vomiting", "diarrhea", "urinary", "skin"],
        "priority": 7,
    },
    "Cardiology": {
        "keywords": ["chest pain", "chest discomfort", "palpitation", "heart", "chest", "மார்பு", "இதயம்"],
        "symptom_patterns": ["chest_pain"],
        "priority": 1,
    },
    "Pulmonology": {
        "keywords": ["breathing", "breathlessness", "cough", "wheeze", "asthma", "மூச்சு", "இருமல்"],
        "symptom_patterns": ["cough", "breathing_difficulty"],
        "priority": 2,
    },
    "Neurology": {
        "keywords": ["seizure", "faint", "headache", "migraine", "weakness", "numbness", "தலைவலி", "மயக்கம்"],
        "symptom_patterns": ["headache"],
        "priority": 3,
    },
    "Orthopaedics": {
        "keywords": ["bone", "joint", "knee", "back pain", "fracture", "shoulder", "மூட்டு", "முதுகு"],
        "symptom_patterns": ["back_pain", "limb_pain"],
        "priority": 6,
    },
    "Dermatology": {
        "keywords": ["skin", "rash", "itch", "acne", "eczema", "தோல்", "சொறி"],
        "symptom_patterns": ["skin"],
        "priority": 6,
    },
    "ENT": {
        "keywords": ["ear", "nose", "throat", "sinus", "hearing", "காது", "மூக்கு", "தொண்டை"],
        "symptom_patterns": [],
        "priority": 6,
    },
    "Gynaecology": {
        "keywords": ["period", "pregnancy", "menstrual", "pelvic", "மாதவிடாய்", "கர்ப்ப"],
        "symptom_patterns": [],
        "priority": 6,
    },
    "Paediatrics": {
        "keywords": ["child", "baby", "infant", "குழந்தை"],
        "symptom_patterns": [],
        "priority": 5,
    },
    "Gastroenterology": {
        "keywords": ["stomach", "abdomen", "vomit", "diarrhea", "constipation", "வயிறு", "வயிற்று"],
        "symptom_patterns": ["abdominal_pain"],
        "priority": 4,
    },
    "Urology": {
        "keywords": ["urine", "urinary", "burning urine", "சிறுநீர்"],
        "symptom_patterns": ["urinary"],
        "priority": 5,
    },
}


def _score_department(
    dept_name: str,
    config: Dict[str, Any],
    memory: Dict[str, Any],
    flat_answers: Dict[str, Any],
) -> float:
    score = 0.0

    for pattern in config.get("symptom_patterns", []):
        if has_fact(memory, pattern) or get_fact(memory, pattern):
            score += 3.0
        for key, val in flat_answers.items():
            if norm(str(val)) and pattern in norm(str(val)):
                score += 1.0

    for keyword in config.get("keywords", []):
        for key, val in flat_answers.items():
            if norm(str(val)).count(keyword):
                score += 0.5

    for symptom_name, symptom in memory.get("symptoms", {}).items():
        if isinstance(symptom, dict) and symptom.get("present"):
            for pattern in config.get("symptom_patterns", []):
                if pattern in norm(symptom_name):
                    score += 2.0

    if config.get("priority"):
        score += config["priority"] * 0.1

    return score


def route_department(
    memory: Dict[str, Any],
    flat_answers: Dict[str, Any] = None,
) -> Dict[str, Any]:
    flat = flat_answers or flatten_answers(memory)

    scores: Dict[str, float] = {}
    for dept_name, config in DEPARTMENT_CONFIG.items():
        scores[dept_name] = _score_department(dept_name, config, memory, flat)

    scored = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    top = scored[0] if scored else ("General Medicine", 0.0)
    top_dept, top_score = top

    candidates = [d for d, s in scored if s > 0]
    needs_review = len(candidates) > 1 or top_score <= 1.0

    supporting = []
    for symptom_name, symptom in memory.get("symptoms", {}).items():
        if isinstance(symptom, dict) and symptom.get("present"):
            supporting.append(f"{symptom_name} = present")
    for key, val in flat.items():
        if val and norm(str(val)) and "fever" in norm(str(val)):
            supporting.append(f"mentioned: {str(val)[:80]}")

    routing_reason_parts = []
    if memory.get("symptoms"):
        active = [n for n, s in memory["symptoms"].items() if isinstance(s, dict) and s.get("present")]
        if active:
            routing_reason_parts.append(f"Active symptoms: {', '.join(active[:5])}")
    if memory.get("chief_complaint"):
        cc = " ".join(str(c) for c in memory["chief_complaint"][:3]) if isinstance(memory["chief_complaint"], list) else str(memory["chief_complaint"])
        if cc:
            routing_reason_parts.append(f"Chief complaint: {cc[:100]}")

    return {
        "department": top_dept,
        "routing_reason": "; ".join(routing_reason_parts) if routing_reason_parts else "General symptoms",
        "main_problem": "",
        "supporting_facts": supporting[:10],
        "confidence": round(min(0.95, top_score / 5.0), 2) if top_score > 0 else 0.0,
        "needs_doctor_review": needs_review,
        "all_scores": {d: round(s, 2) for d, s in scored if s > 0},
        "ai_source": "RULE_ENGINE",
    }


def route_with_llm(
    memory: Dict[str, Any],
    flat_answers: Dict[str, Any] = None,
) -> Dict[str, Any]:
    rule_result = route_department(memory, flat_answers)

    if rule_result.get("confidence", 0) >= 0.7 and not rule_result.get("needs_doctor_review"):
        rule_result["ai_source"] = "RULE_ENGINE"
        return rule_result

    flat = flat_answers or flatten_answers(memory)
    prompt = f"""You are MediKiosk's department routing assistant.

Based ONLY on the following patient information, recommend the most appropriate medical department.

Rules:
1. Base your recommendation on the COMPLETE gathered information, not just the first symptom.
2. Do NOT diagnose.
3. Do NOT claim certainty when information is insufficient.
4. If multiple specialties are plausible, mark needs_doctor_review = true.
5. Return ONLY valid JSON.

PATIENT INFORMATION:
Name: {flat.get('name', 'N/A')}
Age: {flat.get('age', 'N/A')}
Gender: {flat.get('gender', 'N/A')}

CLINICAL MEMORY SUMMARY:
{json.dumps(flat, ensure_ascii=False, indent=2)}

RULE ENGINE SUGGESTION: {json.dumps(rule_result, ensure_ascii=False)}

OUTPUT JSON:
{{
  "department": "",
  "routing_reason": "",
  "main_problem": "",
  "supporting_facts": [],
  "confidence": 0.0,
  "needs_doctor_review": true
}}
"""

    try:
        raw, source = generate_json(prompt, json.dumps(rule_result))
        data = raw if isinstance(raw, dict) else {}
        if isinstance(data, dict):
            data["ai_source"] = source
            data["rule_engine_fallback"] = rule_result
            return data
    except Exception:
        pass

    rule_result["ai_source"] = "RULE_ENGINE"
    return rule_result
