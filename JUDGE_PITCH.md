# Judge Explanation — MediKiosk SIH 26047

## Problem in one sentence

Busy OPDs often have very little consultation time, while detailed patient history and previous records still need to be understood; this creates a first-mile information bottleneck before the clinician can make a decision.

## Our solution

MediKiosk is a patient-facing clinical intake layer, not a registration kiosk. It lets patients tell their story using voice, touch or typing in Tamil or English, asks symptom-specific follow-up questions, validates and extracts previous medical documents, screens for urgent warning signals, prepares a structured physician-ready draft and routes the case to the care team.

## What makes it different

1. **Language-first:** patient chooses Tamil or English before anything else.
2. **Elderly-first UX:** large touch targets, simple language, voice and text fallback.
3. **Adaptive history:** the symptom changes the next question instead of a long fixed form.
4. **AYUSH-aware:** Ayurveda-oriented history can be collected in the same workflow.
5. **Document intelligence:** the system checks whether an upload is actually medical before extracting useful clinical facts.
6. **Safety layer:** red flags are surfaced for human triage without claiming a diagnosis.
7. **Clinical routing:** department and doctor assignment use hospital availability rules; the patient does not choose the doctor.
8. **Doctor-in-control:** AI creates a draft; the doctor can edit, confirm or reject it.
9. **Interoperability-ready:** mock HIS/FHIR/ABDM adapters show where authorized production integrations fit.

## Judge demo script

### Demo 1 — Tamil patient

- Open MediKiosk.
- Select Tamil.
- Register/login.
- Start a general visit.
- Speak a synthetic example: “எனக்கு மூன்று நாட்களாக காய்ச்சல், இருமல் இருக்கு.”
- Show that the next question is about fever duration, then fever pattern/associated symptoms and respiratory follow-up.
- Tap a large answer button.
- Press the speaker button to hear the Tamil question.

### Demo 2 — Document intelligence

- Upload `data/sample_documents/demo_medical_report.txt`.
- Show medical-document confirmation.
- Show extracted medicine/investigation counts and OCR confidence.
- Explain that low-confidence image OCR is marked for verification.

### Demo 3 — Safety

- Use a synthetic example such as “severe chest pain with difficulty breathing”.
- Show the red-flag alert.
- Explain: this is a screening signal, not a diagnosis, and it goes to staff/triage.

### Demo 4 — Doctor handoff

- Complete a non-urgent synthetic case.
- Explain department recommendation → availability → assignment.
- Login as `doctor@medikiosk.local` / `Doctor@123`.
- Open the assigned case.
- Show history, adaptive answers, documents, timeline, red flags and AI draft.
- Edit and confirm.

### Demo 5 — AYUSH

- Start an AYUSH case.
- Show Prakriti, Vikriti, Agni, Koshtha, Ahara-Vihara, Nidana and related history.
- Explain that MediKiosk collects information for the Ayurveda clinician and does not prescribe treatment.

## Closing statement

“MediKiosk does not try to replace the doctor. It removes the information-collection bottleneck before the doctor sees the patient, while keeping language accessibility, safety screening, document intelligence, routing and clinician verification in one connected workflow.”
