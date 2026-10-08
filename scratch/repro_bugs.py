"""Reproduce Bug 1 (500 after adaptive intake turns) and inspect Bug 2 language behaviour.

Runs the real HTTP handler pipeline through the Flask test client with
TESTING=True so exceptions propagate with a full traceback.
"""
import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ALLOW_DEV_OTP"] = "true"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402

app = create_app()
app.config["TESTING"] = True

client = app.test_client()

import json  # noqa: E402

RESULTS = {}


def has_tamil(s):
    return any('\u0b80' <= ch <= '\u0bff' for ch in str(s or ''))


def show(label, resp):
    body = resp.get_data(as_text=True)
    try:
        body = json.dumps(resp.get_json(), ensure_ascii=False, indent=1)
    except Exception:
        pass
    print(f"[{label}] status={resp.status_code}")
    print(body[:2000])
    print("-" * 60)
    return resp.get_json() if resp.is_json else None


def run_flow(language, answers_script):
    print("=" * 70)
    print(f"FLOW: {language}")
    print("=" * 70)

    r = client.post(
        "/api/kiosk/patient-start",
        json={
            "name": "Repro Patient",
            "age": 40,
            "gender": "FEMALE",
            "language": language,
        },
    )
    data = show("patient-start", r)
    tok = data["token"]
    token = tok["access_token"] if isinstance(tok, dict) else tok

    h = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

    r = client.post(
        "/api/kiosk/start",
        json={"mode": "NORMAL", "language": language},
        headers=h,
    )
    data = show("kiosk/start", r)
    case_id = data["case"]["id"]

    r = client.post(f"/api/conversation/{case_id}/session", json={}, headers=h)
    data = show("session", r)
    session_id = data["session"]["id"]
    nq = data["next_question"]
    print(f"Q0 lang check -> key={nq.get('key')} q={nq.get('question')} opts={nq.get('options')}")

    for i, (key, text) in enumerate(answers_script, start=1):
        try:
            r = client.post(
                f"/api/conversation/{case_id}/message",
                json={
                    "session_id": session_id,
                    "question_key": key,
                    "text": text,
                    "input_type": "TEXT",
                },
                headers=h,
            )
        except Exception:
            print(f"!!! EXCEPTION on message {i} (key={key}):")
            traceback.print_exc()
            return
        data = show(f"message {i}", r)
        if not data or not data.get("success"):
            return
        nq = data.get("next_question")
        print(f"status={data.get('status')} ai_source={data.get('ai_source')}")
        if nq:
            print(f"Q{i} -> key={nq.get('key')} q={nq.get('question')} opts={nq.get('options')}")
        else:
            print(f"interview done. summary={(data.get('final_summary') or '')[:120]}")
            break

        # If the backend did not tell us the next key, stop.
        if nq:
            # rotate the scripted answer text for the next turn
            pass


# ─── Flow A: English ───
eng_turns = [
    ("chief_complaint", "I have fever and stomach pain for 3 days"),
]
# remaining keys are filled from the backend's next_question in run_flow loop
# via dynamic lookup below.


def run_dynamic(language, canned_answers):
    """canned_answers: list of texts used for successive turns."""
    print("=" * 70)
    print(f"FLOW: {language}")
    print("=" * 70)

    v = {
        "exception": False, "http_500": False, "complete": False,
        "options_seen": [], "summary": "",
    }
    RESULTS[language] = v

    r = client.post(
        "/api/kiosk/patient-start",
        json={"name": "Repro Patient", "age": 40, "gender": "FEMALE", "language": language},
    )
    data = show("patient-start", r)
    tok = data["token"]
    token = tok["access_token"] if isinstance(tok, dict) else tok
    h = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

    r = client.post("/api/kiosk/start", json={"mode": "NORMAL", "language": language}, headers=h)
    data = show("kiosk/start", r)
    case_id = data["case"]["id"]

    r = client.post(f"/api/conversation/{case_id}/session", json={}, headers=h)
    data = show("session", r)
    session_id = data["session"]["id"]
    nq = data["next_question"]
    print(f"Q0 -> key={nq.get('key')} | {nq.get('question')} | opts={nq.get('options')}")

    for i in range(1, 9):
        if not nq:
            break
        text = canned_answers[(i - 1) % len(canned_answers)]
        key = nq["key"]
        try:
            r = client.post(
                f"/api/conversation/{case_id}/message",
                json={
                    "session_id": session_id,
                    "question_key": key,
                    "text": text,
                    "input_type": "TEXT",
                },
                headers=h,
            )
        except Exception:
            print(f"!!! EXCEPTION on message {i} (key={key}):")
            traceback.print_exc()
            v["exception"] = True
            return
        if r.status_code >= 500:
            v["http_500"] = True
        data = show(f"message {i}", r)
        if not data or not data.get("success"):
            v["http_500"] = True
            return
        print(f"status={data.get('status')} ai_source={data.get('ai_source')} done={data.get('status')=='complete'}")
        nq = data.get("next_question")
        if nq:
            v["options_seen"].extend(nq.get("options") or [])
            print(f"Q{i} -> key={nq.get('key')} | {nq.get('question')} | opts={nq.get('options')}")
        else:
            v["complete"] = True
            v["summary"] = data.get("final_summary") or data.get("summary") or ""
            print(f"DONE. summary head: {(data.get('final_summary') or data.get('summary') or '')[:200]!r}")
            break


run_dynamic(
    "English",
    [
        "3 days, moderate fever with chills",
        "pain is in the upper belly, worse after food",
        "no vomiting, mild nausea",
        "no chest pain or breathing trouble",
    ],
)

run_dynamic(
    "Tamil",
    [
        "3 நாட்களாக காய்ச்சல், உடல் வலி",
        "வயிற்று வலி, சாப்பாட்டுக்கு பிறகு மோசமாகிறது",
        "வாந்தி இல்லை, சிறிது குமட்டல்",
        "மார்பு வலி இல்லை",
    ],
)

# ─── Machine-checkable verdicts (ASCII only) ───
print()
print("=" * 70)
print("VERDICTS")
print("=" * 70)

failures = []

for lang in ("English", "Tamil"):
    v = RESULTS.get(lang) or {}

    def check(name, cond, detail=""):
        line = f"[{'PASS' if cond else 'FAIL'}] {lang}: {name}{(' -- ' + detail) if detail else ''}"
        print(line)
        if not cond:
            failures.append(line)

    check("no exception (Bug 1)", not v.get("exception"))
    check("no HTTP 5xx (Bug 1)", not v.get("http_500"))
    check("interview completed", v.get("complete"))
    check("final summary produced", bool(v.get("summary")))

    opts = v.get("options_seen") or []
    if lang == "English":
        check("options in English (Bug 2)",
              bool(opts) and not any(has_tamil(o) for o in opts),
              f"n={len(opts)}")
        check("summary has no Tamil (Bug 2)", not has_tamil(v.get("summary")))
    else:
        check("options in Tamil (Bug 2)",
              bool(opts) and all(has_tamil(o) for o in opts),
              f"n={len(opts)}")
        check("summary in Tamil (Bug 2)", has_tamil(v.get("summary")))

# Only Ollama may be called (no cloud LLM fallback).
print()
print("All verifications PASSED!" if not failures else "FAILURES:\n" + "\n".join(failures))
