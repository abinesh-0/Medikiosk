import sys, os
os.environ.setdefault('FLASK_ENV', 'testing')
sys.path.insert(0, '.')

from routes.ai_routes import detect_query_language

tests = [
    ("indha report la enna abnormal ah irukku?", "English", "Tamil"),
    ("hemoglobin low ah?",                       "English", "Tamil"),
    ("platelet count evlo?",                     "English", "Tamil"),
    ("romba low ah irukku?",                     "English", "Tamil"),
    ("enna irukku report la?",                   "English", "Tamil"),
    ("sollunga doctor yaar?",                    "English", "Tamil"),
    ("irukku normal ah?",                        "English", "Tamil"),
    ("What is my hemoglobin level?",             "English", "English"),
    ("What are the prescribed medications?",     "English", "English"),
    ("Who is the Prime Minister?",               "English", "English"),
    ("Are any values abnormal?",                 "English", "English"),
    # Tamil Unicode tests
    ("en report la enna solludu?",               "English", "Tamil"),
    ("normal ah irukka?",                        "English", "Tamil"),
]

passed, failed = 0, 0
lines = ["=== Backend Language Detection Test ==="]
for text, ui_lang, expected in tests:
    result = detect_query_language(text, ui_lang)
    ok = result == expected
    status = "PASS" if ok else "FAIL"
    if ok: passed += 1
    else: failed += 1
    lines.append(f"  [{status}] \"{text[:50]}\" => {result} (expected {expected})")

lines.append(f"\nResult: {passed}/{len(tests)} passed, {failed} failed")
print("\n".join(lines))
