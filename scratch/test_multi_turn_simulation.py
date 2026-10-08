import sys
import json
import time
from services.ai.clinical_memory import empty_memory, record_turn, set_fact, mark_answered, build_context
from services.ai.fact_extractor import extract_facts
from services.ai.interview_engine import analyze_turn, _candidate_questions
from services.ai.summary_generator import generate
from services.ai.llm_service import OLLAMA_MODEL, OLLAMA_BASE_URL

def simulate_interview(scenario_name, initial_complaint, turn_answers, language="English"):
    print(f"\n=======================================================")
    print(f"SCENARIO: {scenario_name}")
    print(f"Complaint: {initial_complaint}")
    print(f"=======================================================")
    
    answers = {"chief_complaint": initial_complaint}
    memory = empty_memory()
    memory["chief_complaint"] = [initial_complaint]
    
    # Initial turn extraction
    ext = extract_facts(patient_text=initial_complaint, language=language)
    record_turn(memory, initial_complaint)
    
    turn = 1
    done = False
    last_question = None
    
    # We run up to 6 turns
    while turn <= 6 and not done:
        candidates = _candidate_questions("NORMAL", answers, language)
        res = analyze_turn(
            mode="NORMAL",
            language=language,
            answers=answers,
            candidates=candidates,
            answer_count=len(answers),
            clinical_memory=memory,
        )
        
        nq = res.get("next_question")
        done = res.get("done") or (nq is None)
        
        if done or not nq:
            print(f"[Turn {turn}] Interview marked COMPLETE! (done={done})")
            break
            
        q_text = nq.get("question")
        q_key = nq.get("key")
        print(f"[Turn {turn}] AI Question ({nq.get('branch', 'general')}): {q_text} [Key: {q_key}]")
        
        # Verify: Exactly one question, no explanation
        assert "\n" not in q_text or len(q_text.splitlines()) <= 2, f"Explanation found in question: {q_text}"
        assert not any(w in q_text.lower() for w in ["diagnosis:", "prescribe", "take paracetamol"]), "Diagnosis/prescribing found!"
        
        # Patient gives answer
        if q_key in turn_answers:
            ans_text = turn_answers[q_key]
        elif len(turn_answers) > 0 and (turn - 1) < len(list(turn_answers.values())):
            ans_text = list(turn_answers.values())[turn - 1]
        else:
            ans_text = "No other symptoms, normal."
            
        print(f"        Patient Answer: {ans_text}")
        
        # Record answer
        answers[q_key] = ans_text
        record_turn(memory, ans_text)
        set_fact(memory, q_key, ans_text)
        mark_answered(memory, q_key, ans_text)
        
        turn += 1
        last_question = nq
        
    print(f"Total turns executed: {turn - 1}")
    print(f"Answers collected: {list(answers.keys())}")
    
    # Verify doctor summary generation at completion
    print("Generating final doctor summary...")
    class MockCase:
        def __init__(self, lang, cc):
            self.id = 1
            self.case_number = "CASE-101"
            self.chief_complaint = cc
            self.language = lang
            self.patient = None
            self.visit = None

    mock_case = MockCase(language, initial_complaint)
    case_ans_rows = [{"question_key": k, "answer_text": v} for k, v in answers.items()]
    summary_text, structured = generate(
        case=mock_case,
        history={"chief_complaint": initial_complaint},
        ayush={},
        answers=case_ans_rows,
        documents=[],
        flags=[],
        assignment={"doctor_name": "Dr. Ramesh", "department": "General Medicine"},
        language=language
    )
    print("Doctor summary generated successfully! Summary preview:")
    for line in summary_text.splitlines()[:12]:
        print("  ", line)
    print("  ...")
    return True

print(f"Active LLM Backend: Ollama ({OLLAMA_MODEL}) at {OLLAMA_BASE_URL}")

# Test 1: Fever
simulate_interview(
    "Fever Assessment",
    "I have fever",
    {
        "fever_duration": "3 days",
        "fever_associated": "chills and body pain",
        "fever_pattern": "comes and goes",
        "fever_exposure": "no travel"
    }
)

# Test 2: Cough
simulate_interview(
    "Respiratory / Cough Assessment",
    "I have bad cough",
    {
        "resp_duration": "4 days",
        "resp_breathing": "no breathing difficulty",
        "resp_sputum": "dry cough without phlegm",
        "resp_wheeze": "no wheezing"
    }
)

# Test 3: Abdominal Pain
simulate_interview(
    "Abdominal Pain Assessment",
    "I have severe stomach pain",
    {
        "abd_duration": "2 days",
        "abd_location": "lower right side of belly",
        "abd_vomit_stool": "feeling nauseous, no loose motions",
        "abd_onset": "started suddenly after lunch",
        "abd_character": "sharp cramp"
    }
)

# Test 4: Headache with known duration
simulate_interview(
    "Headache for 2 days (Duration Pre-Known)",
    "I have headache for 2 days",
    {
        "head_character": "throbbing on the temples",
        "head_associated": "mild nausea, sensitive to bright light",
        "head_vision": "no vision blurriness"
    }
)
