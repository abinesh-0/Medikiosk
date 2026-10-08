# 🏥 MediKiosk



MediKiosk is a patient-facing clinical intake prototype designed to make the initial patient case-taking process more structured, accessible, and efficient.

The system provides a guided question-based workflow where patients can provide information through a simple interface. The project is designed as a Hackathon prototype with support for multilingual interaction, voice-related controls, structured data collection, and a local-first AI direction.

> ⚠️ **Medical Disclaimer:** MediKiosk is a software prototype for patient intake and clinical-support workflows. It is **not a medical diagnosis system** and must not replace a qualified doctor or healthcare professional.

---

## ✨ Features

- 🌐 **English + Tamil language support**
- 🤖 **AI-assisted patient questioning**
- 🧠 **Local AI support / local-first architecture**
- 📝 **Structured patient information collection**
- 🔊 **Question read-aloud / voice control**
- 🎙️ **Voice/microphone answer control**
- ⬅️ **Previous-question navigation**
- ➡️ **Next-question navigation**
- 🏠 **Home/Exit button from the question page**
- 📊 **Question progress tracking**
- 💾 **SQLite support for local demos**
- 🗄️ **MySQL support**
- 🔐 **Privacy-oriented local processing direction**
- 🧪 **Demo-friendly development setup**
- 💻 **Windows + Python development support**

---

#  Problem Statement

Traditional patient intake can involve:

- Repetitive questioning
- Manual data entry
- Inconsistent information collection
- Language barriers
- Long waiting times
- Difficulty organizing patient responses
- Additional workload for healthcare staff

MediKiosk attempts to improve the initial information-gathering process by providing a guided digital patient-intake workflow.

---

#  Proposed Solution

MediKiosk provides a digital kiosk-style interface where the patient can:

1. Select a language.
2. Start the patient intake process.
3. Receive guided questions.
4. Listen to questions using voice functionality.
5. Enter or provide answers.
6. Move between questions.
7. Return to the previous question when required.
8. Exit the current question flow using the Home button.
9. Continue through the complete case-taking process.
10. Generate/organize structured patient information for the next stage of the workflow.

---

#  AI Direction

MediKiosk is designed with a **local-first AI direction**.

Depending on the enabled modules, AI can assist with:

- Generating relevant follow-up questions
- Organizing patient responses
- Summarizing collected information
- Structuring case information
- Supporting multilingual interaction
- Assisting the clinical intake workflow

The goal is to minimize unnecessary dependency on paid cloud AI APIs.

---

#  Local AI / Zero API Cost Direction

A local AI model can run directly on the user's computer instead of sending every request to a paid cloud AI API.

### Advantages

- No per-request API charges
- Better control over data flow
- Reduced dependency on internet connectivity
- Useful for hackathon demonstrations
- Better privacy potential for sensitive workflows
- Can continue working locally after the required model is downloaded

### Important

Local AI performance depends on:

- CPU
- RAM
- Storage
- Model size
- Quantization
- Operating system
- Available GPU/VRAM

For lower-end laptops, lightweight models are generally more practical than large models.

---


# markdown
| AI Model | Gemma 4 EB4 |
| AI Runtime | Ollama / Local Runtime | . 
It uses OCR to extract text from the medical prescription.

```
```
#  Technology Stack

| Component | Technology |
|---|---|
| Backend | Python |
| Web Framework | Flask |
| ORM | SQLAlchemy |
| MySQL Driver | PyMySQL |
| Local Database | SQLite |
| Frontend | HTML |
| Styling | CSS |
| Client Logic | JavaScript |
| Development OS | Windows 10/11 |
| Terminal | Git Bash |
| Recommended Python | Python 3.13.x |

> **Important:** MediKiosk is currently a Python/Flask project. Do not use `npm` or Node.js commands unless a separate Node-based frontend has been added to the project.

---

# 📁 Project Structure

```text
Medikiosk/
│
├── app.py
├── config.py
├── requirements.txt
├── VERIFY_PROJECT.py
├── JUDGE_PITCH.md
├── PROJECT_ARCHITECTURE.md
├── debug_out.txt
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
├── .env
└── medikiosk.db
