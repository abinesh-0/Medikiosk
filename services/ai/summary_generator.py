import json
from services.ai.llm_service import generate_json


def _local(case, history, ayush, answers, documents, flags, assignment, language):
    ta = language == 'Tamil'
    patient = getattr(case, 'patient', None) or (case.visit.patient if getattr(case, 'visit', None) else None)
    p_name = getattr(patient, 'full_name', 'Patient') if patient else 'Patient'
    p_age = getattr(patient, 'age', 'N/A') if patient else 'N/A'
    p_gender = getattr(patient, 'gender', 'N/A') if patient else 'N/A'

    doc_title = f"{p_name.replace(' ', '_')}_Clinical_Intake_Summary"

    lines = []
    lines.append(f"DOCUMENT TITLE: {doc_title}\n")
    lines.append("--------------------------------")
    lines.append("PATIENT INFORMATION")
    lines.append("--------------------------------")
    lines.append(f"Patient Name: {p_name}")
    lines.append(f"Age: {p_age}")
    lines.append(f"Gender: {p_gender}\n")

    lines.append("--------------------------------")
    lines.append("CURRENT SYMPTOM SUMMARY")
    lines.append("--------------------------------")
    cc = history.get('chief_complaint') or getattr(case, 'chief_complaint', '') or 'Not stated'
    lines.append(f"Main complaint: {cc}")
    if history.get('history_present_illness'):
        lines.append(f"Timeline / Progression: {history['history_present_illness']}")
    if history.get('severity'):
        lines.append(f"Severity: {history['severity']}")
    if history.get('associated_symptoms'):
        lines.append(f"Associated symptoms: {history['associated_symptoms']}")

    if answers:
        lines.append("\nPatient intake answers:")
        for a in answers:
            q_key = str(a.get('question_key', '')).replace('_', ' ').title()
            lines.append(f"  • {q_key}: {a.get('answer_text')}")

    lines.append("\n--------------------------------")
    lines.append("MEDICAL HISTORY SUMMARY")
    lines.append("--------------------------------")
    lines.append(f"Previous conditions: {history.get('past_medical_history') or 'Not available in uploaded document.'}")
    lines.append(f"Previous surgeries / procedures: {history.get('past_surgical_history') or 'Not available in uploaded document.'}")
    lines.append(f"Previous hospitalizations: Not available in uploaded document.")
    lines.append(f"Known allergies: {history.get('allergy_history') or 'Not available in uploaded document.'}")
    lines.append(f"Current / previous medications: {history.get('medication_history') or 'Not available in uploaded document.'}")
    lines.append(f"Relevant investigations: {history.get('investigation_history') or 'Not available in uploaded document.'}")
    lines.append(f"Family / social history: {history.get('family_history') or history.get('social_history') or 'Not available in uploaded document.'}")

    lines.append("\n--------------------------------")
    lines.append("MEDICAL HISTORY DOCUMENT")
    lines.append("--------------------------------")
    med_docs = [d for d in (documents or []) if d.get('document_type') == 'MEDICAL_HISTORY' or 'history' in str(d.get('original_filename', '')).lower()]
    if med_docs:
        for md in med_docs:
            fname = md.get('original_filename', 'Medical_History_Doc')
            ex = md.get('extraction') or {}
            ext_json = ex.get('extraction_json') or ''
            is_unreliable = ex.get('verification_required') or 'unreliable' in ext_json.lower() or 'could not be reliably' in ext_json.lower()
            if is_unreliable:
                lines.append(f"Status: Medical history could not be reliably extracted from the uploaded document ({fname}).")
                lines.append(f"Original Document Attached for Doctor Review: [FILE ATTACHMENT: {fname}] (Path: {md.get('file_path', fname)})")
                lines.append("Doctor Action Required: Please visually inspect the attached original image/PDF document.")
            else:
                lines.append(f"Document File: {fname}")
                summary_str = ex.get('clinical_summary') or ''
                if summary_str:
                    lines.append(f"Extracted Summary: {summary_str}")
                else:
                    lines.append("Extracted Medical History Summary included above.")
    else:
        lines.append("No previous medical history document uploaded.")

    if flags:
        lines.append("\n--------------------------------")
        lines.append("SAFETY SCREENING")
        lines.append("--------------------------------")
        for f in flags:
            lines.append(f"• {f.get('flag_title')} ({f.get('severity')})")
    else:
        lines.append("\nSafety Screening: No active red flags detected.")

    if assignment:
        lines.append(f"\nAssigned doctor: {assignment['doctor_name']} — {assignment['department']}")

    lines.append("\n--------------------------------")
    lines.append("AI INTAKE NOTE")
    lines.append("--------------------------------")
    lines.append("Note: This is an AI-assisted patient intake summary and medical report record. Clinician verification of original records and patient details required before final diagnosis or prescription.")
    return '\n'.join(lines)


def generate(case, history, ayush, answers, documents, flags, assignment, language):
    fallback_text = _local(case, history, ayush, answers, documents, flags, assignment, language)
    fallback = {
        'language': language,
        'summary_text': fallback_text,
        'timeline': history.get('history_present_illness'),
        'chief_complaint': history.get('chief_complaint') or case.chief_complaint,
        'symptoms': history.get('associated_symptoms'),
        'severity': history.get('severity'),
        'past_history': history.get('past_medical_history'),
        'medications': history.get('medication_history'),
        'allergies': history.get('allergy_history'),
        'investigations': history.get('investigation_history'),
        'documents': documents,
        'safety_screen': flags,
        'recommended_department': assignment.get('department') if assignment else None,
        'assigned_doctor': assignment.get('doctor_name') if assignment else None,
        'next_review_points': ['Clinician verification required'],
        'ai_source': 'LOCAL_RULES'
    }

    prompt = """Create a clinician-reviewable MediKiosk intake handoff.
Do not diagnose, prescribe, or invent facts. Use only the supplied patient answers and extracted document facts.

IMPORTANT ORDER FOR THE SUMMARY:
1. Chief complaint in the patient's own words.
2. Timeline: when it started, duration, onset and progression.
3. Main symptoms and associated symptoms.
4. Severity / functional impact.
5. Relevant positives and relevant negatives that the patient actually stated.
6. Past medical/surgical history.
7. Current medicines and allergies.
8. Relevant family, social and lifestyle information.
9. Previous investigations and medical-document findings, clearly separated from today's history.
10. Safety screening / red flags.
11. Department routing and assigned doctor.
12. Missing or clinician-review points.

For documents, distinguish OCR/extracted facts from patient-reported facts. Preserve dates, units, medicine names and values. Do not convert an uncertain OCR value into a fact.
Return JSON only with:
{
  "summary_text":"human-readable doctor handoff",
  "chief_complaint":"",
  "timeline":"",
  "symptoms":[],
  "relevant_negatives":[],
  "severity":"",
  "past_history":"",
  "medications":[],
  "allergies":[],
  "lifestyle":"",
  "investigations":[],
  "documents":[],
  "safety_screen":[],
  "recommended_department":"",
  "assigned_doctor":"",
  "next_review_points":[]
}

DATA:
""" + json.dumps({
        'case_number': case.case_number,
        'history': history,
        'ayush': ayush or {},
        'answers': answers,
        'documents': documents,
        'red_flags': flags,
        'assignment': assignment,
        'language': language,
    }, ensure_ascii=False)

    raw, source = generate_json(prompt, json.dumps(fallback, ensure_ascii=False), max_tokens=600)
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError('Invalid summary JSON')
        data['ai_source'] = source
        if not data.get('summary_text'):
            data['summary_text'] = fallback_text
        return str(data['summary_text']), data
    except Exception:
        fallback['ai_source'] = source
        return fallback_text, fallback
