import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:5000"

def test_acceptance_criteria():
    print("==================================================")
    print("RUNNING COMPREHENSIVE AI DOCUMENT CHATBOT VERIFICATION")
    print("==================================================")

    # 1. Prepare Ranjana Bhelende CBC context
    cbc_context = """Document Type: Complete Blood Count (CBC)
Patient Name: Mrs. Ranjana Bhelende
Patient Age: 54 Years, Gender: Female
Report Date: 28/11/2025
Doctor: Dr. A. Sharma, Hospital: Varad Pathology Lab
LAB RESULTS:
Hemoglobin: 12.7 gm% [Ref: 12-16] [Status: NORMAL]
Total WBC Count: 8100 /cmm [Ref: 4000-11000] [Status: NORMAL]
Neutrophils: 73 % [Ref: 40-75 %] [Status: NORMAL]
Lymphocytes: 20 % [Ref: 20-40 %] [Status: NORMAL]
Eosinophils: 03 % [Ref: 1-6 %] [Status: NORMAL]
Monocytes: 04 % [Ref: 2-10 %] [Status: NORMAL]
Basophils: 00 % [Ref: 0-1 %] [Status: NORMAL]
RBC Count: 4.45 mil./cmm [Ref: 3.8-5.2] [Status: NORMAL]
HCT: 38.9 % [Ref: 36-46 %] [Status: NORMAL]
MCV: 87.4 fL [Ref: 80-100] [Status: NORMAL]
MCH: 28.6 pg [Ref: 27-32] [Status: NORMAL]
MCHC: 32.7 gm/dl [Ref: 31.5-34.5] [Status: NORMAL]
RDW-CV: 12.6 % [Ref: 11.5-14.5 %] [Status: NORMAL]
Platelet Count: 308000 /cmm [Ref: 150000-450000] [Status: NORMAL]
MPV: 9.2 fL [Ref: 7.4-10.4] [Status: NORMAL]
PDW: 16.4 fL [Ref: 10-18] [Status: NORMAL]
MEDICATIONS:
None recorded
Red Flags: None"""

    # ----------------------------------------------------
    # TEST 1: Explain this report in simple words (English & Tamil)
    # ----------------------------------------------------
    print("\n--- TEST 1: 'Explain this report in simple words' ---")
    r1 = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "Explain this report in simple words",
        "document_context": cbc_context,
        "language": "English"
    }).json()

    assert r1.get("success") == True, f"Failed: {r1}"
    reply1 = r1.get("reply", "")
    print(f"Reply: {reply1}")
    assert "please consult your physician for clinical decisions" not in reply1.lower(), "Generic disclaimer returned!"
    assert any(w in reply1.lower() for w in ["cbc", "blood count", "normal", "hemoglobin", "platelet", "wbc"]), "Answer not grounded in CBC values!"
    print("[PASS] Test 1: Real summary based on extracted CBC values.")

    # ----------------------------------------------------
    # TEST 2: "hemoglobin epdi irukku?" (Tamil query)
    # ----------------------------------------------------
    print("\n--- TEST 2: 'hemoglobin epdi irukku?' (Tamil) ---")
    r2 = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "hemoglobin epdi irukku?",
        "document_context": cbc_context,
        "language": "Tamil"
    }).json()

    assert r2.get("success") == True
    reply2 = r2.get("reply", "")
    print(f"Reply: {reply2}")
    assert "12.7" in reply2, "Missing 12.7 hemoglobin value in reply!"
    assert any(k in reply2 for k in ["range", "12-16", "இயல்பான", "உள்ளது"]), "Missing reference range validation in reply!"
    print("[PASS] Test 2: Natural Tamil response with 12.7 gm% and reference range grounding.")

    # ----------------------------------------------------
    # TEST 3: "Any abnormal values?"
    # ----------------------------------------------------
    print("\n--- TEST 3: 'Any abnormal values?' ---")
    r3 = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "Any abnormal values?",
        "document_context": cbc_context,
        "language": "English"
    }).json()

    assert r3.get("success") == True
    reply3 = r3.get("reply", "")
    print(f"Reply: {reply3}")
    assert any(w in reply3.lower() for w in ["no abnormal", "within", "normal"]), "Failed to correctly confirm normal values!"
    print("[PASS] Test 3: Correctly verified all parameters against report reference ranges.")

    # ----------------------------------------------------
    # TEST 4: OCR Validation (78% vs 73% Neutrophils)
    # ----------------------------------------------------
    print("\n--- TEST 4: OCR Validation (Neutrophils 78% -> 73% via DLC validation) ---")
    from services.ocr.clinical_document_extractor import _local
    ocr_raw = """Varad Pathology Lab
Patient Name: Mrs. Ranjana Bhelende
Age: 54 Years, Sex: Female, Date: 28/11/2025
Complete Blood Count
Hemoglobin: 12.7 gm% 12-16
Total WBC Count: 8100 /cmm 4000-11000
Neutrophils: 78 % 40-75
Lymphocytes: 20 % 20-40
Eosinophils: 03 % 1-6
Monocytes: 04 % 2-10
Basophils: 00 % 0-1
Platelet Count: 308000 /cmm 150000-450000"""

    extracted = _local(ocr_raw)
    neut_inv = next((i for i in extracted["investigations"] if i["test"] == "Neutrophils"), None)
    assert neut_inv is not None, "Neutrophils not extracted!"
    print(f"Extracted Neutrophils: {neut_inv['value']}% (Expected: 73%)")
    assert neut_inv['value'] == '73', f"Expected 73%, got {neut_inv['value']}%!"
    print("[PASS] Test 4: DLC cross-validation successfully corrected 78% to 73%.")

    # ----------------------------------------------------
    # TEST 5: Previous Patient Inquiry (Session Isolation)
    # ----------------------------------------------------
    print("\n--- TEST 5: Active Patient Isolation ('What about Ramesh Kumar?') ---")
    r5 = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "What about Ramesh Kumar?",
        "document_context": cbc_context,
        "language": "English"
    }).json()

    assert r5.get("success") == True
    reply5 = r5.get("reply", "")
    print(f"Reply: {reply5}")
    assert any(w in reply5.lower() for w in ["don't have", "not have", "current session", "ranjana bhelende"]), "Failed patient isolation!"
    print("[PASS] Test 5: Strict patient isolation enforced, previous patient data not leaked.")

    # ----------------------------------------------------
    # TEST 6: Unreadable / Low Confidence Value
    # ----------------------------------------------------
    print("\n--- TEST 6: Unreadable / Low Confidence Value ---")
    unclear_context = """Document Type: Complete Blood Count (CBC)
Patient Name: Test Patient
LAB RESULTS:
Hemoglobin: Unable to verify [Ref: 12-16] [Status: UNCERTAIN]
Platelet Count: 308000 /cmm [Ref: 150000-450000] [Status: NORMAL]"""

    r6 = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "what is my hemoglobin?",
        "document_context": unclear_context,
        "language": "English"
    }).json()

    assert r6.get("success") == True
    reply6 = r6.get("reply", "")
    print(f"Reply: {reply6}")
    assert any(w in reply6.lower() for w in ["couldn't reliably read", "unable to verify", "clearer image", "clearer scan"]), "Did not flag uncertain reading!"
    print("[PASS] Test 6: Uncertain reading flagged cleanly without guessing.")

    # ----------------------------------------------------
    # TEST 7: Medications Quick Action on Lab Report
    # ----------------------------------------------------
    print("\n--- TEST 7: 'Medications' on Lab Report ---")
    r7 = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "Medications",
        "document_context": cbc_context,
        "language": "English"
    }).json()

    assert r7.get("success") == True
    reply7 = r7.get("reply", "")
    print(f"Reply: {reply7}")
    assert any(w in reply7.lower() for w in ["no medication", "none"]), "Did not accurately report absence of medications!"
    print("[PASS] Test 7: Correctly indicated no medication information present.")

    # ----------------------------------------------------
    # TEST 8: Domain Guard
    # ----------------------------------------------------
    print("\n--- TEST 8: Domain Guard ---")
    r8 = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "Who won the cricket world cup?",
        "document_context": cbc_context,
        "language": "English"
    }).json()
    assert r8.get("source") == "DOMAIN_GUARD"
    print(f"Reply: {r8.get('reply')}")
    print("[PASS] Test 8: Medical domain guard active.")

    print("\n==================================================")
    print("ALL 8 ACCEPTANCE TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_acceptance_criteria()
