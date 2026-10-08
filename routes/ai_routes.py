import os
import json
import time
import logging
import requests
from pathlib import Path
from flask import Blueprint, jsonify, request, current_app
from services.ocr.ocr_engine import extract as ocr_extract
from services.ocr.clinical_document_extractor import extract as clinical_extract
from services.ai.llm_service import generate_json, generate_text
from services.ai.clinical_reasoner import answer_clinical_query
from utils.file_utils import save_upload
from utils.validators import allowed_extension

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai", __name__)

def mask_key(k):
    if not k:
        return ""
    k = str(k).strip()
    if len(k) <= 8:
        return "****"
    return k[:6] + "..." + k[-4:]

@ai_bp.get("/config")
def get_config():
    """Returns current AI configuration, masked keys, and provider statuses."""
    ollama_base = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip()
    ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:e4b").strip()

    ollama_online = False
    try:
        r = requests.get(f"{ollama_base.rstrip('/')}/api/tags", timeout=2)
        if r.status_code == 200:
            models = [m.get("name", "") for m in r.json().get("models", [])]
            ollama_online = any(ollama_model in m for m in models) or (len(models) > 0)
    except Exception:
        ollama_online = False

    return jsonify(
        success=True,
        ollama={
            "base_url": ollama_base,
            "model": ollama_model,
            "status": "ONLINE" if ollama_online else "OFFLINE",
            "is_local": True
        },
        gemini={
            "key_masked": "N/A (LOCAL_GEMMA4_ACTIVE)",
            "has_key": ollama_online,
            "model": f"{ollama_model} (Local)",
            "status": "ONLINE (Local Gemma 4)" if ollama_online else "OFFLINE"
        },
        openrouter={
            "key_masked": "N/A (LOCAL_GEMMA4_ACTIVE)",
            "has_key": False,
            "model": f"{ollama_model} (Local)",
            "status": "REPLACED_BY_LOCAL_AI"
        },
        primary_provider="OLLAMA_GEMMA4" if ollama_online else "LOCAL_RULES"
    )

@ai_bp.post("/config")
def update_config():
    """Update Ollama model and endpoint in runtime and persist to .env file."""
    data = request.get_json() or {}
    
    updated = {}
    if "ollama_base_url" in data and data["ollama_base_url"].strip():
        val = data["ollama_base_url"].strip()
        os.environ["OLLAMA_BASE_URL"] = val
        updated["OLLAMA_BASE_URL"] = val
    if "ollama_model" in data and data["ollama_model"].strip():
        val = data["ollama_model"].strip()
        os.environ["OLLAMA_MODEL"] = val
        updated["OLLAMA_MODEL"] = val

    # Persist changes into .env if present
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists() and updated:
        try:
            lines = env_path.read_text(encoding="utf-8").splitlines()
            new_lines = []
            handled = set()
            for line in lines:
                matched = False
                for k, v in updated.items():
                    if line.startswith(f"{k}="):
                        new_lines.append(f"{k}={v}")
                        handled.add(k)
                        matched = True
                        break
                if not matched:
                    new_lines.append(line)
            for k, v in updated.items():
                if k not in handled:
                    new_lines.append(f"{k}={v}")
            env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        except Exception as e:
            logger.warning("Failed to update .env: %s", e)

    return jsonify(
        success=True,
        message="Local AI configuration updated successfully",
        updated=list(updated.keys())
    )

@ai_bp.post("/test")
def test_connection():
    """Test connection to local Ollama Gemma 4 and return latency + status."""
    data = request.get_json() or {}
    base_url = (data.get("base_url") or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).strip().rstrip("/")
    model = (data.get("model") or os.getenv("OLLAMA_MODEL", "gemma4:e4b")).strip()

    t0 = time.perf_counter()
    url = f"{base_url}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "Confirm you are active by replying with: OK: OLLAMA_GEMMA4_CONNECTED"}
        ],
        "options": {"temperature": 0.1, "num_predict": 50},
        "think": False,
        "stream": False
    }
    try:
        r = requests.post(url, json=payload, timeout=20)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        if r.status_code == 200:
            body = r.json()
            text = (body.get("message") or {}).get("content", "Connected").strip()
            return jsonify(
                success=True,
                provider="OLLAMA",
                latency_ms=ms,
                model=model,
                message=text
            )
        else:
            return jsonify(
                success=False,
                provider="OLLAMA",
                latency_ms=ms,
                status_code=r.status_code,
                error=r.text[:300]
            ), 400
    except Exception as e:
        ms = round((time.perf_counter() - t0) * 1000, 1)
        return jsonify(
            success=False,
            provider="OLLAMA",
            latency_ms=ms,
            error=str(e)
        ), 500

def detect_query_language(text: str, user_selected_lang: str = "English") -> str:
    """
    Detects the language of the patient's message.
    1. If user explicitly selected Tamil, respect their choice and return 'Tamil'.
    2. If user message contains Tamil Unicode characters, return 'Tamil'.
    3. If user message contains Tanglish patterns, return 'Tamil'.
    4. Otherwise, return 'English'.
    """
    if user_selected_lang == "Tamil":
        return "Tamil"

    if not text:
        return user_selected_lang or "English"

    import re

    # ── 1. Tamil Unicode characters (definitive Tamil signal)
    if re.search(r'[\u0B80-\u0BFF]', text):
        return "Tamil"

    t_lower = text.lower().strip()

    # ── 2. Comprehensive Tanglish patterns (Tamil spoken in English letters)
    tanglish_patterns = [
        # Question words
        r'\b(enna|epdi|eppadi|eppo|eppothu|enga|engae|yen|yean|edhuku|ethuku|yaaru|yaar)\b',
        # Affirmation / negation
        r'\b(irukku|iruku|irukanga|illai|illa|seri|venuma|vendam|venda|aam|aama)\b',
        # Quantity / degree
        r'\b(evlo|evalavu|romba|konjam|niraiya|adhigama|kuravaga|kuranja)\b',
        # Demonstratives
        r'\b(idhu|ithu|adhu|athu|indha|andha|inga|anga|avan|aval|avanga)\b',
        # Verbs / actions
        r'\b(sollunga|solunga|sollu|paaru|paathu|theriyuma|theriyala|theriyathu)\b',
        r'\b(marundhu|marunthu|maathirai|mathirai|valikudhu|valikuthu|vali)\b',
        # Medical Tanglish suffix patterns
        # NOTE: Tamil postpositions (la, le, ku, ah, aa) must be standalone words,
        # not a prefix of longer English words (e.g. 'level', 'lead', 'label').
        # Use (?=\s|[?!,.]|$) lookahead to prevent matching inside longer words.
        r'\b(report|blood|sugar|bp|hemoglobin|platelet|wbc|rbc|tlc|pcv|mcv|mch)\s+(la|le|oda|ku|ah|aa)(?=\s|[?!,.]|$)',
        r'\b(normal|abnormal|low|high|ok)\s*(ah|aa|dha|tha|na|naa)(?=\s|[?!,.]|$)',
        r'\b(enna|en)\s+(irukku|solludu|pannudu|aaguthu|aachhu)\b',
        # Pronouns / personal
        r'\b(naan|naanum|ungaluku|ungaloda|unaku|unoda|avanga|avaruku)\b',
        # Possibility words
        r'\b(paakalam|parkalam|seyyalam|mudiyuma|mudiyathu|theriyuma)\b',
        # Location/direction suffixes — require standalone postposition
        r'\b(intha|antha)\s+(report|test|result|value|count)\b',
        r'\b(report|test|result|value|count)\s+(la|le|ku|oda)(?=\s|[?!,.]|$)\s+(enna|evlo|evvalo)\b',
        # Common sentence endings — standalone ah/aa before ? only
        r'\s(ah|aa)\s*\?',
        r'\b(nalla|nallaa|ketta|kettaa|avlo|appadi|ippadi|ipdi|apdi)\b',
        # Doctor / hospital Tanglish
        r'\b(maruthuvar|maruthuvam)\b',
        r'\b(doctor|clinic|hospital)\s+(ku|kku|pakkam|kitta)\b',
        # Common Tamil sentence patterns with standalone Tanglish terms
        r'\b(platelet|hemoglobin|rbc|wbc)\s+(evlo|evvalo)\b',
    ]

    for pat in tanglish_patterns:
        if re.search(pat, t_lower):
            return "Tamil"

    return "English"


def is_out_of_domain_query(text: str) -> bool:
    """Detect non-medical unrelated queries like trivia, jokes, weather, or coding."""
    import re
    t_lower = text.lower().strip()
    unrelated_patterns = [
        r'\b(prime minister|president|weather|forecast|joke|riddle|python|javascript|code|coding|movie|cricket|football|capital of|who wrote|who invented)\b',
        r'\b(write a poem|write an essay|write code|sing a song|tell a story|recipe|cooking)\b',
    ]
    for pat in unrelated_patterns:
        if re.search(pat, t_lower):
            return True
    return False


@ai_bp.post("/doc-analyze")
def doc_analyze():
    """Standalone Medical Document Analyzer. Accepts uploaded/scanned document or raw clinical text."""
    try:
        extracted_text = ""
        conf = 0.95
        doc_name = "Direct Input"

        f = request.files.get("file")
        if f and f.filename:
            doc_name = f.filename
            if not allowed_extension(f.filename, current_app.config["ALLOWED_EXTENSIONS"]):
                return jsonify(success=False, error="Unsupported file type. Use PDF, PNG, JPG, or DOCX"), 400
            original, stored, path, size = save_upload(f, Path(current_app.config["UPLOAD_FOLDER"]) / "documents")
            extracted_text, conf = ocr_extract(path)
            if not extracted_text.strip() and request.form.get("text"):
                extracted_text = request.form.get("text")
        else:
            req_json = request.get_json(silent=True) or {}
            extracted_text = req_json.get("text") or request.form.get("text") or ""
            doc_name = req_json.get("filename") or "Manual Clinical Report"

        if not extracted_text.strip():
            return jsonify(success=False, error="Could not extract readable text from this document. Please ensure the document is well-lit and clear, or paste text directly."), 400

        # Run clinical information extraction pipeline
        clinical_info = clinical_extract(extracted_text)

        return jsonify(
            success=True,
            filename=doc_name,
            ocr_confidence=round(conf, 2),
            raw_text=extracted_text,
            analysis=clinical_info,
            source=clinical_info.get("ai_source", "Vision OCR")
        )
    except Exception as e:
        logger.exception("Error in doc_analyze: %s", e)
        return jsonify(success=False, error=str(e)), 500


@ai_bp.post("/doc-chat")
def doc_chat():
    """Interactive AI Chatbot answering questions based on an analyzed medical document."""
    try:
        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        doc_context = data.get("document_context") or ""
        user_lang = data.get("language") or "English"
        history = data.get("history") or []

        if not message:
            return jsonify(success=False, error="Message is required"), 400

        import re
        t_lower = message.lower().strip()

        # 1. Check for explicit language switch requests
        if re.search(r'^(tamil|தமிழ்|தமிள்)$|\b(tamil\s*la\s*(explain|sollu|pesu|pannu)|in\s*tamil|change\s*to\s*tamil|explain\s*in\s*tamil|tamilil)\b', t_lower):
            reply = "நிச்சயமாக! இனி விளக்கங்கள் அனைத்தும் தமிழில் வழங்கப்படும். உங்கள் மருத்துவ அறிக்கை பற்றி என்ன தெரிந்து கொள்ள வேண்டும்?"
            return jsonify(success=True, reply=reply, source="LANG_CONTROL", language="Tamil")

        if re.search(r'^(english|ஆங்கிலம்)$|\b(in\s*english|change\s*to\s*english|explain\s*in\s*english|english\s*la)\b', t_lower):
            reply = "Switched to English. I am ready to answer your questions regarding your medical report."
            return jsonify(success=True, reply=reply, source="LANG_CONTROL", language="English")

        # 2. Detect language (English vs Tamil vs Tanglish)
        detected_lang = detect_query_language(message, user_lang)

        # 3. Medical domain restriction
        if is_out_of_domain_query(message):
            if detected_lang == "Tamil":
                reply = "இந்த மருத்துவ அறிக்கை தொடர்பான தகவல்களுக்கு மட்டுமே என்னால் உதவ முடியும். அறிக்கை பற்றிய உங்கள் கேள்விகளைக் கேட்கவும்."
            else:
                reply = "I can help only with medical information related to this report. Please ask any question about your tests, medications, or doctor notes."
            return jsonify(success=True, reply=reply, source="DOMAIN_GUARD", language=detected_lang)

        # 4. Clinical Grounded Reasoning
        is_tamil = (detected_lang == "Tamil")
        grounded_reply = answer_clinical_query(doc_context, message, language=detected_lang, is_tamil=is_tamil)

        # Check if the query was decisively answered by the clinical reasoner
        # (e.g. specific lab tests, report summaries, abnormal checks, medications, doctor referral, patient isolation, unreadable checks)
        msg_l = message.lower()
        is_direct_clinical = any(k in msg_l for k in [
            'explain', 'simple', 'விளக்கு', 'சொல்லு', 'summary', 'report', 'அறிக்கை',
            'hemoglobin', 'hb', 'wbc', 'platelet', 'neutrophil', 'lymphocyte', 'eosinophil', 'monocyte', 'basophil', 'rbc',
            'hct', 'mcv', 'mch', 'mchc', 'rdw', 'glucose', 'sugar', 'creatinine', 'cholesterol',
            'abnormal', 'problem', 'மருந்து', 'மாத்திரை', 'medication', 'medicine', 'tablet',
            'doctor', 'மருத்துவர்', 'ரமேஷ்', 'ramesh', 'ranjana'
        ])

        if is_direct_clinical and grounded_reply:
            reply = grounded_reply
            source = "CLINICAL_GROUNDED_ENGINE"
        else:
            # For open conversational queries, try LLM with compact max_tokens (180) to avoid 402 errors
            history_text = "\n".join([f"{h.get('sender', 'User')}: {h.get('text', '')}" for h in history[-6:]])
            if is_tamil:
                lang_instruction = (
                    "Respond entirely in natural, polite everyday Tamil script (தமிழ்). "
                    "2-3 short sentences. Ground answers strictly in the document context. "
                    "Do NOT say 'consult your physician' as the only answer."
                )
            else:
                lang_instruction = (
                    "Respond in clear, concise, patient-friendly English (2-3 short sentences). "
                    "Ground answers strictly in the document context. "
                    "Do NOT say 'consult your physician' as the only answer."
                )

            prompt = (
                f"You are MediKiosk's Document-Grounded Clinical AI Assistant.\n"
                f"{lang_instruction}\n\n"
                f"--- DOCUMENT CLINICAL CONTEXT ---\n{doc_context[:3500]}\n--- END CONTEXT ---\n\n"
                f"--- CONVERSATION HISTORY ---\n{history_text}\n--- END HISTORY ---\n\n"
                f"Patient Question: {message}\n\n"
                f"Clinical Assistant Response:"
            )

            llm_reply, llm_src = generate_text(prompt, max_tokens=180, temperature=0.15)
            if llm_reply and llm_reply != "[LOCAL_FALLBACK]" and "consult your physician for clinical decisions" not in llm_reply.lower():
                reply = llm_reply.strip()
                source = llm_src
            else:
                reply = grounded_reply or (
                    "உங்கள் அறிக்கையின்படி தகவல்கள் ஆய்வு செய்யப்பட்டுள்ளன. குறிப்பிட்ட பரிசோதனை முடிவுகள் பற்றி கேட்கலாம்."
                    if is_tamil else
                    "Based on the documented findings in your report, your results have been reviewed. You can ask about any specific test or abnormal value."
                )
                source = "CLINICAL_GROUNDED_ENGINE"

        return jsonify(
            success=True,
            reply=reply.strip(),
            source=source,
            language=detected_lang
        )
    except Exception as e:
        logger.exception("Error in doc_chat: %s", e)
        # Ensure we always return JSON, never a 500 HTML page
        fallback_msg = (
            "மருத்துவ அறிக்கை தகவல் செயலாக்கத்தில் பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்."
            if (request.get_json(silent=True) or {}).get("language") == "Tamil"
            else "An error occurred while analyzing the document query. Please try again."
        )
        return jsonify(success=False, error=str(e), reply=fallback_msg), 200


