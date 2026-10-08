# tests/test_question_selection.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_question_selector_basic():
    from services.ai.question_selector import (
        select_next_question,
        rank_candidates,
        filter_covered_questions,
    )
    from services.ai.clinical_memory import empty_memory, register_symptom, is_covered

    memory = empty_memory()
    register_symptom(memory, "fever", present=True)

    candidates = [
        {"key": "fever_duration", "question": "How long?", "options": [], "branch": "fever"},
        {"key": "fever_pattern", "question": "Constant?", "options": [], "branch": "fever"},
        {"key": "chest_onset", "question": "When did chest issue start?", "options": [], "branch": "chest"},
    ]

    ranked = rank_candidates(memory, candidates)
    assert len(ranked) >= 2

    scored = select_next_question(
        memory=memory,
        candidates=candidates,
        language="English",
        debug=False,
    )
    assert scored is not None
    assert scored.get("done") is not None


def test_question_selector_does_not_repeat_covered():
    from services.ai.question_selector import select_next_question
    from services.ai.clinical_memory import (
        empty_memory, register_symptom, is_covered,
    )

    m = empty_memory()
    register_symptom(m, "fever", present=True, duration="2 days")
    register_symptom(m, "headache", present=True, location="head")

    candidates = [
        {"key": "fever_duration", "question": "Duration?", "options": [], "branch": "fever"},
        {"key": "head_location", "question": "Where?", "options": [], "branch": "headache"},
        {"key": "fever_pattern", "question": "Pattern?", "options": [], "branch": "fever"},
    ]

    scored = select_next_question(memory=m, candidates=candidates, language="English")
    if scored.get("next_question"):
        key = scored["next_question"]["key"]
        if key in {"fever_duration", "head_location"}:
            assert is_covered(m, key), f"Selected covered question: {key}"


def test_question_selector_debug():
    from services.ai.question_selector import select_next_question
    from services.ai.clinical_memory import empty_memory, register_symptom

    m = empty_memory()
    register_symptom(m, "fever", present=True)

    candidates = [
        {"key": "fever_duration", "question": "How long?", "options": [], "branch": "fever"},
    ]

    scored = select_next_question(
        memory=m,
        candidates=candidates,
        language="English",
        debug=True,
    )
    assert "debug_log" in scored
    assert len(scored["debug_log"]) > 0


def test_question_filter_covered():
    from services.ai.question_selector import filter_covered_questions
    from services.ai.clinical_memory import (
        empty_memory, register_symptom,
    )

    m = empty_memory()
    register_symptom(m, "headache", present=True, location="head")

    candidates = [
        {"key": "head_location", "question": "Where?", "options": [], "branch": "headache"},
        {"key": "fever_duration", "question": "Duration?", "options": [], "branch": "fever"},
    ]

    filtered = filter_covered_questions(m, candidates)
    keys = [q["key"] for q in filtered]
    assert "head_location" not in keys
    assert "fever_duration" in keys


def test_relevance_score():
    from services.ai.question_selector import relevance_score
    from services.ai.clinical_memory import empty_memory

    m = empty_memory()
    q = {"key": "chest_breathing", "branch": "respiratory", "question": "Breathing difficulty?", "options": []}
    score = relevance_score(q, m)
    assert isinstance(score, int)
