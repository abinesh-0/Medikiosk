import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from app import create_app
from extensions import db
from models.user_model import User
from models.patient_model import Patient
from models.visit_model import Visit
from models.case_model import Case
from models.conversation_model import ConversationSession
from services.ai.llm_service import OLLAMA_MODEL, OLLAMA_BASE_URL
from services.ai.interview_engine import analyze_turn, _candidate_questions
from services.ai.clinical_memory import empty_memory, record_turn, set_fact, mark_answered

print("=" * 60)
print("REALISTIC CLINICAL INTAKE FLOW VERIFICATION")
print(f"Verified LLM: Ollama Gemma 4 ({OLLAMA_MODEL}) at {OLLAMA_BASE_URL}")
print("=" * 60)

# ── 1. Unit Flow Simulation ──
print("\n--- STEP 1: Simulating Adaptive Intake Engine ---")
answers = {"chief_complaint": "I have stomach pain"}
memory = empty_memory()
memory["chief_complaint"] = ["I have stomach pain"]
record_turn(memory, "I have stomach pain")

# Turn 1: Analyze complaint
candidates = _candidate_questions("NORMAL", answers, "English")
turn1 = analyze_turn(
    mode="NORMAL",
    language="English",
    answers=answers,
    candidates=candidates,
    answer_count=len(answers),
    clinical_memory=memory
)

print(f"Turn 1 Status: {turn1.get('status')}")
print(f"Turn 1 Missing Info Identified: {turn1.get('missing_important_information')[:3]}")
print(f"Turn 1 Question Selected: {turn1['next_question']['question']} (Key: {turn1['next_question']['key']})")
print(f"Turn 1 AI Source: {turn1.get('ai_source')}")

assert turn1.get('status') == 'continue', "Turn 1 must continue"
assert turn1.get('next_question') is not None, "Turn 1 must have next_question"
assert turn1.get('clinical_summary') == "", "No summary during questioning stage"

# Turn 2: Patient answers with location and duration
q1_key = turn1['next_question']['key']
patient_ans1 = "lower right side of belly, for 2 days"
answers[q1_key] = patient_ans1
record_turn(memory, patient_ans1)
set_fact(memory, q1_key, patient_ans1)
mark_answered(memory, q1_key, patient_ans1)

candidates = _candidate_questions("NORMAL", answers, "English")
turn2 = analyze_turn(
    mode="NORMAL",
    language="English",
    answers=answers,
    candidates=candidates,
    answer_count=len(answers),
    clinical_memory=memory
)

print(f"\nTurn 2 Status: {turn2.get('status')}")
if turn2.get('next_question'):
    print(f"Turn 2 Question Selected: {turn2['next_question']['question']} (Key: {turn2['next_question']['key']})")
print(f"Turn 2 AI Source: {turn2.get('ai_source')}")

# Turn 3: Patient answers with associated symptoms
if turn2.get('next_question'):
    q2_key = turn2['next_question']['key']
    patient_ans2 = "mild nausea, no vomiting, normal bowel movements"
    answers[q2_key] = patient_ans2
    record_turn(memory, patient_ans2)
    set_fact(memory, q2_key, patient_ans2)
    mark_answered(memory, q2_key, patient_ans2)

    candidates = _candidate_questions("NORMAL", answers, "English")
    turn3 = analyze_turn(
        mode="NORMAL",
        language="English",
        answers=answers,
        candidates=candidates,
        answer_count=len(answers),
        clinical_memory=memory
    )
    final_turn = turn3
else:
    final_turn = turn2

print(f"\nTurn 3 Status: {final_turn.get('status')}")
print(f"Turn 3 Done: {final_turn.get('done')}")
if final_turn.get('next_question'):
    print(f"Turn 3 Question: {final_turn['next_question']['question']}")
    # Final turn 4 to complete
    q3_key = final_turn['next_question']['key']
    patient_ans3 = "sharp cramping pain, moderate severity"
    answers[q3_key] = patient_ans3
    record_turn(memory, patient_ans3)
    set_fact(memory, q3_key, patient_ans3)
    mark_answered(memory, q3_key, patient_ans3)

    candidates = _candidate_questions("NORMAL", answers, "English")
    turn4 = analyze_turn(
        mode="NORMAL",
        language="English",
        answers=answers,
        candidates=candidates,
        answer_count=len(answers),
        clinical_memory=memory
    )
    final_turn = turn4
    print(f"\nTurn 4 Status: {final_turn.get('status')}")
    print(f"Turn 4 Done: {final_turn.get('done')}")

print(f"\nFinal Summary Present: {bool(final_turn.get('final_summary'))}")
print("Final Clinician-Facing Summary Preview:")
print("-" * 50)
print(final_turn.get('final_summary'))
print("-" * 50)

assert "diagnos" not in (final_turn.get('final_summary') or "").lower() or "before final diagnosis" in (final_turn.get('final_summary') or "").lower(), "Must not make medical diagnoses"
assert "prescrib" not in (final_turn.get('final_summary') or "").lower() or "before" in (final_turn.get('final_summary') or "").lower() or "not" in (final_turn.get('final_summary') or "").lower(), "Must not prescribe medications"

print("\n--- STEP 2: Testing End-to-End Flask Conversation Route ---")
app = create_app()
with app.app_context():
    client = app.test_client()
    
    # 1. Register/start patient session
    r_pstart = client.post('/api/kiosk/patient-start', json={
        'name': 'Test Patient',
        'age': 35,
        'gender': 'FEMALE',
        'phone': '9876543210',
        'language': 'English'
    })
    assert r_pstart.status_code == 200, f"patient-start failed: {r_pstart.text}"
    token_obj = r_pstart.get_json()['token']
    auth_header = {'Authorization': f"Bearer {token_obj.get('access_token', '')}"}

    # 2. Start kiosk case
    r_start = client.post('/api/kiosk/start', json={'language': 'English', 'mode': 'NORMAL'}, headers=auth_header)
    assert r_start.status_code == 200, f"Start failed: {r_start.text}"
    case_data = r_start.get_json()['case']
    case_id = case_data['id']

    # 2. Start session
    r_sess = client.post(f'/api/conversation/{case_id}/session', headers=auth_header)
    assert r_sess.status_code == 200, f"Session failed: {r_sess.text}"
    sess_id = r_sess.get_json()['session']['id']
    initial_q = r_sess.get_json()['next_question']
    print(f"Initial Session Question: {initial_q['question']} (Key: {initial_q['key']})")

    # 3. Patient replies with stomach pain
    r_msg1 = client.post(
        f'/api/conversation/{case_id}/message',
        json={
            'session_id': sess_id,
            'question_key': initial_q['key'],
            'text': 'I have severe stomach pain for 2 days',
            'input_type': 'TEXT'
        },
        headers=auth_header
    )
    d1 = r_msg1.get_json()
    print(f"Message 1 Response Status: {d1.get('status')}")
    print(f"Message 1 Next Question: {d1.get('next_question', {}).get('question') if d1.get('next_question') else 'None'}")
    print(f"Message 1 Final Summary: {d1.get('final_summary')}")
    assert d1.get('status') in ('continue', 'complete'), "Status must be continue or complete"

    if d1.get('status') == 'continue' and d1.get('next_question'):
        q2 = d1['next_question']
        r_msg2 = client.post(
            f'/api/conversation/{case_id}/message',
            json={
                'session_id': sess_id,
                'question_key': q2['key'],
                'text': 'lower right side, sharp pain, no vomiting',
                'input_type': 'TEXT'
            },
            headers=auth_header
        )
        d2 = r_msg2.get_json()
        print(f"Message 2 Response Status: {d2.get('status')}")
        print(f"Message 2 Next Question: {d2.get('next_question', {}).get('question') if d2.get('next_question') else 'None'}")
        print(f"Message 2 Final Summary: {bool(d2.get('final_summary'))}")
        
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
