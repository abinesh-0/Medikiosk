# services/ai/question_selector.py

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from services.ai.llm_service import generate_json
from services.ai.clinical_memory import is_covered, norm, has_fact


# ============================================================
# NORMALIZATION
# ============================================================

def norm(value: Any) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(value or "").strip().lower(),
    )


# ============================================================
# UNIQUE QUESTIONS
# ============================================================

def unique_questions(
    candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    result = []
    seen = set()

    for q in candidates or []:

        if not isinstance(q, dict):
            continue

        key = str(
            q.get("key") or ""
        ).strip()

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)

        result.append(q)

    return result


# ============================================================
# REMOVE ANSWERED QUESTIONS
# ============================================================

def filter_covered_questions(
    memory: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    debug: bool = False,
    debug_log: List[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:

    result = []

    for q in unique_questions(
        candidates
    ):

        key = str(
            q.get("key") or ""
        ).strip()

        question = str(
            q.get("question")
            or q.get("en")
            or ""
        ).strip()

        covered = is_covered(memory, key, question)

        if debug and debug_log is not None:
            debug_log.append({
                "check": "filter_covered",
                "key": key,
                "question": question[:100],
                "covered": covered,
            })

        if covered:
            continue

        result.append(q)

    return result


# ============================================================
# CLINICAL RELEVANCE FILTER
# ============================================================

def _active_symptoms(
    memory: Dict[str, Any],
) -> List[str]:

    symptoms = memory.get(
        "symptoms",
        {}
    )

    result = []

    if isinstance(symptoms, dict):

        for name, item in symptoms.items():

            if not isinstance(item, dict):
                continue

            if item.get("present") is False:
                continue

            result.append(
                str(name)
            )

    return result


def relevance_score(
    question: Dict[str, Any],
    memory: Dict[str, Any],
) -> int:

    key = norm(
        question.get("key")
    )

    branch = norm(
        question.get("branch")
    )

    text = norm(
        question.get("question")
        or question.get("en")
        or ""
    )

    symptoms = _active_symptoms(
        memory
    )

    score = 0

    # Safety-related questions
    safety_words = [
        "breathing",
        "faint",
        "weakness",
        "numbness",
        "vision",
        "blood",
        "severe",
        "chest",
        "speech",
        "மூச்சு",
        "மயக்கம்",
        "ரத்தம்",
    ]

    if any(
        word in key
        or word in text
        for word in safety_words
    ):
        score += 50

    # Match active symptom branch
    for symptom in symptoms:

        s = norm(symptom)

        if s in branch:
            score += 30

        if (
            "headache" in s
            and (
                "head" in key
                or "head" in text
            )
        ):
            score += 30

        if (
            "abdominal" in s
            and (
                "abd" in key
                or "abdominal" in text
                or "stomach" in text
            )
        ):
            score += 30

        if (
            "fever" in s
            and "fever" in key
        ):
            score += 30

        if (
            "chest" in s
            and "chest" in key
        ):
            score += 40

        if (
            "breathing" in s
            and (
                "resp" in branch
                or "breathing" in text
            )
        ):
            score += 40

    # Core history gets lower priority than active symptom details.
    if branch in {
        "core_history",
        "general",
    }:
        score += 5

    return score


# ============================================================
# RANK CANDIDATES
# ============================================================

def rank_candidates(
    memory: Dict[str, Any],
    candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    items = []

    for index, q in enumerate(
        filter_covered_questions(
            memory,
            candidates,
        )
    ):

        score = relevance_score(
            q,
            memory,
        )

        q2 = dict(q)

        q2["_local_score"] = score
        q2["_candidate_index"] = index

        items.append(q2)

    items.sort(
        key=lambda x: (
            -int(
                x.get(
                    "_local_score",
                    0,
                )
            ),
            int(
                x.get(
                    "_candidate_index",
                    0,
                )
            ),
        )
    )

    return items


# ============================================================
# LLM NEXT QUESTION
# ============================================================

def select_next_question(
    *,
    memory: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    language: str,
    debug: bool = False,
) -> Dict[str, Any]:

    debug_log: List[Dict[str, Any]] = []

    if debug:
        debug_log.append({
            "check": "start",
            "memory_keys": list(memory.get("facts", {}).keys()),
            "symptoms": list(memory.get("symptoms", {}).keys()),
            "candidates": [q.get("key", "") for q in candidates],
        })

    ranked = rank_candidates(
        memory,
        candidates,
    )

    if not ranked:

        return {
            "next_question": None,
            "done": True,
            "reason": "no_unanswered_relevant_question",
            "ai_source": "LOCAL_RULES",
            "debug_log": debug_log if debug else None,
        }

    # Keep the candidate pool small and relevant (max 6 candidates)
    pool = ranked[:6]

    symptoms = _active_symptoms(memory)
    sym_str = ", ".join(symptoms) if symptoms else "none"
    known_facts = list(memory.get("facts", {}).keys())
    known_str = ", ".join(known_facts) if known_facts else "none"

    cand_lines = []
    for c in pool:
        q_text = c.get("question") or (c.get("ta") if language == "Tamil" else c.get("en")) or c.get("key")
        cand_lines.append(f"- {c['key']}: {q_text}")
    cand_str = "\n".join(cand_lines)

    prompt = f"""Clinical intake assistant for MediKiosk.
Select ONE relevant follow-up question key from the candidates.
Rules:
1. Ask exactly ONE concise question from the candidates.
2. Do NOT diagnose, prescribe, or provide medical advice.
3. Do NOT explain or summarize the case.
4. Do NOT re-ask known information.
5. If enough clinical information is gathered for doctor review, set "is_complete": true and "key": null.

Active symptoms: {sym_str}
Already known facts: {known_str}

Candidate questions:
{cand_str}

Return ONLY JSON:
{{"key": "<selected_key>", "is_complete": false}}"""

    fallback = {
        "next_question": pool[0],
        "done": False,
    }

    try:
        raw, source = generate_json(
            prompt,
            json.dumps({"key": pool[0]["key"], "is_complete": False}, ensure_ascii=False),
            max_tokens=45,
        )

        if isinstance(raw, dict):
            data = raw
        else:
            try:
                data = json.loads(
                    str(raw or "")
                )
            except Exception:
                data = {}

        if not isinstance(
            data,
            dict,
        ):
            data = {}

        next_q = data.get("next_question")

        if data.get("is_complete") or (("key" in data) and data.get("key") in (None, "null", "")):
            next_q = None
        elif not next_q and data.get("key"):
            sel_k = str(data.get("key", "")).strip()
            matched = next((c for c in pool if c.get("key") == sel_k), None)
            if matched:
                next_q = {
                    "key": matched["key"],
                    "question": matched.get("question") or (matched.get("ta") if language == "Tamil" else matched.get("en")) or matched["key"],
                    "options": matched.get("options", []),
                    "adaptive": True,
                    "branch": matched.get("branch", ""),
                    "reason": "adaptive_selection",
                }

            key = str(
                next_q.get("key")
                or ""
            ).strip()

            question = str(
                next_q.get("question")
                or ""
            ).strip()

            # Must be a real candidate.
            allowed_keys = {
                str(
                    q.get("key")
                    or ""
                )
                for q in pool
            }

            if key not in allowed_keys:
                next_q = None

            elif is_covered(
                memory,
                key,
                question,
            ):
                next_q = None

            else:

                next_q = {
                    "key": key,
                    "question": question,
                    "options": (
                        next_q.get(
                            "options"
                        )
                        if isinstance(
                            next_q.get(
                                "options"
                            ),
                            list,
                        )
                        else []
                    ),
                    "adaptive": True,
                    "branch": str(
                        next_q.get(
                            "branch"
                        )
                        or ""
                    ),
                    "reason": str(
                        next_q.get(
                            "reason"
                        )
                        or "missing_high_value_information"
                    ),
                }

                if not question:
                    next_q = None

        # ----------------------------------------------------
        # SECOND GUARD
        # ----------------------------------------------------

        if next_q is None and not data.get("is_complete"):

            # Find first candidate that is definitely
            # not covered.
            for candidate in pool:

                key = str(
                    candidate.get("key")
                    or ""
                )

                question = str(
                    candidate.get("question")
                    or candidate.get("en")
                    or ""
                )

                if not is_covered(
                    memory,
                    key,
                    question,
                ):

                    next_q = {
                        "key": key,
                        "question": (
                            candidate.get(
                                "question"
                            )
                            or candidate.get(
                                "en"
                            )
                            or candidate.get(
                                "ta"
                            )
                            or ""
                        ),
                        "options": candidate.get(
                            "options",
                            []
                        ),
                        "adaptive": True,
                        "branch": candidate.get(
                            "branch",
                            "",
                        ),
                        "reason": "local_safe_fallback",
                    }

                    break

        return {
            "next_question": next_q,
            "covered_information": data.get(
                "covered_information",
                [],
            ),
            "missing_important_information": data.get(
                "missing_important_information",
                [],
            ),
            "done": next_q is None,
            "ai_source": source,
            "debug_log": debug_log if debug else None,
        }

    except Exception:

        return {
            "next_question": {
                "key": pool[0].get(
                    "key"
                ),
                "question": (
                    pool[0].get(
                        "question"
                    )
                    or pool[0].get(
                        "en"
                    )
                    or pool[0].get(
                        "ta"
                    )
                    or ""
                ),
                "options": pool[0].get(
                    "options",
                    [],
                ),
                "adaptive": True,
                "branch": pool[0].get(
                    "branch",
                    "",
                ),
                "reason": "local_fallback",
            },
            "done": False,
            "ai_source": "LOCAL_RULES",
        }