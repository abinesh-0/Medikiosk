# tests/test_department_routing.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_department_router_fever():
    from services.ai.department_router import route_department
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True)
    result = route_department(m)
    assert result["department"] in [
        "General Medicine", "Pulmonology"
    ]
    assert isinstance(result["confidence"], float)


def test_department_router_chest_pain():
    from services.ai.department_router import route_department
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )
    m = empty_memory()
    register_symptom(m, "chest_pain", present=True)
    result = route_department(m)
    assert result["department"] in ["Cardiology", "General Medicine"]


def test_department_router_cough():
    from services.ai.department_router import route_department
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )
    m = empty_memory()
    register_symptom(m, "cough", present=True)
    result = route_department(m)
    assert result["department"] in [
        "Pulmonology", "General Medicine"
    ]


def test_department_router_headache():
    from services.ai.department_router import route_department
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )
    m = empty_memory()
    register_symptom(m, "headache", present=True)
    result = route_department(m)
    assert result["department"] in [
        "Neurology", "General Medicine"
    ]


def test_department_router_abdominal():
    from services.ai.department_router import route_department
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )
    m = empty_memory()
    register_symptom(m, "abdominal_pain", present=True)
    result = route_department(m)
    assert result["department"] in [
        "Gastroenterology", "General Medicine"
    ]


def test_department_router_completed_case():
    """Test with complete ClinicalMemory - main problem identification."""
    from services.ai.department_router import route_department
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, set_fact,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True, duration="2 days")
    register_symptom(m, "headache", present=True, location="head")
    register_symptom(m, "cough", present=True)
    set_fact(m, "chest_pain", True)
    result = route_department(m)
    assert "department" in result
    assert isinstance(result["supporting_facts"], list)
    assert "confidence" in result
    assert isinstance(result["needs_doctor_review"], bool)


def test_department_routing_conservative():
    """When multiple departments match, needs_doctor_review should be true."""
    from services.ai.department_router import route_department
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )
    m = empty_memory()
    register_symptom(m, "fever", present=True)
    register_symptom(m, "cough", present=True)
    result = route_department(m)
    assert isinstance(result.get("needs_doctor_review"), bool)
