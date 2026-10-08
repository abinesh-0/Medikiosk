# services/ai/doctor_summary.py

from __future__ import annotations

import json
from typing import Any, Dict, List

from services.ai.llm_service import generate_json
from services.ai.clinical_memory import (
    flatten_answers,
    get_fact,
    has_fact,
    build_context,
)


def _get_symptom_details(memory: Dict[str, Any], name: str) -> Dict[str, Any]:
    symptom = memory.get("symptoms", {}).get(name, {})
    if not isinstance(symptom, dict):
        return {}
    return {
        "name": name,
        "present": symptom.get("present", True),
        "location": symptom.get("location"),
        "duration": symptom.get("duration"),
        "onset": symptom.get("onset"),
        "severity": symptom.get("severity"),
        "character": symptom.get("character"),
        "pattern": symptom.get("pattern"),
        "trigger": symptom.get("trigger"),
        "associated": symptom.get("associated", []),
        "source": symptom.get("source", "unknown"),
    }


def generate_doctor_summary(memory: Dict[str, Any]) -> Dict[str, Any]:
    flat = flatten_answers(memory)

    # Patient info
    patient = memory.get("patient", {})
    patient_info = {
        "name": patient.get("name") or "Not provided",
        "age": str(patient.get("age")) if patient.get("age") is not None else "Not provided",
        "gender": patient.get("gender") or "Not provided",
    }

    # Chief complaint
    chief_complaint = ""
    cc = memory.get("chief_complaint", [])
    if isinstance(cc, list) and cc:
        chief_complaint = " ".join(str(c) for c in cc[:3])
    elif isinstance(cc, str) and cc:
        chief_complaint = cc
    if not chief_complaint:
        chief_complaint = flat.get("chief_complaint", flat.get("symptom:fever", flat.get("chief_complaint", "Not stated")))

    # Symptoms - each canonical fact appears once
    active_symptoms = []
    seen_symptoms = set()
    for name, symptom in memory.get("symptoms", {}).items():
        if isinstance(symptom, dict) and symptom.get("present"):
            if name in seen_symptoms:
                continue
            seen_symptoms.add(name)
            details = _get_symptom_details(memory, name)
            active_symptoms.append(details)

    # Important negatives
    important_negatives = []
    negatives = memory.get("negatives", {})
    if isinstance(negatives, dict):
        for sym, neg in negatives.items():
            if isinstance(neg, dict) and neg.get("status") == "denied":
                important_negatives.append({
                    "symptom": sym,
                    "status": "denied",
                    "evidence": neg.get("evidence", ""),
                    "source": neg.get("source", "patient"),
                })

    # Past medical history
    pmh_list = []
    pmh = memory.get("past_medical_history", {})
    if isinstance(pmh, dict):
        for k, v in pmh.items():
            if v is not None and _is_meaningful(v):
                pmh_list.append(f"{k}: {v}")
    # Also check for OCR-derived conditions
    for ocr in memory.get("ocr_facts", []):
        if isinstance(ocr, dict) and ocr.get("type") == "diagnosis":
            pmh_list.append(f"{ocr.get('value', '')} (document: {ocr.get('document_type', 'N/A')}, source: OCR, confidence: {ocr.get('confidence', 0)})")

    # Past surgical history
    psh_list = []
    psh = memory.get("past_surgical_history", {})
    if isinstance(psh, dict):
        for k, v in psh.items():
            if v is not None and _is_meaningful(v):
                psh_list.append(f"{k}: {v}")

    # Medications
    medications = []
    for med in memory.get("medications", []):
        if isinstance(med, dict):
            medications.append(med.get("name", str(med)))
        elif isinstance(med, str):
            medications.append(med)
    # OCR medications
    for ocr in memory.get("ocr_facts", []):
        if isinstance(ocr, dict) and ocr.get("type") == "medication":
            medications.append(f"{ocr.get('value', '')} (source: OCR, document: {ocr.get('document_type', 'N/A')})")

    # Allergies
    allergies = []
    for alg in memory.get("allergies", []):
        if isinstance(alg, dict):
            allergies.append(alg.get("name", str(alg)))
        elif isinstance(alg, str):
            allergies.append(alg)

    # Family history
    family_lines = []
    fh = memory.get("family_history", {})
    if isinstance(fh, dict):
        for k, v in fh.items():
            if v is not None and _is_meaningful(v):
                family_lines.append(f"{k}: {v}")

    # Social history
    social_lines = []
    sh = memory.get("social_history", {})
    if isinstance(sh, dict):
        for k, v in sh.items():
            if v is not None and _is_meaningful(v):
                social_lines.append(f"{k}: {v}")

    # Investigations
    investigations = []
    for inv in memory.get("investigations", []):
        if isinstance(inv, dict):
            investigations.append(inv.get("name", str(inv)))
        elif isinstance(inv, str):
            investigations.append(inv)
    for ocr in memory.get("ocr_facts", []):
        if isinstance(ocr, dict) and ocr.get("type") == "investigation":
            investigations.append(f"{ocr.get('value', '')} (source: OCR, document: {ocr.get('document_type', 'N/A')})")

    # OCR history documents
    doc_lines = []
    for doc in memory.get("uploaded_documents", []):
        if isinstance(doc, dict):
            doc_lines.append(f"{doc.get('original_filename', 'Unknown')} ({doc.get('document_type', 'N/A')})")
    for ocr in memory.get("ocr_facts", []):
        if isinstance(ocr, dict) and ocr.get("type") in ("diagnosis", "medication", "investigation"):
            already = any(ocr.get("value", "") in d for d in doc_lines)
            if not already:
                doc_lines.append(f"OCR: {ocr.get('value', '')} ({ocr.get('document_type', 'N/A')})")

    # Safety flags
    safety_lines = []
    for flag in memory.get("safety_flags", []):
        if isinstance(flag, dict):
            safety_lines.append(f"{flag.get('flag_title', flag.get('flag_code', 'Unknown'))} ({flag.get('severity', 'N/A')})")

    # Main problem (identify from active symptoms)
    main_problem = _identify_main_problem(memory)

    # Unknown / needs clarification
    needs_clarification = list(memory.get("unresolved_concepts", []))

    summary = {
        "PATIENT_INFORMATION": patient_info,
        "CONSULTATION_REASON": {
            "main_problem": main_problem,
            "chief_complaint": chief_complaint,
        },
        "CURRENT_SYMPTOMS": active_symptoms,
        "IMPORTANT_NEGATIVE_FINDINGS": important_negatives,
        "PAST_MEDICAL_HISTORY": pmh_list if pmh_list else ["None documented"],
        "PAST_SURGICAL_HISTORY": psh_list if psh_list else ["None documented"],
        "MEDICATIONS": medications if medications else ["None documented"],
        "ALLERGIES": allergies if allergies else ["None documented"],
        "FAMILY_HISTORY": family_lines if family_lines else ["None documented"],
        "SOCIAL_HISTORY": social_lines if social_lines else ["None documented"],
        "PREVIOUS_REPORT_OCR_HISTORY": doc_lines if doc_lines else ["None uploaded"],
        "RELEVANT_INVESTIGATIONS": investigations if investigations else ["None documented"],
        "SAFETY_URGENT_FLAGS": safety_lines if safety_lines else ["None detected"],
        "MAIN_CLINICAL_PROBLEM": main_problem,
        "ROUTED_DEPARTMENT": "",
        "ROUTING_REASON": "",
        "IMPORTANT_UNKNOWN_NEEDS_CLARIFICATION": needs_clarification if needs_clarification else ["None"],
    }

    return summary


def _identify_main_problem(memory: Dict[str, Any]) -> str:
    active = []
    for name, symptom in memory.get("symptoms", {}).items():
        if isinstance(symptom, dict) and symptom.get("present"):
            parts = [name]
            if symptom.get("duration"):
                parts.append(f"for {symptom['duration']}")
            if symptom.get("location"):
                parts.append(f"in {symptom['location']}")
            if symptom.get("severity"):
                parts.append(f"{symptom['severity']}")
            active.append(" ".join(parts))

    if not active:
        return "Not yet determined"

    if len(active) == 1:
        return active[0]

    primary_candidates = [a for a in active if any(
        kw in a.lower() for kw in ["fever", "chest", "breathing", "headache", "abdominal", "pain", "vomiting", "cough"]
    )]
    if primary_candidates:
        return primary_candidates[0]

    return active[0]


def _is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def generate_llm_summary(memory: Dict[str, Any]) -> str:
    structured = generate_doctor_summary(memory)
    flat = flatten_answers(memory)

    prompt = """Create a clinician-reviewable MediKiosk patient handoff summary.
Do not diagnose, prescribe, or invent facts. Use only the supplied patient information.
Clearly distinguish patient-reported information from document-derived information.
Do not repeat the same fact multiple times.

Return ONLY valid JSON with this structure:
{
  "summary_text": "human-readable doctor handoff",
  "structured": <the structured summary object>
}

STRUCTURED DATA:
""" + json.dumps(structured, ensure_ascii=False)

    fallback = {
        "summary_text": json.dumps(structured, ensure_ascii=False),
        "structured": structured,
    }

    try:
        raw, source = generate_json(prompt, json.dumps(fallback, ensure_ascii=False))
        if isinstance(raw, dict):
            return raw.get("summary_text", fallback["summary_text"])
        return str(raw or fallback["summary_text"])
    except Exception:
        return fallback["summary_text"]
