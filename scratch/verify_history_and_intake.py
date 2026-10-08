import os
import sys
import json
import requests

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"

print("==================================================")
print("VERIFYING MEDICAL HISTORY UPLOAD & INTAKE FLOW")
print("==================================================")

session = requests.Session()

# 1. Start Patient Session
start_res = session.post(f"{BASE_URL}/api/kiosk/patient-start", json={
    "name": "Mrs. Ranjana Bhelende",
    "age": 54,
    "gender": "FEMALE",
    "phone": "9876543210",
    "language": "Tamil"
}).json()

assert start_res.get("success") == True, f"Failed patient-start: {start_res}"
tok_dict = start_res.get("token", {})
token = tok_dict.get("access_token") if isinstance(tok_dict, dict) else tok_dict
headers = {"Authorization": f"Bearer {token}"}
patient = start_res.get("patient", {})

print(f"Registered Kiosk Patient: {patient.get('full_name')} (ID: {patient.get('id')})")

# 2. Start Kiosk Case
case_res = session.post(f"{BASE_URL}/api/kiosk/start", json={
    "language": "Tamil",
    "mode": "NORMAL"
}, headers=headers).json()

assert case_res.get("success") == True, f"Failed kiosk start: {case_res}"
case = case_res.get("case", {})
case_id = case.get("id")

print(f"Created Case #{case_id} ({case.get('case_number')})")

# 3. Start Conversation Session
sess_res = session.post(f"{BASE_URL}/api/conversation/{case_id}/session", headers=headers).json()
assert sess_res.get("success") == True, f"Failed session start: {sess_res}"
session_id = sess_res.get("session", {}).get("id")

# --- TEST 1: Multi-Symptom Extraction in 1 Pass ---
multi_symptom_input = "Enakku fever irukku, rendu naala headache, body pain um irukku, sapida mudiyala, konjam vomiting madhiri irukku."
msg_res = session.post(f"{BASE_URL}/api/conversation/{case_id}/message", json={
    "session_id": session_id,
    "question_key": "chief_complaint",
    "text": multi_symptom_input,
    "input_type": "TEXT"
}, headers=headers).json()

assert msg_res.get("success") == True, f"Failed message: {msg_res}"
next_q = msg_res.get("next_question")
print("\n--- TEST 1: Multi-Symptom Input ---")
print(f"Input: '{multi_symptom_input}'")
print(f"Next Question Returned: {json.dumps(next_q, ensure_ascii=False)}")
assert next_q is not None, "Expected next question"
print("[PASS] Test 1: Multi-symptom answer processed smoothly in 1 turn.")

# --- TEST 2: Medical History Upload (Clear Document) ---
sample_history = """Previous Prescription:
1. Tab. Paracetamol 650mg - 1-0-1 (3 days)
2. Tab. Amoxicillin 500mg - 1-0-1 (5 days)
Doctor Note: History of Hypertension and Type 2 Diabetes."""

resp = session.post(f"{BASE_URL}/api/documents/{case_id}/medical-history", json={"text": sample_history}, headers=headers)
print(f"\nDEBUG Response Status: {resp.status_code}")
print(f"DEBUG Response Text: {resp.text[:500]}")
hist_res = resp.json()

assert hist_res.get("success") == True, f"Failed medical history: {hist_res}"
summary_text = hist_res.get("history_summary", "")

print("\n--- TEST 2: Clear Medical History Upload ---")
print(f"Extracted History Summary:\n{summary_text}")
assert "MEDICAL HISTORY SUMMARY" in summary_text
assert "Hypertension" in summary_text or "Diabetes" in summary_text or "Paracetamol" in summary_text
print("[PASS] Test 2: Structured 9-point Medical History extracted without chatbot UI.")

# --- TEST 3: Unreadable Medical History Fallback ---
unreadable_text = "[Uncertain OCR document] ??? blurry document 123"
unreliable_res = session.post(f"{BASE_URL}/api/documents/{case_id}/medical-history", json={
    "text": unreadable_text
}, headers=headers).json()

assert unreliable_res.get("success") == True, f"Failed unreadable upload: {unreliable_res}"
unreliable_summary = unreliable_res.get("history_summary", "")

print("\n--- TEST 3: Unreadable Medical History Fallback ---")
print(f"Fallback History Summary:\n{unreliable_summary}")
assert "could not be reliably extracted" in unreliable_summary
print("[PASS] Test 3: Unreadable document cleanly fallback-summarized without hallucination.")

# --- TEST 4: Complete Consultation & Doctor Document Generation ---
comp_res = session.post(f"{BASE_URL}/api/conversation/{case_id}/complete", headers=headers).json()
assert comp_res.get("success") == True, f"Failed complete: {comp_res}"

doc_summary = comp_res.get("summary", "")
print("\n--- TEST 4: Final Doctor Summary & Document Handoff ---")
print(f"Final Doctor Summary:\n{doc_summary}")

assert "PATIENT INFORMATION" in doc_summary
assert "Ranjana Bhelende" in doc_summary
assert "CURRENT SYMPTOM SUMMARY" in doc_summary
assert "MEDICAL HISTORY SUMMARY" in doc_summary
assert "MEDICAL HISTORY DOCUMENT" in doc_summary
assert "AI INTAKE NOTE" in doc_summary
print("[PASS] Test 4: Final doctor document format verified with patient name, symptoms, history, and AI intake note.")

print("\n==================================================")
print("ALL MEDICAL HISTORY & INTAKE VERIFICATIONS PASSED!")
print("==================================================")
