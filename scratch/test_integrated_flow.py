import time, json
from services.ai.clinical_memory import empty_memory, record_turn, set_fact, mark_answered
from services.ai.interview_engine import _candidate_questions, _local_facts, _validate_question
from services.ai.question_selector import rank_candidates, filter_covered_questions
from services.ai.llm_service import generate_json

def test_turn(chief_complaint, previous_answers, language="English"):
    answers = {"chief_complaint": chief_complaint}
    answers.update(previous_answers)
    
    memory = empty_memory()
    for k, v in answers.items():
        record_turn(memory, v)
        set_fact(memory, k, v)
        mark_answered(memory, k, v)
    
    # 1. Get candidates
    candidates = _candidate_questions("NORMAL", answers, language)
    
    # 2. Filter covered
    filtered = filter_covered_questions(memory, candidates)
    
    # 3. Rank
    ranked = rank_candidates(memory, filtered)
    
    pool = ranked[:6]
    if not pool:
        print("No candidates remain. Interview is COMPLETE.")
        return None
    
    # 4. Prompt
    history_items = [f"{k}: {v}" for k, v in answers.items() if v and k != "chief_complaint"]
    history_str = "; ".join(history_items[-3:]) if history_items else "None yet"
    cand_lines = [f"- {c['key']}: {c.get('question') or c.get('en')}" for c in pool]
    cand_str = "\n".join(cand_lines)
    
    prompt = f"""Clinical intake assistant for MediKiosk.
Ask ONE follow-up question to gather missing history for the doctor.
Rules:
1. Ask exactly ONE concise question from the candidates.
2. Do NOT diagnose, prescribe, or provide medical advice.
3. Do NOT explain or summarize the case.
4. Do NOT re-ask known information.
5. If enough clinical information is gathered for doctor review, set "is_complete": true and "key": null.

Patient complaint: {chief_complaint}
Previous answers: {history_str}

Candidate questions:
{cand_str}

Return ONLY JSON:
{{"key": "<selected_candidate_key>", "is_complete": false}}"""

    fallback = {"key": pool[0]["key"], "is_complete": False}
    t0 = time.perf_counter()
    raw, source = generate_json(prompt, json.dumps(fallback), max_tokens=40)
    dur = time.perf_counter() - t0
    
    try:
        data = json.loads(raw)
    except:
        data = fallback
        
    selected_key = data.get("key")
    selected_q = next((c for c in pool if c["key"] == selected_key), pool[0])
    print(f"Turn took {dur:.2f}s ({source})")
    print(f"Selected: {selected_q['key']} -> {selected_q.get('question') or selected_q.get('en')}")
    return selected_q

print("--- Test 1: Fever ---")
q1 = test_turn("I have fever", {})
print("\n--- Test 2: Fever with 2 days duration ---")
q2 = test_turn("I have fever", {"fever_duration": "2 days"})
print("\n--- Test 3: Stomach pain ---")
q3 = test_turn("I have stomach pain", {})
print("\n--- Test 4: Headache for 2 days ---")
q4 = test_turn("I have headache for 2 days", {})
