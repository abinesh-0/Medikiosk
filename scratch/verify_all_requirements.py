import sys
import os
sys.path.insert(0, '.')
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_language_detection():
    print("\n--- TEST 1: Language Detection in ai_routes ---")
    from routes.ai_routes import detect_query_language

    test_cases = [
        # Explicit user_selected_lang = Tamil
        ("What is my blood sugar?", "Tamil", "Tamil"),
        ("Explain this report", "Tamil", "Tamil"),
        ("இந்த அறிக்கை என்ன சொல்லுது?", "Tamil", "Tamil"),
        
        # Explicit user_selected_lang = English
        ("What is my blood sugar?", "English", "English"),
        ("What are the prescribed medications?", "English", "English"),
        
        # English UI but patient types Tamil / Tanglish
        ("இந்த report என்ன சொல்லுது?", "English", "Tamil"),
        ("indha report la enna abnormal ah irukku?", "English", "Tamil"),
        ("sugar level romba adhigama irukka?", "English", "Tamil"),
        ("maruthuvar enna sonnaru?", "English", "Tamil"),
        ("hemoglobin low ah?", "English", "Tamil"),
        ("blood test la platelet evlo irukku?", "English", "Tamil"),
    ]

    passed = 0
    for text, user_lang, expected in test_cases:
        res = detect_query_language(text, user_lang)
        status = "PASS" if res == expected else f"FAIL (got {res})"
        if res == expected:
            passed += 1
        print(f"[{status}] text='{text[:35]}...' user_lang={user_lang} => {res} (expected {expected})")

    print(f"Result: {passed}/{len(test_cases)} passed.")
    assert passed == len(test_cases), "Language detection tests failed!"


def test_api_endpoints():
    print("\n--- TEST 2: API Endpoints Verification ---")

    # 1. Health / Home check
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"Home page returned {r.status_code}"
    print("[PASS] Home page is up and serving 200 OK")

    # 2. Language command test: "tamil la explain pannu"
    r = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "tamil la explain pannu",
        "document_context": "Patient: Ramesh Kumar\nHbA1c: 8.6%",
        "language": "English"
    })
    data = r.json()
    assert data.get("success") == True, f"Doc-chat failed: {data}"
    assert data.get("source") == "LANG_CONTROL", f"Expected LANG_CONTROL source, got {data.get('source')}"
    assert data.get("language") == "Tamil", f"Expected Tamil language, got {data.get('language')}"
    print(f"[PASS] Language command response: {data.get('reply')[:60]}... (Lang: {data.get('language')})")

    # 3. Out-of-domain test: "who is prime minister"
    r = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "who is the prime minister of India?",
        "document_context": "Patient: Ramesh Kumar\nHbA1c: 8.6%",
        "language": "English"
    })
    data = r.json()
    assert data.get("success") == True
    assert data.get("source") == "DOMAIN_GUARD", f"Expected DOMAIN_GUARD source, got {data.get('source')}"
    print(f"[PASS] Out-of-domain guard response: {data.get('reply')[:60]}... (Lang: {data.get('language')})")

    # 4. Out-of-domain test in Tamil mode
    r = requests.post(f"{BASE_URL}/api/ai/doc-chat", json={
        "message": "who is the prime minister?",
        "document_context": "Patient: Ramesh Kumar\nHbA1c: 8.6%",
        "language": "Tamil"
    })
    data = r.json()
    assert data.get("success") == True
    assert data.get("source") == "DOMAIN_GUARD"
    assert data.get("language") == "Tamil"
    print(f"[PASS] Out-of-domain guard in Tamil: {data.get('reply')[:60]}...")

    # 5. Medical Document Analysis endpoint
    blood_sample = """SRI RAMAKRISHNA HOSPITAL CLINICAL LABORATORY
Patient: Ramesh Kumar, Age: 52, Gender: Male, Date: 18-Sep-2026
TEST RESULTS:
- Fasting Blood Sugar (FBS): 168 mg/dL (Normal: 70-100) [HIGH]
- HbA1c: 8.6 % (Target: < 7.0 %) [ELEVATED]
- Serum Creatinine: 1.4 mg/dL (Normal: 0.7 - 1.2) [BORDERLINE HIGH]"""

    r = requests.post(f"{BASE_URL}/api/ai/doc-analyze", json={
        "text": blood_sample,
        "filename": "Sample_Blood_Test.txt"
    })
    data = r.json()
    assert data.get("success") == True, f"doc-analyze failed: {data}"
    analysis = data.get("analysis", {})
    assert len(analysis.get("investigations", [])) > 0, "No investigations extracted!"
    print(f"[PASS] Doc Analyze extracted {len(analysis.get('investigations', []))} investigations, Document Type: {analysis.get('document_type')}")


if __name__ == "__main__":
    test_language_detection()
    test_api_endpoints()
    print("\nALL BACKEND & API VERIFICATIONS PASSED SUCCESSFULLY!")
