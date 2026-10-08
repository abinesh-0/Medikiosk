# MediKiosk – SIH 26047

**Patient Case-Taking Software | MedTech / HealthTech**

MediKiosk is a patient-facing clinical intake prototype designed to reduce the first-mile history-taking bottleneck in high-volume OPDs.

## What the prototype demonstrates

1. Language-first patient experience (English/Tamil)
2. Elder-friendly touch/type/voice interaction
3. Normal consultation with adaptive symptom questions
4. AYUSH consultation mode with Ayurveda-oriented history
5. Potential red-flag detection and staff escalation
6. Paper medical-record scan/upload workflow
7. Prototype clinical document extraction from supplied text
8. Structured physician-ready summary
9. Department recommendation with General Medicine fallback
10. Patient token generation
11. Department-level doctor login with current doctor name + shift
12. Doctor queue, call/start/complete and review/verification
13. Staff triage dashboard
14. Hospital Admin department/staff management and audit log

## Run

```powershell
python app.py
```
Then open `http://127.0.0.1:5000`.

## Architecture

Patient → Language → Identity → Normal/AYUSH → Adaptive History → Voice/Touch → Document Scan/Upload → Clinical Extraction → Red Flags → Structured Summary → Department Routing → Token → Doctor Review

## Production roadmap

Replace prototype adapters with validated Indian-language ASR, medical OCR, clinical NLP/LLM, FHIR/ABDM/HIS connectors, encrypted storage, RBAC, secure password hashing, TLS, rate limiting, consent management, retention/deletion policies, and clinically validated red-flag rules.
