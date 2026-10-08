# tests/test_doctor_summary.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_summary_basic():
    from services.ai.doctor_summary import generate_doctor_summary
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, set_fact, set_patient_info,
    )
    m = empty_memory()
    set_patient_info(m, name="John", age=45, gender="MALE")
    register_symptom(m, "fever", present=True, duration="2 days")
    register_symptom(m, "headache", present=True, location="head")
    register_negative = None

    summary = generate_doctor_summary(m)
    assert summary["PATIENT_INFORMATION"]["name"] == "John"
    assert summary["PATIENT_INFORMATION"]["age"] == "45"
    assert summary["PATIENT_INFORMATION"]["gender"] == "MALE"
    assert len(summary["CURRENT_SYMPTOMS"]) == 2


def test_summary_does_not_duplicate():
    """Each symptom appears only once in CURRENT_SYMPTOMS."""
    from services.ai.doctor_summary import generate_doctor_summary
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True)
    register_symptom(m, "fever", present=True)
    summary = generate_doctor_summary(m)
    names = [s["name"] for s in summary["CURRENT_SYMPTOMS"]]
    assert names.count("fever") == 1


def test_summary_patient_vs_document():
    from services.ai.doctor_summary import generate_doctor_summary
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, set_patient_info,
    )
    m = empty_memory()
    set_patient_info(m, name="Alice", age=30, gender="FEMALE")
    register_symptom(m, "fever", present=True)
    summary = generate_doctor_summary(m)
    assert summary["PATIENT_INFORMATION"]["name"] == "Alice"
    assert "PAST_MEDICAL_HISTORY" in summary


def test_summary_negative_findings():
    from services.ai.doctor_summary import generate_doctor_summary
    from services.ai.clinical_memory import (
        empty_memory, register_negative, register_symptom,
    )
    m = empty_memory()
    register_negative(m, "vomiting")
    register_symptom(m, "headache", present=True)
    summary = generate_doctor_summary(m)
    neg = summary["IMPORTANT_NEGATIVE_FINDINGS"]
    assert any("vomiting" in str(n).lower() for n in neg)


def test_summary_main_problem():
    from services.ai.doctor_summary import generate_doctor_summary
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True, duration="2 days")
    register_symptom(m, "headache", present=True)
    summary = generate_doctor_summary(m)
    assert summary["MAIN_CLINICAL_PROBLEM"] != ""
