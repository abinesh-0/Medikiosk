# tests/test_no_repeat.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_no_repeat_fever_duration():
    """2 naala fever must NOT block cough duration."""
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True, duration="2 days")
    register_symptom(m, "cough", present=True)
    assert is_covered(m, "fever_duration") is True
    assert is_covered(m, "resp_duration") is False


def test_no_repeat_headache_location():
    """thala vali must NOT cause head_location to be re-asked."""
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered,
    )
    m = empty_memory()
    register_symptom(m, "headache", present=True, location="head")
    assert is_covered(m, "head_location") is True
    assert is_covered(m, "head_onset") is False


def test_no_repeat_abdominal_location():
    """vayiru vali must NOT cause abd_location to be re-asked."""
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered,
    )
    m = empty_memory()
    register_symptom(m, "abdominal_pain", present=True, location="abdomen")
    assert is_covered(m, "abd_location") is True


def test_no_repeat_fever_duration_for_headache():
    """fever duration must NOT cover headache duration."""
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered_by_semantic,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True, duration="2 days")
    register_symptom(m, "headache", present=True)
    assert is_covered_by_semantic(m, "fever_duration") is True
    assert is_covered_by_semantic(m, "head_duration") is False


def test_no_repeat_local_fact_fever_duration_for_cough():
    """Local extraction: fever duration must NOT cover cough duration."""
    from services.ai.fact_extractor import local_extract
    result = local_extract("2 days fever, cough")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert symptoms["fever"].get("duration") is not None
    assert symptoms["cough"].get("duration") is None


def test_no_repeat_onset_not_global():
    """Duration for one symptom must NOT cover onset for another."""
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered_by_semantic,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True, duration="2 days")
    register_symptom(m, "chest_pain", present=True)
    assert is_covered_by_semantic(m, "fever_duration") is True
    assert is_covered_by_semantic(m, "chest_onset") is False


def test_negation_is_denied_not_unknown():
    """vomiting illa should be denied, not unknown."""
    from services.ai.clinical_memory import (
        empty_memory, register_negative, is_denied,
    )
    m = empty_memory()
    register_negative(m, "vomiting")
    assert is_denied(m, "vomiting") is True


def test_absent_vs_unknown():
    """vomiting absent is different from vomiting unknown."""
    from services.ai.clinical_memory import (
        empty_memory, register_negative, register_symptom, is_denied, is_covered,
    )
    m = empty_memory()
    register_negative(m, "vomiting")
    assert is_denied(m, "vomiting") is True
    m2 = empty_memory()
    register_symptom(m2, "vomiting", present=False)
    assert is_covered(m2, "vomiting") is True


def test_thala_vali_covers_headache_and_location():
    from services.ai.fact_extractor import local_extract
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered,
    )
    result = local_extract("thala vali irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "headache" in symptoms
    m = empty_memory()
    register_symptom(m, "headache", present=True, location="head")
    assert is_covered(m, "head_location") is True


def test_vayiru_vali_covers_abdominal_and_location():
    from services.ai.fact_extractor import local_extract
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered,
    )
    result = local_extract("vayiru vali irukku")
    symptoms = {s["name"]: s for s in result["symptoms"]}
    assert "abdominal_pain" in symptoms
    m = empty_memory()
    register_symptom(m, "abdominal_pain", present=True, location="abdomen")
    assert is_covered(m, "abd_location") is True


def test_cough_duration_only_covered_when_cough_has_duration():
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered_by_semantic,
    )
    m = empty_memory()
    register_symptom(m, "cough", present=True)
    assert is_covered_by_semantic(m, "resp_duration") is False
    register_symptom(m, "cough", present=True, duration="3 days")
    assert is_covered_by_semantic(m, "resp_duration") is True


def test_no_repeat_after_multiple_symptoms_first_turn():
    """All facts from a multi-symptom answer must be covered."""
    from services.ai.fact_extractor import local_extract
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered, merge_extraction,
    )
    result = local_extract("2 naala fever irukku, thala vali, vomiting illa")
    m = empty_memory()
    merge_extraction(m, result)
    assert is_covered(m, "fever_duration") is True
    assert is_covered(m, "head_location") is True
    assert is_covered(m, "vomiting") is True


def test_new_symptom_creates_new_question_path():
    """Adding a new symptom later should make its questions eligible."""
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True)
    assert is_covered(m, "fever_duration") is False
    assert is_covered(m, "fever_pattern") is False


def test_denied_symptom_not_considered_active():
    from services.ai.clinical_memory import (
        empty_memory, register_negative, is_covered,
    )
    m = empty_memory()
    register_negative(m, "vomiting")
    assert is_covered(m, "vomiting") is True


def test_conflicting_sources_preserved():
    """Patient says stopped medicine while OCR says current."""
    from services.ai.clinical_memory import empty_memory, set_fact, get_fact_meta
    m = empty_memory()
    set_fact(m, "medication_a", "Med A (historical, stopped)", source="ocr", confidence=0.9)
    set_fact(m, "medication_a_current", "stopped last month", source="patient", confidence=0.95)
    meta = get_fact_meta(m, "medication_a")
    assert meta is not None
    assert meta["source"] == "ocr"
