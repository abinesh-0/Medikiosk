# 🏥 MediKiosk

### AI-Assisted Multilingual Patient Intake System

MediKiosk is a patient-facing digital clinical intake system designed to make the initial patient information-gathering process faster, more structured, multilingual, and accessible.

Instead of asking every patient the same fixed set of questions, MediKiosk uses an **adaptive clinical interview workflow** to analyze the patient's input and generate relevant follow-up questions.

The system supports **Tamil and English**, voice-assisted interaction, structured patient data collection, safety screening, and clinical summary generation.

> ⚠️ **Medical Disclaimer**
>
> MediKiosk is a clinical intake and decision-support prototype. It does not diagnose diseases, prescribe treatment, or replace a qualified healthcare professional.

---

# 🎯 Problem

Traditional patient intake can be:

- Time-consuming for healthcare staff
- Repetitive
- Difficult to manage with large patient volumes
- Challenging for patients with language barriers
- Inconsistent when collecting important symptoms and history
- Difficult to convert into structured clinical information

Patients may provide information in their own words, but important details such as duration, severity, associated symptoms, and relevant history may still need to be collected.

---

# 💡 Our Solution

MediKiosk provides an AI-assisted conversational intake workflow.

The patient can:

1. Select **Tamil or English**
2. Enter or speak their symptoms
3. Receive an AI-generated relevant follow-up question
4. Answer using text, predefined options, or voice
5. Continue through multiple adaptive questions
6. Receive safety/urgency screening
7. Complete the intake
8. Generate a structured clinical summary for healthcare staff

The system focuses on **information collection**, not medical diagnosis.

---

# 🧠 AI-Powered Adaptive Interview

The core feature of MediKiosk is its **adaptive questioning system**.

Instead of following only a fixed questionnaire:

```text
Patient Input
      ↓
Analyze Patient Response
      ↓
Identify Missing Clinical Information
      ↓
Generate Relevant Follow-up Question
      ↓
Patient Answer
      ↓
Repeat if More Information Is Needed
      ↓
Clinical Summary

Patient:
"I have fever"

        ↓

MediKiosk:
"How many days have you had the fever?"

        ↓

Patient:
"3 days"

        ↓

MediKiosk:
"Do you have cough, cold, or breathing difficulty?"

        ↓

Patient:
"No"

        ↓

Continue collecting relevant information
        ↓

Structured Clinical Summary

**🔄 System Architecture**
┌──────────────────────────────┐
│       Patient / Kiosk        │
│                              │
│ Tamil / English              │
│ Text / Voice                 │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Flask Web Server       │
│                              │
│ Session & Intake Management  │
│ Question Flow                │
│ Language Management          │
│ Safety Workflow              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     AI Service Layer         │
│                              │
│ Ollama                       │
│ Gemma 4 E4B                  │
│                              │
│ Adaptive Questions           │
│ Response Analysis            │
│ Clinical Summary             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Data Layer             │
│                              │
│ SQLite / MySQL               │
│ Patient Intake Data          │
│ Session Information          │
│ Structured Responses         │
└──────────────────────────────┘

**🛠️ Technology Stack**
| Layer                | Technology                           |
| -------------------- | ------------------------------------ |
| Backend              | Python                               |
| Web Framework        | Flask                                |
| AI Runtime           | Ollama                               |
| AI Model             | Gemma 4 E4B                          |
| ORM                  | SQLAlchemy                           |
| Database             | SQLite / MySQL                       |
| MySQL Driver         | PyMySQL                              |
| Frontend             | HTML                                 |
| Styling              | CSS                                  |
| Client Logic         | JavaScript                           |
| Voice                | Browser-supported voice capabilities |
| Development Platform | Windows                              |
| Python               | Python 3.x                           |


**📁 Project Structure**
MediKiosk/
│
├── app.py
├── config.py
├── requirements.txt
│
├── models/
│   └── ...
│
├── routes/
│   └── ...
│
├── services/
│   └── ...
│
├── templates/
│   └── ...
│
├── static/
│   └── ...
│
├── demo_ui/
│   ├── app.js
│   └── ...
│
├── VERIFY_PROJECT.py
├── JUDGE_PITCH.md
├── PROJECT_ARCHITECTURE.md
│
├── .env
└── medikiosk.db
