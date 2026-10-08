LANGUAGES = {"English": "en-IN", "Tamil": "ta-IN"}
ROLES = {"PATIENT", "DOCTOR", "TRIAGE", "ADMIN"}

# Fixed questions are used only as a safe fallback. The adaptive engine chooses a smaller,
# answer-aware path first and skips fields already covered by the patient's answer.
NORMAL_SECTIONS = [
    ("chief_complaint", "What is your main health problem today?"),
    ("history_present_illness", "When did it start, and is it getting better, worse, or staying the same?"),
    ("severity", "How severe is it: mild, moderate, or severe?"),
    ("associated_symptoms", "What other symptoms are happening along with it?"),
    ("past_medical_history", "Do you have any previous medical conditions?"),
    ("past_surgical_history", "Have you had any previous surgeries or hospital admissions?"),
    ("medication_history", "Are you currently taking any medicines?"),
    ("allergy_history", "Do you have any medicine, food, or other allergies?"),
    ("family_history", "Are there important medical conditions in your family?"),
    ("personal_history", "Tell us about your daily habits, food, sleep and activity."),
    ("social_history", "Is there any relevant social or occupational information?"),
    ("review_of_systems", "Is there anything else important you want the doctor to know?"),
    ("investigation_history", "Do you have previous test or scan results?"),
]

AYUSH_SECTIONS = [
    ("prakriti", "Please describe your Prakriti information, if known."),
    ("vikriti", "Please describe your current Vikriti information, if known."),
    ("sara", "Tell us about Sara, if assessed."),
    ("samhanana", "Tell us about Samhanana, if assessed."),
    ("pramana", "Tell us about Pramana, if assessed."),
    ("satmya", "Tell us about Satmya, if assessed."),
    ("sattva", "Tell us about Sattva, if assessed."),
    ("ahara_shakti", "Tell us about Ahara Shakti, if assessed."),
    ("vyayama_shakti", "Tell us about Vyayama Shakti, if assessed."),
    ("vaya", "Tell us about Vaya."),
    ("ahara_vihara", "Describe your Ahara and Vihara."),
    ("nidana", "Are there known Nidana or triggers?"),
    ("samprapti", "Describe Samprapti information, if assessed."),
    ("agni", "How is your Agni, if known?"),
    ("koshtha", "How is your Koshtha, if known?"),
]

NORMAL_TA = {
    "chief_complaint": "இன்று உங்களுக்கு முக்கியமாக என்ன உடல்நலப் பிரச்சனை உள்ளது?",
    "history_present_illness": "இது எப்போது தொடங்கியது? இப்போது நல்லதாகிறதா, மோசமாகிறதா அல்லது அதேபோல இருக்கிறதா?",
    "severity": "பிரச்சனையின் தீவிரம் எப்படி உள்ளது: லேசா, மிதமா அல்லது அதிகமா?",
    "associated_symptoms": "இதனுடன் வேறு என்ன அறிகுறிகள் இருக்கின்றன?",
    "past_medical_history": "உங்களுக்கு முன்பு ஏதேனும் உடல்நலப் பிரச்சனைகள் இருந்ததா?",
    "past_surgical_history": "முன்பு ஏதேனும் அறுவை சிகிச்சை அல்லது மருத்துவமனை அனுமதி இருந்ததா?",
    "medication_history": "தற்போது ஏதேனும் மருந்துகள் எடுத்துக்கொள்கிறீர்களா?",
    "allergy_history": "மருந்து, உணவு அல்லது வேறு ஏதேனும் அலர்ஜி உள்ளதா?",
    "family_history": "உங்கள் குடும்பத்தில் முக்கியமான உடல்நலப் பிரச்சனைகள் உள்ளதா?",
    "personal_history": "உங்கள் தினசரி உணவு, தூக்கம் மற்றும் உடற்பயிற்சி பற்றி சொல்லுங்கள்.",
    "social_history": "வேலை அல்லது சமூக வாழ்க்கை தொடர்பான முக்கிய தகவல் ஏதேனும் உள்ளதா?",
    "review_of_systems": "மருத்துவர் தெரிந்துகொள்ள வேண்டிய வேறு முக்கிய தகவல் ஏதேனும் உள்ளதா?",
    "investigation_history": "முன்பு எடுத்த பரிசோதனை அல்லது ஸ்கேன் முடிவுகள் உள்ளதா?",
}

AYUSH_TA = {
    "prakriti": "உங்கள் பிரகிருதி (Prakriti) பற்றி தகவல் தெரிந்தால் சொல்லுங்கள்.",
    "vikriti": "தற்போதைய விகிருதி (Vikriti) பற்றி தெரிந்தால் சொல்லுங்கள்.",
    "sara": "சாரா (Sara) மதிப்பீடு செய்யப்பட்டிருந்தால் அதன் தகவலை சொல்லுங்கள்.",
    "samhanana": "சம்ஹனன (Samhanana) மதிப்பீடு செய்யப்பட்டிருந்தால் சொல்லுங்கள்.",
    "pramana": "பிரமாண (Pramana) மதிப்பீடு செய்யப்பட்டிருந்தால் சொல்லுங்கள்.",
    "satmya": "சாத்ம்ய (Satmya) பற்றி தெரிந்தால் சொல்லுங்கள்.",
    "sattva": "சத்த்வ (Sattva) மதிப்பீடு பற்றி சொல்லுங்கள்.",
    "ahara_shakti": "ஆஹார சக்தி (Ahara Shakti) பற்றி சொல்லுங்கள்.",
    "vyayama_shakti": "வ்யாயாம சக்தி (Vyayama Shakti) பற்றி சொல்லுங்கள்.",
    "vaya": "உங்கள் வயது தொடர்பான தகவலை சொல்லுங்கள்.",
    "ahara_vihara": "உங்கள் உணவு மற்றும் வாழ்க்கை முறையை (Ahara-Vihara) பற்றி சொல்லுங்கள்.",
    "nidana": "அறிகுறிகளை அதிகரிக்கும் காரணிகள் அல்லது தூண்டுதல்கள் (Nidana) உள்ளதா?",
    "samprapti": "சம்பிராப்தி (Samprapti) மதிப்பீடு இருந்தால் அதன் தகவலை சொல்லுங்கள்.",
    "agni": "அக்னி (Agni) எப்படி உள்ளது என்று தெரிந்தால் சொல்லுங்கள்.",
    "koshtha": "கோஷ்டம் (Koshtha) பற்றி தெரிந்தால் சொல்லுங்கள்.",
}

DEPARTMENT_KEYWORDS = {
    "Cardiology": ["chest pain", "chest discomfort", "palpitation", "heart", "chest", "மார்பு", "இதயம்"],
    "Pulmonology": ["breathing", "breathlessness", "cough", "wheeze", "asthma", "மூச்சு", "இருமல்"],
    "Neurology": ["seizure", "faint", "headache", "migraine", "weakness", "numbness", "தலைவலி", "மயக்கம்"],
    "Orthopaedics": ["bone", "joint", "knee", "back pain", "fracture", "shoulder", "மூட்டு", "முதுகு"],
    "Dermatology": ["skin", "rash", "itch", "acne", "eczema", "தோல்", "சொறி"],
    "ENT": ["ear", "nose", "throat", "sinus", "hearing", "காது", "மூக்கு", "தொண்டை"],
    "Gynaecology": ["period", "pregnancy", "menstrual", "pelvic", "மாதவிடாய்", "கர்ப்ப"],
    "Paediatrics": ["child", "baby", "infant", "குழந்தை"],
    "Ayurveda": ["ayurveda", "prakriti", "agni", "koshtha", "ஆயுர்வேத", "பிரகிருதி"],
    "General Medicine": ["fever", "cold", "vomit", "diarrhea", "stomach", "pain", "காய்ச்சல்", "வலி", "வாந்தி"],
}

RED_FLAG_RULES = [
    ("CHEST_BREATHING", ["chest pain", "chest discomfort", "severe breathing", "difficulty breathing", "மார்பு வலி", "மூச்சுத்திணறல்"], "Potential urgent symptoms detected", "Seek immediate triage assessment.", "URGENT"),
    ("STROKE_LIKE", ["face droop", "speech difficulty", "sudden weakness", "one side weakness", "முகம் சாய்வு", "பேச முடியவில்லை", "திடீர் பலவீனம்"], "Sudden neurological warning symptom", "Immediate triage assessment is required.", "URGENT"),
    ("SEVERE_BLEEDING", ["heavy bleeding", "vomiting blood", "blood loss", "அதிக ரத்தப்போக்கு", "ரத்தம் வாந்தி"], "Significant bleeding reported", "Immediate triage assessment is required.", "HIGH"),
    ("LOSS_CONSCIOUSNESS", ["unconscious", "passed out", "fainted", "loss of consciousness", "நினைவிழப்பு", "மயங்கி விழுந்தேன்"], "Loss of consciousness reported", "Immediate clinical assessment is required.", "HIGH"),
    ("SEVERE_ALLERGY", ["anaphylaxis", "throat swelling", "severe allergic reaction", "தொண்டை வீக்கம்", "கடுமையான அலர்ஜி"], "Potential severe allergic reaction", "Immediate triage assessment is required.", "URGENT"),
]
