import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.ai.llm_service import _call_ollama

prompt = """You are MediKiosk's clinical intake documentation assistant.
Generate a concise, structured clinician-facing intake summary for the consulting doctor based ONLY on the patient's intake facts.

Rules:
1. Do NOT diagnose or prescribe medications.
2. Ground strictly on patient-stated facts.
3. Keep it concise, structured, and fast to read.

Patient Complaint: I have stomach pain
Intake History:
- abd_duration: 2 days
- abd_location: lower right side
- abd_character: sharp cramps
- abd_vomit_stool: no vomiting, normal bowel movements

Return a structured summary with:
• Chief Complaint:
• Duration / Timeline:
• Location & Character:
• Associated Symptoms & Pertinent Negatives:
• Safety Screening:
• Clinician Handoff Note:"""

print("Testing concise clinician summary generation with Gemma 4...")
res, src = _call_ollama(prompt, max_tokens=220, temperature=0.1)
print(f"Summary from {src}:\n{res}")
