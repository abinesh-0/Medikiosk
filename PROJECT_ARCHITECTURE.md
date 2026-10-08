# MediKiosk — SIH 26047 Architecture

## End-to-end

```text
PATIENT
  ↓
Language selection
  ↓
Patient registration / login
  ↓
Consent
  ↓
Voice / Touch / Text
  ↓
ASR (browser Web Speech; Whisper-family adapter point)
  ↓
Clinical understanding / extraction
  ↓
Adaptive Question Engine
  ↓
Structured Clinical History
  ├───────────────┐
  ↓               ↓
Red Flag Engine   Medical Document Intelligence
  ↓               ↓
Triage signal     Medical check → OCR/parser → clinical extraction
  │               ↓
  │            Timeline
  └───────┬───────┘
          ↓
   Physician-ready Summary
          ↓
 Department recommendation
          ↓
 Hospital directory / availability
          ↓
 Queue + doctor assignment
          ↓
 Doctor Dashboard
          ↓
 Review / Edit / Confirm / Reject
          ↓
 Mock HIS → FHIR → Mock ABDM/ABHA
```

## Why patient login exists

The project is not merely a token/registration kiosk. Login gives the system a stable patient identity across visits, consent records, documents, clinical summaries and future follow-ups. Hospital staff have separate role accounts.

## Language architecture

The landing page deliberately has only language selection. The language is then carried through the patient journey and stored on the patient/case. Question text and touch choices are localized; browser TTS uses `ta-IN` or `en-IN`; speech recognition uses the same locale.

## Adaptive question architecture

Every answer is stored in `case_answers`. The next question is selected from symptom branches before generic history. Because the answer state is persisted, a refresh does not restart or repeat the branch.

## Safety architecture

Red-flag detection is intentionally hybrid: deterministic screening rules are applied to the full conversation and stored as evidence. It does not produce a disease diagnosis. High/urgent cases go to triage rather than normal queue.

## AYUSH architecture

AYUSH mode adds structured Ayurveda-oriented history: Prakriti, Vikriti, Sara, Samhanana, Pramana, Satmya, Sattva, Ahara Shakti, Vyayama Shakti, Vaya, Ahara-Vihara, Nidana, Samprapti, Agni and Koshtha. It remains an intake/structuring layer and does not recommend treatment.

## Document architecture

The document service first checks whether extracted content looks medical. Non-medical content is rejected. Accepted documents are parsed/OCR'd, classified, extracted into diagnoses/medicines/investigations/important text, assigned confidence and marked for verification when confidence is low.

## Doctor handoff

The patient never chooses a doctor. Department recommendation is followed by availability lookup. A specialist is used when available; General Medicine is the prototype fallback. A notification record is created for the assigned clinician; actual email delivery is not falsely claimed.

## Data and AI model requirement

No manually trained ML dataset is required to run the prototype. Synthetic demo data and deterministic fallback logic are included. An LLM/Whisper-family integration can be attached later through the service boundaries.
