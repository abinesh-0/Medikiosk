# MediKiosk — SIH 26047 demo flow

## What the prototype demonstrates
1. Patient signs in and chooses English or Tamil.
2. Patient chooses Normal clinical history or AYUSH assessment.
3. Patient gives the chief complaint by voice, typing or touch.
4. The adaptive engine uses the complaint and previous answers to choose the next relevant question and skips fields already answered.
5. Red-flag rules continuously screen the whole conversation and can move the visit to triage priority.
6. Patient uploads a synthetic previous report/prescription. PDF/DOCX/text extraction and optional image OCR create a medical timeline entry; low confidence is marked for verification.
7. MediKiosk generates a structured physician-ready draft.
8. The system recommends a hospital department and creates a queue for non-urgent cases.
9. Doctor dashboard shows the case, summary, red flags, documents and timeline. Doctor can edit/confirm/reject the AI draft.
10. Mock HIS/FHIR/ABHA adapters demonstrate the intended integration boundary without claiming live ABDM access.

## Best judge demo
Use a synthetic case such as:
- Language: Tamil
- Mode: Normal
- Chief complaint: "எனக்கு 3 நாட்களாக காய்ச்சல் மற்றும் உடல் வலி இருக்கிறது"
- Show that the next question changes to fever duration/associated symptoms instead of repeating the chief complaint.
- Answer a red-flag-free path and upload `data/sample_reports/demo_lab_report.txt`.
- Finish intake and show department, queue number and physician summary.
- Then demonstrate an urgent synthetic example such as chest discomfort + breathing difficulty and show the triage priority banner. Do not present the alert as a diagnosis.
