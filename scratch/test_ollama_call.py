import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.ai.llm_service import _call_ollama

prompt = """You are MediKiosk's clinical intake assistant.
Select ONE relevant follow-up question key from the candidate list to collect missing clinical history for the doctor.
Rules:
1. Ask exactly ONE concise question from the candidates.
2. Do NOT diagnose, prescribe, or provide medical advice.
3. Do NOT explain or summarize the case.
4. Do NOT re-ask information that is already known.
5. If enough clinical information is gathered for doctor review, set "is_complete": true and "key": null.

Patient complaint: I have stomach pain
Previous answers: None yet

Candidate questions:
- abd_location: Where exactly is the pain located?
- abd_duration: How many days has this pain lasted?
- abd_vomit_stool: Are you having vomiting or loose motions?

Return ONLY valid JSON:
{"key": "<selected_candidate_key>", "is_complete": false}"""

print("Testing with max_tokens=45...")
res = _call_ollama(prompt, max_tokens=45, format_json=True)
print("res with 45 tokens:", repr(res))

print("Testing with max_tokens=150...")
res2 = _call_ollama(prompt, max_tokens=150, format_json=True)
print("res with 150 tokens:", repr(res2))
