# 🏥 MediKiosk
### AI-Assisted Multilingual Clinical Intake System


MediKiosk is a smart clinical intake kiosk designed to make the patient registration and pre-consultation process faster, simpler, multilingual, and more structured.

Instead of making patients repeatedly explain their symptoms at the reception desk, MediKiosk collects their information through an interactive intake workflow, uses a **locally running Gemma 4 E4B model** to understand the patient's responses and ask relevant follow-up questions, and prepares a structured summary for clinical review.

---

## 🎯 Problem

Traditional hospital registration often requires patients to:

- Explain the same symptoms repeatedly
- Communicate through language barriers
- Wait for basic information collection
- Provide medical documents manually
- Answer generic questions that may not be relevant to their complaint

This increases waiting time and puts additional workload on hospital staff.

---

## 💡 Our Solution

MediKiosk acts as an **AI-assisted first-level clinical intake system**.

The system:

1. Collects patient information.
2. Allows the patient to choose **Tamil or English**.
3. Accepts symptoms through text and supported voice interaction.
4. Uses **local Gemma 4 E4B** to analyze the patient's response.
5. Generates relevant follow-up questions.
6. Continues the adaptive interview until essential intake information is collected.
7. Performs safety / red-flag screening.
8. Creates a structured clinical intake summary.
9. Supports medical document OCR using local processing.
10. Provides patient token / queue and doctor-assignment workflow.

### Important

MediKiosk is an **AI-assisted clinical intake tool**, not an autonomous diagnostic system.

The AI does not replace a doctor and does not make the final medical decision.

---

# 🧠 AI Architecture

The core AI is designed to run locally.

```text
                 ┌─────────────────────┐
                 │     Patient Input   │
                 │ Text / Voice / Form │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Clinical Intake    │
                 │    Controller       │
                 └──────────┬──────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │     Local Ollama         │
              │      Gemma 4 E4B         │
              │                          │
              │ Symptom Understanding    │
              │ Follow-up Questions      │
              │ Structured Summary       │
              └────────────┬─────────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │ Adaptive Interview       │
              │                          │
              │ Question → Answer →      │
              │ Analyze → Next Question  │
              └────────────┬─────────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │ Clinical Intake Summary  │
              │                          │
              │ • Chief complaint        │
              │ • Duration               │
              │ • Symptoms               │
              │ • Relevant information   │
              │ • Safety indicators      │
              └────────────┬─────────────┘
                           │
                           ▼
                    👨‍⚕️ Doctor Review