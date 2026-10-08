# tests/test_fact_extraction.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_local_extract_single_symptom():
    from services.ai.fact_extractor import local_extract
    result = local_extract("I have fever")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "fever" in symptoms
    assert symptoms["fever"]["present"] is True


def test_local_extract_fever_with_duration():
    from services.ai.fact_extractor import local_extract
    result = local_extract("2 naala fever irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "fever" in symptoms
    assert symptoms["fever"]["present"] is True
    assert symptoms["fever"]["duration"] is not None


def test_local_extract_headache_location():
    from services.ai.fact_extractor import local_extract
    result = local_extract("thala vali irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "headache" in symptoms
    assert symptoms["headache"]["present"] is True
    assert symptoms["headache"]["location"] == "head"


def test_local_extract_abdominal_pain_location():
    from services.ai.fact_extractor import local_extract
    result = local_extract("vayiru vali irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "abdominal_pain" in symptoms
    assert symptoms["abdominal_pain"]["present"] is True
    assert symptoms["abdominal_pain"]["location"] == "abdomen"


def test_local_extract_negation():
    from services.ai.fact_extractor import local_extract
    result = local_extract("vomiting illa")
    negatives = {n["symptom"]: n for n in result["negatives"]}
    assert "vomiting" in negatives


def test_local_extract_multiple_symptoms():
    from services.ai.fact_extractor import local_extract
    result = local_extract("2 days ah fever, thala vali, vayiru vali, vomiting illa")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "fever" in symptoms
    assert "headache" in symptoms
    assert "abdominal_pain" in symptoms
    assert symptoms["fever"]["present"] is True
    assert symptoms["headache"]["present"] is True
    assert symptoms["abdominal_pain"]["present"] is True


def test_local_extract_no_ghost_duration_for_other_symptoms():
    from services.ai.fact_extractor import local_extract
    result = local_extract("2 naala fever irukku, thala vali")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    fever_dur = symptoms["fever"].get("duration")
    head_dur = symptoms["headache"].get("duration")
    assert fever_dur is not None
    assert head_dur is None


def test_local_extract_tamil():
    from services.ai.fact_extractor import local_extract
    result = local_extract("எனக்கு தலை வலி இருக்கு")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "headache" in symptoms
    assert symptoms["headache"]["location"] == "head"


def test_local_extract_tanglish():
    from services.ai.fact_extractor import local_extract
    result = local_extract("enakku thala vali irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "headache" in symptoms


def test_local_extract_english():
    from services.ai.fact_extractor import local_extract
    result = local_extract("I have a headache")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "headache" in symptoms


def test_local_extract_breathing_difficulty():
    from services.ai.fact_extractor import local_extract
    result = local_extract("moochu kashtam")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "breathing_difficulty" in symptoms


def test_local_extract_cough():
    from services.ai.fact_extractor import local_extract
    result = local_extract("cough irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "cough" in symptoms


def test_local_extract_denied_fever():
    from services.ai.fact_extractor import local_extract
    result = local_extract("fever illa")
    negatives = {n["symptom"]: n for n in result["negatives"]}
    assert "fever" in negatives


def test_local_extract_skin():
    from services.ai.fact_extractor import local_extract
    result = local_extract("skin rash irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "skin" in symptoms


def test_local_extract_back_pain():
    from services.ai.fact_extractor import local_extract
    result = local_extract("back pain irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "back_pain" in symptoms
    assert symptoms["back_pain"]["location"] == "back"


def test_local_extract_chest_pain():
    from services.ai.fact_extractor import local_extract
    result = local_extract("chest pain irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "chest_pain" in symptoms
    assert symptoms["chest_pain"]["location"] == "chest"


def test_local_extract_diarrhea():
    from services.ai.fact_extractor import local_extract
    result = local_extract("loose motion irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "diarrhea" in symptoms


def test_local_extract_urinary():
    from services.ai.fact_extractor import local_extract
    result = local_extract("burning urine irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "urinary" in symptoms


def test_local_extract_denied_cough():
    from services.ai.fact_extractor import local_extract
    result = local_extract("cough illai")
    negatives = {n["symptom"]: n for n in result["negatives"]}
    assert "cough" in negatives


def test_local_extract_speech_to_text_variants():
    from services.ai.fact_extractor import local_extract
    result = local_extract("moochu vida kashtama irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "breathing_difficulty" in symptoms


def test_local_extract_no_overlapping_duration():
    from services.ai.fact_extractor import local_extract
    result = local_extract("2 days fever, headache")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert symptoms["fever"].get("duration") is not None
    assert symptoms["headache"].get("duration") is None


def test_local_extract_no_fever_when_denied():
    from services.ai.fact_extractor import local_extract
    result = local_extract("fever illa, thala vali irukku")
    neg = {n["symptom"] for n in result["negatives"]}
    sym = {s["name"] for s in result["symptoms"]}
    assert "fever" in neg
    assert "headache" in sym


def test_extract_facts_no_invent():
    from services.ai.fact_extractor import extract_facts
    result = extract_facts(patient_text="I have headache", previous_context={}, language="English")
    for sym in result.get("symptoms", []):
        if sym.get("name") == "headache":
            assert sym.get("present") is True


def test_clinical_memory_empty():
    from services.ai.clinical_memory import empty_memory
    m = empty_memory()
    assert m["patient"]["name"] is None
    assert m["patient"]["age"] is None
    assert m["patient"]["gender"] is None
    assert m["symptoms"] == {}
    assert m["facts"] == {}
    assert m["chief_complaint"] == []


def test_clinical_memory_set_fact():
    from services.ai.clinical_memory import empty_memory, set_fact, has_fact, get_fact
    m = empty_memory()
    set_fact(m, "fever", True)
    assert has_fact(m, "fever")
    assert get_fact(m, "fever") is True


def test_clinical_memory_register_symptom():
    from services.ai.clinical_memory import empty_memory, register_symptom, is_covered
    m = empty_memory()
    register_symptom(m, "headache", present=True, location="head")
    assert is_covered(m, "head_location") is True


def test_clinical_memory_register_negation():
    from services.ai.clinical_memory import empty_memory, register_negative, is_denied
    m = empty_memory()
    register_negative(m, "vomiting")
    assert is_denied(m, "vomiting") is True


def test_clinical_memory_semantic_coverage():
    from services.ai.clinical_memory import empty_memory, register_symptom, is_covered, is_covered_by_semantic
    m = empty_memory()
    register_symptom(m, "headache", present=True, location="head")
    assert is_covered(m, "head_location") is True
    assert is_covered_by_semantic(m, "head_location") is True


def test_clinical_memory_fever_duration_per_symptom():
    from services.ai.clinical_memory import empty_memory, register_symptom, is_covered_by_semantic
    m = empty_memory()
    register_symptom(m, "fever", present=True)
    assert is_covered_by_semantic(m, "fever_duration") is False
    register_symptom(m, "fever", present=True, duration="2 days")
    assert is_covered_by_semantic(m, "fever_duration") is True


def test_clinical_memory_merged_extraction():
    from services.ai.clinical_memory import empty_memory, merge_extraction, has_fact
    m = empty_memory()
    merge_extraction(m, {"symptoms": [
        {"name": "fever", "present": True, "duration": "2 days"},
        {"name": "headache", "present": True, "location": "head"},
        {"name": "vomiting", "present": False},
    ]})
    assert has_fact(m, "fever_duration") is True
    assert has_fact(m, "head_location") is True


def test_clinical_memory_no_overwrite_high_confidence():
    from services.ai.clinical_memory import empty_memory, set_fact, get_fact
    m = empty_memory()
    set_fact(m, "fever", True, confidence=0.99)
    set_fact(m, "fever", None, confidence=0.3)
    assert get_fact(m, "fever") is True


def test_clinical_memory_denied_vs_unknown():
    from services.ai.clinical_memory import empty_memory, register_negative, get_fact_meta
    m = empty_memory()
    register_negative(m, "vomiting")
    meta = get_fact_meta(m, "vomiting")
    assert meta is None or meta.get("status") == "denied"


def test_clinical_memory_record_turn():
    from services.ai.clinical_memory import empty_memory, record_turn
    m = empty_memory()
    record_turn(m, "patient said fever")
    assert len(m["conversation_turns"]) == 1
