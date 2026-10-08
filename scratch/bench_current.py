import time
from services.ai.clinical_memory import empty_memory
from services.ai.fact_extractor import extract_facts
from services.ai.interview_engine import analyze_turn, _candidate_questions

print("Benchmarking current turn pipeline...")
answers = {"chief_complaint": "I have fever"}
memory = empty_memory()

# 1. extract_facts
t_ext_start = time.perf_counter()
ext = extract_facts(patient_text="I have fever", language="English")
t_ext = time.perf_counter() - t_ext_start
print(f"extract_facts latency: {t_ext:.2f}s, source: {ext.get('_ai_source')}")

# 2. analyze_turn
cand = _candidate_questions("NORMAL", answers, "English")
t_turn_start = time.perf_counter()
turn = analyze_turn("NORMAL", "English", answers, cand, clinical_memory=memory)
t_turn = time.perf_counter() - t_turn_start
print(f"analyze_turn latency: {t_turn:.2f}s, source: {turn.get('ai_source')}")
print(f"Selected question: {turn.get('next_question', {}).get('question')}")
print(f"Total time for 1 turn: {t_ext + t_turn:.2f}s")
