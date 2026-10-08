"""
Regression tests for the two reported bugs:

Bug 1 — /api/conversation/<id>/message returned 500 when the interview
        completed because conversation_routes imported a non-existent
        module ``models.ai_summary_model`` (real module: models.summary_model).

Bug 2 — Question text honoured the session language but the touch options
        stayed Tamil for English sessions, and the final-summary prompts
        ignored the session language entirely.

These tests are deterministic: no Ollama call, no database.
"""

import inspect
import re

import routes.conversation_routes as conversation_routes
from services.ai.interview_engine import _build_prompt, _candidate_questions
from services.ai.question_engine import (
    AYUSH_BRANCHES,
    BRANCHES,
    OPTION_EN,
    get_relevant_candidates,
    localize_options,
)


TAMIL_SCRIPT = re.compile(r"[஀-௿]")


def _all_branch_options():
    return {
        opt
        for source in (BRANCHES, AYUSH_BRANCHES)
        for _, _, questions in source
        for q in questions
        for opt in q.get("options", [])
    }


def test_every_branch_option_has_english_translation():
    missing = _all_branch_options() - set(OPTION_EN)
    assert not missing, f"Options missing from OPTION_EN: {sorted(missing)}"


def test_localize_options_english_session():
    out = localize_options(["ஆம்", "இல்லை", "தெரியவில்லை"], "English")
    assert out == ["Yes", "No", "Don't know"]


def test_localize_options_tamil_session_keeps_tamil():
    src = ["ஆம்", "இல்லை"]
    out = localize_options(src, "Tamil")
    assert out == src
    assert out is not src  # never aliases the shared branch data


def test_localize_options_unknown_passthrough_and_empty():
    assert localize_options(["Mystery option"], "English") == ["Mystery option"]
    assert localize_options([], "English") == []
    assert localize_options(None, "English") == []


def test_english_candidates_emit_english_options():
    answers = {"chief_complaint": "fever for 3 days"}

    for cand in get_relevant_candidates("NORMAL", answers, "English"):
        for opt in cand["options"]:
            assert not TAMIL_SCRIPT.search(opt), (
                f"English session got Tamil option {opt!r} "
                f"on question {cand['key']}"
            )

    for cand in _candidate_questions("NORMAL", answers, "English"):
        for opt in cand["options"]:
            assert not TAMIL_SCRIPT.search(opt), (
                f"English session got Tamil option {opt!r} "
                f"on question {cand['key']}"
            )


def test_tamil_candidates_emit_tamil_options():
    answers = {"chief_complaint": "காய்ச்சல் 3 நாட்கள்"}

    with_opts = [
        c for c in _candidate_questions("NORMAL", answers, "Tamil") if c["options"]
    ]
    assert with_opts, "expected at least one candidate with touch options"
    for cand in with_opts:
        for opt in cand["options"]:
            assert TAMIL_SCRIPT.search(opt), (
                f"Tamil session lost Tamil option on {cand['key']}: {opt!r}"
            )


def test_build_prompt_states_session_language_explicitly():
    answers = {"chief_complaint": "fever"}
    candidates = [
        {"key": "fever_duration", "question": "How long?", "options": []}
    ]

    en = _build_prompt("NORMAL", "English", answers, candidates, {})
    assert "session language is English" in en

    ta = _build_prompt("NORMAL", "Tamil", answers, candidates, {})
    assert "session language is Tamil" in ta


def test_summary_prompt_and_fallback_follow_session_language(monkeypatch):
    from services.ai import llm_service
    from services.ai.interview_engine import generate_concise_clinical_summary

    captured = {}

    def fake_generate_text(prompt, **kwargs):
        captured["prompt"] = prompt
        return "[LOCAL_FALLBACK]", "TEST"

    monkeypatch.setattr(llm_service, "generate_text", fake_generate_text)

    ta = generate_concise_clinical_summary(
        "காய்ச்சல்", {"fever_duration": "3 நாட்கள்"}, language="Tamil"
    )
    assert "session language is Tamil" in captured["prompt"]
    assert TAMIL_SCRIPT.search(ta), "Tamil session must get a Tamil fallback summary"

    en = generate_concise_clinical_summary(
        "fever", {"fever_duration": "3 days"}, language="English"
    )
    assert "session language is English" in captured["prompt"]
    assert not TAMIL_SCRIPT.search(en), "English session must get an English summary"


def test_complete_summary_prompt_follows_session_language(monkeypatch):
    from types import SimpleNamespace

    from services.ai import summary_generator
    from services.ai.summary_generator import generate

    captured = {}

    def fake_generate_json(prompt, fallback, **kwargs):
        captured["prompt"] = prompt
        return "not-json", "TEST"  # force deterministic fallback path

    # summary_generator binds the name at import time, so patch it there.
    monkeypatch.setattr(summary_generator, "generate_json", fake_generate_json)

    case = SimpleNamespace(case_number="C-1", chief_complaint="fever",
                           patient=None, visit=None)
    generate(case, {}, {}, [], [], [], None, "Tamil")
    assert "Session language is Tamil" in captured["prompt"]

    generate(case, {}, {}, [], [], [], None, "English")
    assert "Session language is English" in captured["prompt"]

    # fallback text must be produced without errors in both languages
    text, structured = generate(case, {}, {}, [], [], [], None, "Tamil")
    assert isinstance(text, str) and text
    assert isinstance(structured, dict)
    assert structured.get("language") == "Tamil"


def test_completion_persist_import_path_is_correct():
    """Guard against reintroducing the Bug 1 import typo."""
    src = inspect.getsource(conversation_routes)
    assert "ai_summary_model" not in src
    assert "from models.summary_model import AISummary" in src

    # And the real module must expose AISummary.
    from models.summary_model import AISummary  # noqa: F401
