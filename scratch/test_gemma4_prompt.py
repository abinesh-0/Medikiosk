import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.ai.llm_service import _call_ollama
import json

def test_turn(patient_complaint, answers, candidates):
    cand_lines = "\n".join([f"- {c['key']}: {c['question']}" for c in candidates])
    ans_lines = "\n".join([f"- {k}: {v}" for k, v in answers.items()]) if answers else "None"
    
    prompt = f"""You are MediKiosk's clinical intake assistant.
Analyze the patient's latest input and previous answers.
Identify the most important missing clinical information (duration, location, severity, associated symptoms).

Rules:
1. Do NOT diagnose or prescribe.
2. Do NOT provide long medical explanations. Keep responses concise and fast.
3. If essential intake info is still missing, set status to "continue" and choose ONE best candidate question key.
4. If essential intake information is collected, set status to "complete" and key to null.

Patient complaint: {patient_complaint}
Collected answers:
{ans_lines}

Candidate questions:
{cand_lines}

Respond with valid JSON only:
{{"status": "continue"|"complete", "missing_info": "<brief description of missing info or null>", "key": "<chosen_candidate_key_or_null>", "is_complete": false|true}}"""

    print("Prompting Gemma 4...")
    res, src = _call_ollama(prompt, max_tokens=100, format_json=True)
    print(f"Result from {src}: {res}")
    try:
        parsed = json.loads(res)
        print("Parsed JSON:", parsed)
    except Exception as e:
        print("JSON parse error:", e)

# Scenario 1: Initial complaint "I have stomach pain"
print("\n--- TURN 1 ---")
test_turn(
    "I have stomach pain",
    {},
    [
        {"key": "abd_location", "question": "Where exactly is the pain located?"},
        {"key": "abd_duration", "question": "How many days have you had this stomach pain?"},
        {"key": "abd_vomit_stool", "question": "Are you having vomiting or loose motions?"},
    ]
)

# Scenario 2: Patient answered location and duration, missing associated symptoms
print("\n--- TURN 2 ---")
test_turn(
    "I have stomach pain",
    {
        "abd_location": "lower right side",
        "abd_duration": "2 days"
    },
    [
        {"key": "abd_vomit_stool", "question": "Are you having vomiting or loose motions?"},
        {"key": "abd_character", "question": "Is the pain sharp, cramping, or burning?"},
        {"key": "abd_fever", "question": "Do you also have a fever?"}
    ]
)

# Scenario 3: Patient answered all essential info
print("\n--- TURN 3 (All essential info answered) ---")
test_turn(
    "I have stomach pain",
    {
        "abd_location": "lower right side",
        "abd_duration": "2 days",
        "abd_vomit_stool": "no vomiting, normal stools",
        "abd_character": "sharp cramp, moderate severity",
        "abd_fever": "no fever"
    },
    [
        {"key": "abd_aggravate", "question": "Does food worsen the pain?"},
        {"key": "abd_urinary", "question": "Any burning during urination?"}
    ]
)
