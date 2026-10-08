"""
Regression tests for the adaptive interview engine.

These tests are intentionally deterministic (no OpenRouter call, no database)
so they verify the anti-repetition guarantees that must hold even when the
LLM is temporarily unavailable.
"""

from services.ai.interview_engine import _candidate_questions, _fallback, _local_facts
from services.triage.red_flag_engine import normalize_llm_safety_flags


def test_local_facts_tamil_duration():
    assert _local_facts("இரண்டு நாட்கள் fever").get("duration_known") is True
    assert _local_facts("rendu naala fever iruku").get("duration_known") is True
    assert _local_facts("fever iruku").get("duration_known") is None


def test_local_facts_onset_words():
    assert _local_facts("nethu evening start achu").get("onset_known") is True
    assert _local_facts("நேற்று தொடங்கியது").get("onset_known") is True


def test_no_repeat_questions_in_local_fallback():
    mode = "NORMAL"
    lang = "Tamil"
    answers = {
        "chief_complaint": "மார்புவலி, மூச்சுவிடசிரமம், இரண்டு நாட்களாக"
    }

    seen = []
    for _ in range(8):
        cand = _candidate_questions(mode, answers, lang)
        fb = _fallback(mode, lang, answers, cand)
        nq = fb.get("next_question")
        if not nq:
            break
        assert nq["key"] not in seen, f"repeated question: {nq['key']}"
        seen.append(nq["key"])
        # In the real kiosk the patient answers the question that was asked.
        answers[nq["key"]] = "சிறிது முக்க்வலிகள்"

    # Onset / duration / generic location must never be asked when the
    # patient already gave duration + a body-region-specific symptom.
    blocked_prefixes = ("chest_onset", "head_onset", "abd_onset",
                        "pain_onset", "fever_duration", "resp_duration",
                        "head_duration", "abd_duration", "pain_location")
    for k in seen:
        assert not k.endswith("_onset"), k
        assert not k.endswith("_duration"), k
        assert k != "pain_location", k
        assert not k.startswith(blocked_prefixes), k


def test_local_fallback_picks_related_branch_after_new_symptom():
    mode = "NORMAL"
    lang = "English"
    # First the patient only mentions fever.
    answers = {"chief_complaint": "fever for 3 days"}
    cand = _candidate_questions(mode, answers, lang)
    fb = _fallback(mode, lang, answers, cand)
    first = fb["next_question"]["key"]
    # Patient answers and mentions a new symptom (cough) inline.
    answers[first] = "3 days, also cough and breathing trouble"
    cand2 = _candidate_questions(mode, answers, lang)
    fb2 = _fallback(mode, lang, answers, cand2)
    second = fb2["next_question"]["key"]
    # The next question must not repeat the first one.
    assert second != first
    # And duration must not be re-asked.
    assert second != "fever_duration"


def test_normalize_llm_safety_flags_handles_strings_and_dicts():
    flags = ["sputum_blood", "breathing_difficulty", {"flag_code": "chest_pain"}]
    norm = normalize_llm_safety_flags(flags)
    codes = [f["flag_code"] for f in norm]
    assert "SEVERE_BLEEDING" in codes
    assert "CHEST_BREATHING" in codes
    for f in norm:
        assert isinstance(f, dict)
        assert f["detected_by"] == "AI"
        assert f["severity"] in ("HIGH", "URGENT")
        # chest/breathing should be URGENT, not the default HIGH
    chest = next(f for f in norm if f["flag_code"] == "CHEST_BREATHING")
    assert chest["severity"] == "URGENT"


def test_normalize_llm_safety_flags_dedupes_and_drops_invalid():
    flags = ["chest_pain", "dyspnea", "not a real flag", None, 123]
    norm = normalize_llm_safety_flags(flags)
    codes = [f["flag_code"] for f in norm]
    # Both chest_pain and dyspnea map to CHEST_BREATHING -> deduped to one.
    assert codes.count("CHEST_BREATHING") == 1
    # An unmapped flag still becomes a valid HIGH alert (never crashes).
    assert any(f["severity"] == "HIGH" for f in norm)
