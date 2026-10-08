import os
from dotenv import load_dotenv
load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"

from PIL import Image, ImageDraw
from services.ocr.ocr_engine import extract as ocr_extract
from services.ocr.clinical_document_extractor import extract as clinical_extract

# 1) Build a fake prescription/scan image with medical text
img = Image.new("RGB", (1200, 400), "white")
d = ImageDraw.Draw(img)
prescription = (
    "MediKiosk Hospital\n"
    "Patient: Ramesh Kumar, DOB: 12/05/1985\n"
    "Date: 15/09/2026\n\n"
    "Diagnosis: Acute bronchitis\n\n"
    "Medications:\n"
    "- Paracetamol 500mg tab, 1 tab thrice daily after food x 5 days\n"
    "- Azithromycin 500mg, 1 tab once daily for 3 days\n\n"
    "Investigations:\n"
    "- CBC: WBC 15000, Hb 12.5 g/dL\n"
    "- Chest X-ray: No acute consolidation\n"
)
d.text((20, 20), prescription, fill="black")
img.save("_sample_rx.png")

print("=== OCR ===")
text, conf = ocr_extract("_sample_rx.png")
print("ocr_conf:", conf)
print("ocr_text:\n", text)

print("\n=== Clinical extraction (LLM) ===")
info = clinical_extract(text)
for k in ["is_medical_document", "document_type", "diagnoses", "medications", "investigations", "ai_source"]:
    print(f"{k}: {info.get(k)}")

print("\n=== Tamil medical-history extraction (LLM) ===")
tamil_text = "பெயர்: லக்ஷ்மி, வயது 45. நோயறிதல்: பிரதிரோக மார்பு வலி, எரிச்சல். மருந்து: க்லோபிகோவிட்டரின் 10மிக்ரு, தினசரி. பரிசோதனை: எக்சிg 14 கிராம், அமில நீர் சோக் நகர்பு 120."
info2 = clinical_extract(tamil_text)
for k in ["is_medical_document", "document_type", "diagnoses", "medications", "investigations", "clinical_summary", "ai_source"]:
    print(f"{k}: {info2.get(k)}")

os.remove("_sample_rx.png")
