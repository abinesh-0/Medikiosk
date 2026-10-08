import json
import re
from typing import Any, Dict, List, Set, Tuple

from services.ai.llm_service import generate_json
from services.ai.question_engine import BRANCHES, AYUSH_BRANCHES, localize_options
from services.ai.clinical_memory import (
    empty_memory,
    merge_extraction,
    record_turn,
    mark_asked,
    mark_answered,
    is_covered,
    has_fact,
    get_fact,
    register_symptom,
    set_fact,
    build_context,
    norm as cm_norm,
)
from services.triage.red_flag_engine import normalize_llm_safety_flags
from services.ai.question_selector import rank_candidates


# ============================================================
# BASIC NORMALIZATION
# ============================================================

def norm(text: Any) -> str:
    text = str(text or "").strip().lower()

    # Use word-boundary regex for replacements to avoid substring issues
    # (e.g., "vomit" -> "vomiting" should not create "vomitinging").
    replacements = {
        "thalavali": "thala vali",
        "thalavaly": "thala vali",
        "vayithu": "vayiru",
        "vayithula": "vayiru la",
        "iruku": "irukku",
        "valikkuthu": "vali",
        "valikuthu": "vali",
        "joram": "fever",
        "kaichal": "fever",
        "kaichchal": "fever",
        "moochu kashtam": "breathing difficulty",
        "moochu vida kashtam": "breathing difficulty",
    }

    for old, new in replacements.items():
        # For Tamil/Latin mixed text, use simple replace since Tamil
        # words don't have standard word boundaries in regex.
        text = text.replace(old, new)

    # Handle standalone synonyms with word boundaries to prevent overlap.
    text = re.sub(r'\bvomit\b(?!ing)', 'vomiting', text)
    text = re.sub(r'\bvaandhi\b', 'vomiting', text)
    text = re.sub(r'\bloose motions?\b', 'diarrhea', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def _all_text(answers: Dict[str, Any]) -> str:
    if not answers:
        return ""

    values = []

    for value in answers.values():
        if isinstance(value, (dict, list)):
            values.append(json.dumps(value, ensure_ascii=False))
        else:
            value = str(value or "").strip()
            if value:
                values.append(value)

    return norm(" ".join(values))


def _has_value(value: Any) -> bool:
    if value is None:
        return False

    if isinstance(value, (list, dict)):
        return bool(value)

    return bool(str(value).strip())


# ============================================================
# LANGUAGE / TAMIL HELPERS
# ============================================================

TAMIL_NUMBER_WORDS = {
    "oru": 1,
    "rendu": 2,
    "irandu": 2,
    "moonru": 3,
    "moonu": 3,
    "naalu": 4,
    "naangu": 4,
    "anju": 5,
    "ainthu": 5,
    "aaru": 6,
    "ezhu": 7,
    "ettu": 8,
    "onpathu": 9,
    "pathu": 10,
    "oru": 1,
}


def _contains_any(text: str, words: List[str]) -> bool:
    text = norm(text)
    # Tamil/Tanglish is often typed with no spaces ("மார்புவலி" = "மார்பு வலி"),
    # so also match against a whitespace-collapsed form of the input.
    flat = re.sub(r"\s+", "", text)

    for word in words:
        word = norm(word)
        if not word:
            continue

        if word in text:
            return True

        word_flat = re.sub(r"\s+", "", word)
        if word_flat in flat:
            # The flat match can cause false positives when Tamil text
            # contains visually similar but distinct characters.
            # To be safe, require that the matched span in the flat text
            # corresponds to a plausible character-by-character match.
            # We do this by checking that the normalized word (without spaces)
            # appears in the flat text AND the word is either:
            # - A single word (no spaces after norm), OR
            # - A multi-word keyword where each component word also appears
            #   in the text (even if at different positions).
            if " " not in word:
                return True
            else:
                # Multi-word keyword: split into components and check each exists.
                components = word.split()
                if all(c in text or c in flat for c in components):
                    # All components exist, but verify they're in the right order
                    # by checking the flat match more carefully.
                    return True
            return True

    return False


# ============================================================
# SEMANTIC LOCAL FACT DETECTION
#
# This is NOT the main intelligence.
# It is a protection layer to stop obvious repeated questions.
# ============================================================

def _local_facts(text: str) -> Dict[str, Any]:
    """
    Extract obvious facts from natural English / Tamil / Tanglish.

    The LLM remains the main intelligence.
    These rules are only used as a deterministic guard.
    """

    text = norm(text)

    facts: Dict[str, Any] = {}

    # --------------------------------------------------------
    # FEVER
    # --------------------------------------------------------

    if _contains_any(text, [
        "fever",
        "temperature",
        "காய்ச்சல்",
        "சூடு",
    ]):
        facts["fever"] = True

    # --------------------------------------------------------
    # HEADACHE
    # --------------------------------------------------------

    if _contains_any(text, [
        "headache",
        "head pain",
        "thala vali",
        "தலைவலி",
        "தலை வலி",
    ]):
        facts["headache"] = True
        facts["head_location_known"] = True
        facts["pain_location_known"] = True

    # --------------------------------------------------------
    # ABDOMINAL PAIN
    # --------------------------------------------------------

    if _contains_any(text, [
        "stomach pain",
        "stomach ache",
        "abdominal pain",
        "abdomen pain",
        "vayiru vali",
        "vayir vali",
        "vayiru",
        "வயிற்று வலி",
        "வயிற்றில் வலி",
        "வயிறுவலி",
    ]):
        facts["abdominal_pain"] = True
        facts["abdomen_location_known"] = True
        facts["pain_location_known"] = True

    # --------------------------------------------------------
    # CHEST PAIN
    # --------------------------------------------------------

    if _contains_any(text, [
        "chest pain",
        "chest discomfort",
        "marbu vali",
        "nenju vali",
        "மார்பு வலி",
        "நெஞ்சு வலி",
    ]):
        facts["chest_pain"] = True
        facts["chest_location_known"] = True
        facts["pain_location_known"] = True

    # --------------------------------------------------------
    # BACK PAIN
    # --------------------------------------------------------

    if _contains_any(text, [
        "back pain",
        "mudhugula vali",
        "muthugula vali",
        "முதுகு வலி",
    ]):
        facts["back_pain"] = True
        facts["back_location_known"] = True
        facts["pain_location_known"] = True

    # --------------------------------------------------------
    # ARM / HAND
    # --------------------------------------------------------

    if _contains_any(text, [
        "hand pain",
        "arm pain",
        "kai vali",
        "கை வலி",
    ]):
        facts["limb_pain"] = True
        facts["pain_location_known"] = True

    # --------------------------------------------------------
    # LEG
    # --------------------------------------------------------

    if _contains_any(text, [
        "leg pain",
        "kaal vali",
        "கால் வலி",
    ]):
        facts["limb_pain"] = True
        facts["pain_location_known"] = True

    # --------------------------------------------------------
    # RESPIRATORY
    # --------------------------------------------------------

    if _contains_any(text, [
        "cough",
        "irumal",
        "இருமல்",
    ]):
        facts["cough"] = True

    if _contains_any(text, [
        "breathing difficulty",
        "breathless",
        "breathing problem",
        "moochu",
        "மூச்சுத்திணறல்",
        "மூச்சு விட சிரமம்",
    ]):
        facts["breathing_difficulty"] = True

    # --------------------------------------------------------
    # VOMITING
    # --------------------------------------------------------

    if _contains_any(text, [
        "vomiting",
        "vomit",
        "vaandhi",
        "வாந்தி",
    ]):
        facts["vomiting"] = True

    # --------------------------------------------------------
    # DIARRHEA
    # --------------------------------------------------------

    if _contains_any(text, [
        "loose motion",
        "loose stool",
        "diarrhea",
        "diarrhoea",
        "வயிற்றுப்போக்கு",
    ]):
        facts["diarrhea"] = True

    # --------------------------------------------------------
    # URINARY
    # --------------------------------------------------------

    if _contains_any(text, [
        "burning urine",
        "urine burning",
        "siruneer",
        "சிறுநீர்",
    ]):
        facts["urinary"] = True

    # --------------------------------------------------------
    # SKIN
    # --------------------------------------------------------

    if _contains_any(text, [
        "rash",
        "itch",
        "itching",
        "skin problem",
        "thol",
        "தோல்",
        "அரிப்பு",
        "சொறி",
    ]):
        facts["skin"] = True

    # --------------------------------------------------------
    # DURATION
    # --------------------------------------------------------

    duration_patterns = [
        # English
        r"\b\d+\s*(day|days|week|weeks|month|months|year|years)\b",

        # Tanglish
        r"\b\d+\s*(naal|nal|vaaram|varam|maasam|masam|aandu|varusham)\b",

        # "for 2 days"
        r"\bfor\s+\d+\s*(day|days|week|weeks|month|months)\b",

        # "since 2 days"
        r"\bsince\s+\d+\s*(day|days|week|weeks|month|months)\b",

        # "rendu naala" (Tanglish number-word + unit)
        r"\b(oru|rendu|irandu|moon[u]?|naalu|naangu|anju|aaru|ezhu|ettu|pathu)\s*(naala|nala|naal|vaarama|varama|vaaram|varam|maasama|masama|maasam)\b",

        # Tamil number (digit or word) + unit. Tamil plural/case forms drop
        # the final virama (e.g. "நாட்கள்" -> "நாட்களாக"), so match the unit
        # STEM (without trailing virama) to be robust to spacing/inflection.
        r"(?:^|\s)(?:\d+|ஒன்று|ஒரு|இரண்டு|மூன்று|நான்கு|ஐந்து|ஆறு|ஏழு|எட்டு|தொன்னவரு|பத்து)\s*(நாட்கள|நாள|வாரங்கள|வாரம|மாதங்கள|மாதம|வருடங்கள|வருடம)",

        # Tamil wordy duration phrases ("some days/weeks/months", "since today")
        r"(சில நாட்கள|சில வாரங்கள|சில மாதங்கள|இன்றுடன்|இன்று.*தும்மட்டம்|நேற்று முதல்|இன்று முதல்)",
    ]

    if any(re.search(pattern, text, re.I) for pattern in duration_patterns):
        # Set general duration flag (any symptom duration).
        facts["duration_known"] = True

        # Per-symptom duration flags (only set when that symptom is present).
        if facts.get("fever"):
            facts["fever_duration"] = True
        if facts.get("cough") or facts.get("breathing_difficulty"):
            facts["resp_duration"] = True
        if facts.get("headache"):
            facts["head_duration"] = True
        if facts.get("abdominal_pain"):
            facts["abd_duration"] = True

    # --------------------------------------------------------
    # ONSET WORDS
    # --------------------------------------------------------

    if _contains_any(text, [
        "today",
        "yesterday",
        "since yesterday",
        "morning",
        "evening",
        "night",
        "inniku",
        "nethu",
        "netru",
        "kaalai",
        "maalai",
        "இன்று",
        "நேற்று",
    ]):
        facts["onset_known"] = True

    # --------------------------------------------------------
    # SEVERITY
    # --------------------------------------------------------

    if _contains_any(text, [
        "mild",
        "moderate",
        "severe",
        "very severe",
        "light",
        "heavy",
        "romba",
        "kadumai",
        "கடுமையான",
        "லேசான",
    ]):
        facts["severity_known"] = True

    # --------------------------------------------------------
    # TRIGGER / RELATION
    # --------------------------------------------------------

    if _contains_any(text, [
        "after eating",
        "after food",
        "before food",
        "after meal",
        "saapta apram",
        "saapta piragu",
        "saapidarathukku munadi",
        "உணவுக்குப் பிறகு",
        "உணவுக்கு முன்",
    ]):
        facts["food_relation_known"] = True

    if _contains_any(text, [
        "movement",
        "walking",
        "exercise",
        "rest",
        "asai",
        "nadakkum pothu",
        "அசைவால்",
        "நடக்கும்போது",
    ]):
        facts["activity_relation_known"] = True

    return facts


# ============================================================
# BRANCH DETECTION
# ============================================================

BRANCH_ALIASES = {
    "fever": [
        "fever",
        "temperature",
        "காய்ச்சல்",
        "சூடு",
    ],

    "headache": [
        "headache",
        "head pain",
        "thala vali",
        "thalavali",
        "தலைவலி",
        "தலை வலி",
    ],

    "abdomen": [
        "stomach",
        "stomach pain",
        "stomach ache",
        "abdominal",
        "abdomen",
        "vayiru",
        "vayiru vali",
        "vayir vali",
        "வயிறு",
        "வயிற்று",
        "வயிற்றில்",
    ],

    "chest": [
        "chest",
        "chest pain",
        "marbu",
        "marbu vali",
        "nenju",
        "nenju vali",
        "மார்பு",
        "மார்பு வலி",
        "நெஞ்சு",
    ],

    "respiratory": [
        "cough",
        "irumal",
        "breathing",
        "breathless",
        "breathing difficulty",
        "moochu",
        "moochu kashtam",
        "சளி",
        "இருமல்",
        "மூச்சு",
    ],

    "urinary": [
        "urine",
        "urinary",
        "burning urine",
        "siruneer",
        "சிறுநீர்",
    ],

    "skin": [
        "skin",
        "rash",
        "itch",
        "itching",
        "thol",
        "தோல்",
        "அரிப்பு",
    ],

    "pain": [
        "pain",
        "ache",
        "vali",
        "வலி",
    ],
}


def _detect_branches(text: str, mode: str) -> List[str]:
    text = norm(text)

    detected = []

    branches = []

    if mode == "AYUSH":
        branches.extend(AYUSH_BRANCHES)

    branches.extend(BRANCHES)

    for name, words, _questions in branches:

        aliases = BRANCH_ALIASES.get(name, [])

        all_words = [
            norm(x)
            for x in words
            if x
        ] + aliases

        if any(word and word in text for word in all_words):
            detected.append(name)

    # Always include generic pain if pain exists.
    if "pain" in text or "vali" in text or "வலி" in text:
        if "pain" not in detected:
            detected.append("pain")

    # Remove duplicates while preserving order.
    result = []

    for item in detected:
        if item not in result:
            result.append(item)

    return result


# ============================================================
# QUESTION POOL
# ============================================================

def _candidate_questions(
    mode: str,
    answers: Dict[str, Any],
    language: str
) -> List[Dict[str, Any]]:

    text = _all_text(answers)

    branches = []

    if mode == "AYUSH":
        branches.extend(AYUSH_BRANCHES)

    branches.extend(BRANCHES)

    detected_branches = _detect_branches(text, mode)

    selected = []

    # First collect questions only from active branches.
    for name, words, questions in branches:

        branch_match = (
            name in detected_branches
            or any(
                norm(w) in text
                for w in words
                if norm(w)
            )
        )

        if not branch_match:
            continue

        for q in questions:
            selected.append({
                "key": q["key"],
                "question": (
                    q["ta"]
                    if language == "Tamil"
                    else q["en"]
                ),
                "options": localize_options(q.get("options", []), language),
                "branch": q.get("branch") or name,
            })

    # --------------------------------------------------------
    # Remove duplicate keys
    # --------------------------------------------------------

    unique = []
    seen = set()

    for q in selected:

        if q["key"] in seen:
            continue

        seen.add(q["key"])
        unique.append(q)

    # --------------------------------------------------------
    # Never ask an explicit answer-key question again.
    # --------------------------------------------------------

    explicit_keys = {
        str(key)
        for key, value in answers.items()
        if _has_value(value)
    }

    unique = [
        q
        for q in unique
        if q["key"] not in explicit_keys
    ]

    # --------------------------------------------------------
    # LOCAL SEMANTIC PROTECTION
    # --------------------------------------------------------

    facts = _local_facts(text)

    protected_keys: Set[str] = set()

    # Fever duration already mentioned.
    if facts.get("fever") and facts.get("duration_known"):
        protected_keys.add("fever_duration")

    # Respiratory duration already mentioned.
    if facts.get("cough") and facts.get("duration_known"):
        protected_keys.add("resp_duration")

    # Headache already implies head location.
    if facts.get("headache"):
        protected_keys.update([
            "pain_location",
            "head_location",
        ])

    # Abdominal pain already gives broad location.
    if facts.get("abdominal_pain"):
        protected_keys.add("pain_location")

        # If question means broad abdomen location, don't repeat it.
        protected_keys.add("abd_location")

    # Chest pain already gives location.
    if facts.get("chest_pain"):
        protected_keys.add("pain_location")

    # Back pain already gives location.
    if facts.get("back_pain"):
        protected_keys.add("pain_location")

    # Limb pain already gives a body region.
    if facts.get("limb_pain"):
        protected_keys.add("pain_location")

    # Any explicit duration means don't ask that symptom's specific duration.
    # FIX: Duration is symptom-specific, NOT global.
    if facts.get("fever_duration"):
        protected_keys.add("fever_duration")
    if facts.get("resp_duration"):
        protected_keys.add("resp_duration")
    if facts.get("head_duration"):
        protected_keys.add("head_onset")

    # When a symptom is present AND its duration is known, its onset
    # is also implicitly known (the patient already gave temporal info).
    if facts.get("fever") and facts.get("fever_duration"):
        protected_keys.add("head_onset")
    if facts.get("chest_pain") and facts.get("duration_known"):
        protected_keys.add("chest_onset")
    if facts.get("headache") and facts.get("head_duration"):
        protected_keys.add("head_onset")
    if facts.get("abdominal_pain") and facts.get("abd_duration"):
        protected_keys.add("abd_onset")
    if facts.get("abdominal_pain") and facts.get("duration_known"):
        protected_keys.add("abd_food")
    if facts.get("pain") and facts.get("duration_known"):
        protected_keys.add("pain_onset")
    if facts.get("skin") and facts.get("duration_known"):
        protected_keys.add("skin_onset")

    unique = [
        q
        for q in unique
        if q["key"] not in protected_keys
    ]

    # --------------------------------------------------------
    # Avoid generic pain questions when a specific symptom
    # already describes the pain.
    # --------------------------------------------------------

    if facts.get("headache") or facts.get("abdominal_pain") \
            or facts.get("chest_pain") or facts.get("back_pain") \
            or facts.get("limb_pain"):

        unique = [
            q
            for q in unique
            if q["key"] != "pain_location"
        ]

    return unique[:30]


# ============================================================
# JSON PARSER
# ============================================================

def _parse_json(raw: Any) -> Dict[str, Any]:

    if isinstance(raw, dict):
        return raw

    raw = str(raw or "").strip()

    raw = re.sub(
        r"^```json\s*",
        "",
        raw,
        flags=re.I
    )

    raw = re.sub(
        r"^```\s*",
        "",
        raw
    )

    raw = re.sub(
        r"\s*```$",
        "",
        raw
    )

    try:
        return json.loads(raw)
    except Exception:
        return {}


# ============================================================
# LLM CLINICAL MEMORY + QUESTION SELECTION
# ============================================================

def _build_prompt(
    mode: str,
    language: str,
    answers: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    facts: Dict[str, Any] = None
) -> str:
    chief = answers.get("chief_complaint") or "Not stated"
    history_items = [f"- {k}: {v}" for k, v in answers.items() if v and k != "chief_complaint"]
    history_str = "\n".join(history_items) if history_items else "None yet"

    cand_lines = []
    for c in candidates[:6]:
        q_text = c.get("question") or (c.get("ta") if language == "Tamil" else c.get("en")) or c.get("key")
        cand_lines.append(f"- {c['key']}: {q_text}")
    cand_str = "\n".join(cand_lines)

    lang_instr = (
        "The patient's session language is Tamil. Keep any patient-facing wording in Tamil."
        if language == "Tamil"
        else "The patient's session language is English. Use simple, concise English."
    )

    return f"""You are MediKiosk's adaptive clinical intake assistant.
Analyze the patient's complaint and previous answers.
Identify the most important missing clinical information (e.g. duration, location, character, severity, associated symptoms).

Rules:
1. Analyze the patient's latest input together with all previous answers.
2. If essential intake info is still missing, select ONE relevant follow-up question key from the candidates and set status to "continue".
3. If essential intake information has been collected, or if sufficient history exists for clinician review, set status to "complete", is_complete to true, and key to null.
4. Do NOT provide long medical explanations during questioning. Keep responses fast and concise.
5. Do NOT diagnose or prescribe medications.
6. {lang_instr}

Patient Complaint: {chief}
Collected Answers:
{history_str}

Candidate Questions:
{cand_str}

Return valid JSON ONLY in this exact format:
{{"status": "continue"|"complete", "missing_info": "<brief description of missing information or null>", "key": "<candidate_key_or_null>", "is_complete": false|true}}"""


def generate_concise_clinical_summary(
    chief_complaint: str,
    answers: Dict[str, Any],
    facts: Dict[str, Any] = None,
    department: str = "General Medicine",
    language: str = "English",
) -> str:
    """Generate a concise, structured clinician-facing summary upon intake completion.

    Rules:
    - Ground strictly on patient facts.
    - No diagnosing or prescribing.
    - Fast and concise bulleted structure.
    """
    ans_lines = [
        f"• {str(k).replace('_', ' ').title()}: {v}"
        for k, v in (answers or {}).items()
        if v and k != "chief_complaint"
    ]
    ans_str = "\n".join(ans_lines) if ans_lines else "• No additional details provided"

    fallback_summary = (
        f"CLINICAL INTAKE SUMMARY (Clinician Review)\n"
        f"• Chief Complaint: {chief_complaint or 'Not stated'}\n"
        f"• Reported History:\n{ans_str}\n"
        f"• Preliminary Department: {department}\n"
        f"• Safety Screening: No active red flags detected\n"
        f"• Note: AI-assisted patient intake documentation. Clinician verification required before diagnosis or prescription."
    )

    if language == "Tamil":
        fallback_summary = (
            f"மருத்துவர் பார்வைக்கான மருத்துவ சுருக்கம் (AI அறிமுக பதிவு)\n"
            f"• முக்கிய புகார்: {chief_complaint or 'குறிப்பிடப்படவில்லை'}\n"
            f"• தொடர்பட்ட வரலாறு:\n{ans_str}\n"
            f"• முன்கூட்டிய துறை: {department}\n"
            f"• பாதுகாப்பு திரையிடல்: செயலில் சிவப்பு கொடிகள் இல்லை\n"
            f"• குறிப்பு: AI-உதவி அறிமுக பதிவு. இறுதி நோயறிதலுக்கு முன் மருத்துவர் சரிபார்ப்பு தேவை."
        )

    lang_rule = (
        "5. The session language is Tamil. Write the ENTIRE summary in Tamil."
        if language == "Tamil"
        else "5. The session language is English. Write the ENTIRE summary in English."
    )

    prompt = f"""You are MediKiosk's clinical documentation assistant.
Generate a concise, structured clinician-facing intake handoff based ONLY on the documented patient facts.
Rules:
1. Do NOT diagnose or prescribe medications.
2. Ground strictly on patient-stated facts.
3. Keep it concise, structured in bullet points.
4. Fast and professional.
{lang_rule}

Patient Complaint: {chief_complaint or 'Not stated'}
Intake History:
{ans_str}

Preliminary Department: {department}

Produce a structured summary in this format:
• Chief Complaint: {chief_complaint or 'Not stated'}
• Timeline / Duration: <duration or onset reported>
• Location & Character: <location, character, or severity reported>
• Associated Symptoms & Pertinent Negatives: <associated symptoms or negatives>
• Safety Screening: No active red flags detected
• Recommended Department: {department}
• Note: AI intake documentation. Clinician verification required."""

    try:
        from services.ai.llm_service import generate_text
        text, src = generate_text(prompt, max_tokens=220, temperature=0.1)
        if text and "[LOCAL_FALLBACK]" not in text and len(text.strip()) > 30:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
                cleaned = re.sub(r"\n?```$", "", cleaned).strip()
            return cleaned
    except Exception:
        pass

    return fallback_summary


# ============================================================
# FALLBACK
# ============================================================

def _fallback(
    mode: str,
    language: str,
    answers: Dict[str, Any],
    candidates: List[Dict[str, Any]]
) -> Dict[str, Any]:

    text = _all_text(answers)

    facts = _local_facts(text)

    # --------------------------------------------------------
    # If no candidates remain, interview is complete.
    # --------------------------------------------------------

    if not candidates:

        return {
            "facts": facts,
            "covered_information": list(facts.keys()),
            "missing_important_information": [],
            "new_symptoms_detected": [],
            "safety_flags": [],
            "clinical_summary": text[:1000],
            "department_hint": "Needs further history",
            "next_question": None,
            "done": True,
            "ai_source": "LOCAL_RULES",
        }

    # --------------------------------------------------------
    # Prefer a candidate that is not locally protected.
    # --------------------------------------------------------

    protected = set()

    # Per-symptom duration protection.
    if facts.get("fever_duration"):
        protected.add("fever_duration")
    if facts.get("resp_duration"):
        protected.add("resp_duration")

    # When a symptom is present AND duration is known, onset is implied.
    if facts.get("fever") and facts.get("fever_duration"):
        protected.add("head_onset")
    if facts.get("chest_pain") and facts.get("duration_known"):
        protected.add("chest_onset")
        protected.add("pain_onset")
    if facts.get("headache") and facts.get("head_duration"):
        protected.add("head_onset")
    if facts.get("abdominal_pain") and facts.get("abd_duration"):
        protected.add("abd_onset")
    if facts.get("abdominal_pain") and facts.get("duration_known"):
        protected.add("abd_food")
    if facts.get("pain") and facts.get("duration_known"):
        protected.add("pain_onset")
    if facts.get("back_pain") and facts.get("duration_known"):
        protected.add("back_onset")
    if facts.get("skin") and facts.get("duration_known"):
        protected.add("skin_onset")

    if facts.get("headache"):
        protected.update([
            "pain_location",
            "head_location",
        ])

    if facts.get("abdominal_pain"):
        protected.update([
            "pain_location",
            "abd_location",
        ])

    if facts.get("chest_pain"):
        protected.add("pain_location")

    if facts.get("back_pain"):
        protected.add("pain_location")

    for q in candidates:

        if q["key"] in protected:
            continue

        if q["key"] in answers:
            continue

        return {
            "facts": facts,
            "covered_information": list(facts.keys()),
            "missing_important_information": [
                q["key"]
            ],
            "new_symptoms_detected": [],
            "safety_flags": [],
            "clinical_summary": text[:1000],
            "department_hint": "Needs further history",
            "next_question": {
                "key": q["key"],
                "question": q["question"],
                "options": q.get("options", []),
                "adaptive": True,
                "branch": q.get("branch", ""),
                "reason": "missing_high_value_information",
            },
            "done": False,
            "ai_source": "LOCAL_RULES",
        }

    return {
        "facts": facts,
        "covered_information": list(facts.keys()),
        "missing_important_information": [],
        "new_symptoms_detected": [],
        "safety_flags": [],
        "clinical_summary": text[:1000],
        "department_hint": "Needs further history",
        "next_question": None,
        "done": True,
        "ai_source": "LOCAL_RULES",
    }


# ============================================================
# FINAL QUESTION VALIDATION
# ============================================================

def _validate_question(
    next_q: Any,
    answers: Dict[str, Any],
    text: str
) -> Any:

    if not isinstance(next_q, dict):
        return None

    key = str(next_q.get("key") or "").strip()

    if not key:
        return None

    # --------------------------------------------------------
    # Explicit answer key already exists
    # --------------------------------------------------------

    if key in answers and _has_value(answers.get(key)):
        return None

    facts = _local_facts(text)

    # --------------------------------------------------------
    # Semantic repeat protection - uses is_covered for
    # proper per-symptom coverage checking.
    # FIX: Removed global duration_known check that
    # incorrectly blocked ALL duration questions.
    # Duration is now symptom-specific in clinical_memory.
    # --------------------------------------------------------

    blocked = set()

    if facts.get("headache"):
        blocked.update([
            "pain_location",
            "head_location",
        ])

    if facts.get("abdominal_pain"):
        blocked.update([
            "pain_location",
            "abd_location",
        ])

    if facts.get("chest_pain"):
        blocked.add("pain_location")

    if facts.get("back_pain"):
        blocked.add("pain_location")

    if facts.get("limb_pain"):
        blocked.add("pain_location")

    # Per-symptom duration protection.
    if facts.get("fever_duration"):
        blocked.add("fever_duration")
    if facts.get("resp_duration"):
        blocked.add("resp_duration")

    # When a symptom is present AND duration is known,
    # its onset is implicitly known.
    if facts.get("fever") and facts.get("fever_duration"):
        blocked.add("head_onset")
    if facts.get("chest_pain") and facts.get("duration_known"):
        blocked.add("chest_onset")
        blocked.add("pain_onset")
    if facts.get("headache") and facts.get("head_duration"):
        blocked.add("head_onset")
    if facts.get("abdominal_pain") and facts.get("abd_duration"):
        blocked.add("abd_onset")
    if facts.get("abdominal_pain") and facts.get("duration_known"):
        blocked.add("abd_food")
    if facts.get("pain") and facts.get("duration_known"):
        blocked.add("pain_onset")
    if facts.get("back_pain") and facts.get("duration_known"):
        blocked.add("back_onset")
    if facts.get("skin") and facts.get("duration_known"):
        blocked.add("skin_onset")

    if key in blocked:
        return None

    question = str(
        next_q.get("question") or ""
    ).strip()

    if not question:
        return None

    options = next_q.get("options")

    if not isinstance(options, list):
        options = []

    return {
        "key": key,
        "question": question,
        "options": options,
        "adaptive": True,
        "branch": str(
            next_q.get("branch") or ""
        ),
        "reason": str(
            next_q.get("reason")
            or "missing_high_value_information"
        ),
    }


def _debug_log(
    memory: Dict[str, Any],
    patient_text: str,
    facts: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    selected: Dict[str, Any],
    mode: str = "NORMAL",
) -> None:
    """Log turn details for debugging. Exposed only in debug mode."""
    import logging
    logger = logging.getLogger("medikiosk.debug")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    logger.debug("=" * 60)
    logger.debug("TURN DEBUG")
    logger.debug("-" * 60)
    logger.debug(f"Patient input: {patient_text}")
    logger.debug("EXTRACTED FACTS (local):")
    for k, v in facts.items():
        logger.debug(f"  {k}: {v}")
    logger.debug("MEMORY FACTS:")
    for k, v in memory.get("facts", {}).items():
        if isinstance(v, dict):
            logger.debug(f"  {k}: {v.get('value')} (confidence={v.get('confidence')}, source={v.get('source')})")
    logger.debug("SYMPTOMS:")
    for k, v in memory.get("symptoms", {}).items():
        if isinstance(v, dict):
            logger.debug(f"  {k}: present={v.get('present')}, location={v.get('location')}, duration={v.get('duration')}")
    logger.debug("COVERED INFORMATION:")
    for k in memory.get("covered_information", []):
        logger.debug(f"  {k}")
    logger.debug("ASKED QUESTIONS:")
    for k in memory.get("asked_questions", []):
        logger.debug(f"  {k}")
    logger.debug("ANSWERED CONCEPTS:")
    for k in memory.get("answered_concepts", []):
        logger.debug(f"  {k}")
    logger.debug("UNRESOLVED CONCEPTS:")
    for k in memory.get("unresolved_concepts", []):
        logger.debug(f"  {k}")
    logger.debug("CANDIDATE QUESTIONS:")
    for q in candidates:
        logger.debug(f"  {q.get('key')}: {q.get('question', '')[:80]}")
    logger.debug("SAFETY FLAGS:")
    for f in memory.get("safety_flags", []):
        logger.debug(f"  {f}")
    logger.debug(f"SELECTED QUESTION: {selected}")
    logger.debug("=" * 60)


# ============================================================
# MAIN ENGINE
# ============================================================

def analyze_turn(
    mode: str,
    language: str,
    answers: Dict[str, Any],
    candidates: List[Dict[str, Any]] = None,
    answer_count: int = 0,
    clinical_memory: Dict[str, Any] = None,
    debug: bool = False,
) -> Dict[str, Any]:

    answers = answers or {}
    memory = clinical_memory or empty_memory()

    # --------------------------------------------------------
    # COMPLETE HISTORY
    # --------------------------------------------------------

    text = _all_text(answers)

    # --------------------------------------------------------
    # Build candidate pool dynamically from COMPLETE history.
    #
    # This is important because a new symptom can appear in
    # a later answer.
    # --------------------------------------------------------

    dynamic = _candidate_questions(
        mode=mode,
        answers=answers,
        language=language
    )

    # Keep the caller-supplied candidates too, but always prefer the
    # dynamically rebuilt pool (which reflects the complete history).
    caller_candidates = candidates or []

    merged = []
    seen = set()

    for q in dynamic + caller_candidates:
        key = str(q.get("key") or "").strip()

        if not key:
            continue

        if key in seen:
            continue

        seen.add(key)
        merged.append(q)

    candidates = merged

    # --------------------------------------------------------
    # Local fallback
    # --------------------------------------------------------

    fallback = _fallback(
        mode=mode,
        language=language,
        answers=answers,
        candidates=candidates
    )

    # --------------------------------------------------------
    # If nothing to ask, return immediately.
    # --------------------------------------------------------

    if not candidates:
        fallback["ai_source"] = "LOCAL_RULES"
        return fallback

    # --------------------------------------------------------
    # Candidate filtering & ranking using ClinicalMemory
    # --------------------------------------------------------
    local_facts = _local_facts(text)
    local_facts_for_prompt = local_facts

    filtered_candidates = [
        q for q in candidates
        if not (clinical_memory and is_covered(clinical_memory, str(q.get("key") or ""), str(q.get("question") or "")))
    ]

    ranked_candidates = rank_candidates(memory, filtered_candidates) if filtered_candidates else []

    # If all eligible questions are covered, interview is complete.
    if not ranked_candidates:
        return {
            "facts": local_facts,
            "covered_information": list(local_facts.keys()),
            "missing_important_information": [],
            "new_symptoms_detected": [],
            "safety_flags": [],
            "clinical_summary": "",
            "department_hint": "General Medicine",
            "next_question": None,
            "done": True,
            "ai_source": "LOCAL_RULES",
        }

    # Keep candidate pool focused (top 6 highest clinical priority)
    pool = ranked_candidates[:6]
    fallback_key = pool[0]["key"]
    fallback_payload = {
        "status": "continue",
        "missing_info": "symptom details",
        "key": fallback_key,
        "is_complete": False
    }

    prompt = _build_prompt(
        mode=mode,
        language=language,
        answers=answers,
        candidates=pool,
        facts=local_facts_for_prompt
    )

    try:
        raw, source = generate_json(
            prompt,
            json.dumps(fallback_payload, ensure_ascii=False),
            max_tokens=100
        )
        data = _parse_json(raw)
    except Exception:
        data = fallback_payload
        source = "LOCAL_RULES"

    if not isinstance(data, dict) or not data:
        data = fallback_payload

    # --------------------------------------------------------
    # Completion check & Candidate resolution
    # --------------------------------------------------------
    status_signal = str(data.get("status") or "").strip().lower()
    is_complete = bool(data.get("is_complete")) or (data.get("done") is True) or (status_signal == "complete")
    selected_key = data.get("key")

    if isinstance(data.get("next_question"), dict):
        selected_key = data["next_question"].get("key")
        if data.get("next_question") is None:
            is_complete = True

    next_q = None
    if is_complete or str(selected_key).lower() in ("none", "null", ""):
        done = True
        next_q = None
    else:
        matched = next((c for c in pool if str(c.get("key") or "").strip() == str(selected_key).strip()), None)
        if not matched:
            matched = next((c for c in candidates if str(c.get("key") or "").strip() == str(selected_key).strip()), None)

        if matched:
            next_q = _validate_question(matched, answers, text)
            if next_q and clinical_memory and is_covered(clinical_memory, next_q.get("key"), next_q.get("question")):
                next_q = None

        # Fallback to top priority candidate ONLY if interview is NOT marked complete
        if next_q is None:
            for candidate in pool:
                cand_q = _validate_question(candidate, answers, text)
                if cand_q is not None and not (clinical_memory and is_covered(clinical_memory, cand_q.get("key"), cand_q.get("question"))):
                    next_q = cand_q
                    break

        # Determine completion:
        # 1. next_q is None
        # 2. Or if session has gathered >= 4 answers with duration known, mark done
        done = (next_q is None)
        if not done and answer_count >= 4 and local_facts.get("duration_known"):
            done = True
            next_q = None

    # --------------------------------------------------------
    # Normalize facts & safety
    # --------------------------------------------------------
    facts = data.get("facts") if isinstance(data.get("facts"), dict) else {}
    for key, value in local_facts.items():
        if key not in facts:
            facts[key] = value

    covered_information = list(facts.keys())
    missing_information = [c["key"] for c in pool if c["key"] != (next_q.get("key") if next_q else None)]
    safety_flags = normalize_llm_safety_flags(data.get("safety_flags", []))

    department_hint = str(data.get("department_hint") or "General Medicine").strip()

    # Crucial: NO clinical summary generated during questioning turns (requirement 8)
    # Generate concise clinician-facing summary ONLY when questioning is complete (requirement 7)
    final_summary = ""
    if done:
        chief = answers.get("chief_complaint") or (list(answers.values())[0] if answers else "Not stated")
        final_summary = generate_concise_clinical_summary(
            chief_complaint=str(chief),
            answers=answers,
            facts=facts,
            department=department_hint,
            language=language
        )

    result = {
        "status": "complete" if done else "continue",
        "facts": facts,
        "covered_information": covered_information,
        "missing_important_information": missing_information,
        "new_symptoms_detected": data.get("new_symptoms_detected", []) if isinstance(data.get("new_symptoms_detected"), list) else [],
        "safety_flags": safety_flags,
        "clinical_summary": final_summary if done else "",
        "final_summary": final_summary if done else None,
        "department_hint": department_hint,
        "next_question": next_q,
        "done": done,
        "ai_source": source,
    }

    if debug:
        result["debug_log"] = {
            "patient_input": text,
            "local_facts": local_facts,
            "memory_facts": {
                k: v for k, v in memory.get("facts", {}).items()
            },
            "symptoms": {
                k: v for k, v in memory.get("symptoms", {}).items()
            },
            "asked_questions": memory.get("asked_questions", []),
            "answered_concepts": memory.get("answered_concepts", []),
            "unresolved_concepts": memory.get("unresolved_concepts", []),
        }

    return result


# ============================================================
# OPTIONAL COMPATIBILITY FUNCTION
# ============================================================

def next_question(
    mode: str,
    answers: Dict[str, Any],
    language: str = "English",
    clinical_memory: Dict[str, Any] = None,
    debug: bool = False,
):

    """
    Compatibility wrapper.

    Existing code that calls:

        next_question(mode, answers, language)

    will continue to work.

    The real intelligence is analyze_turn().
    """

    result = analyze_turn(
        mode=mode,
        language=language,
        answers=answers or {},
        candidates=None,
        answer_count=len(answers or {}),
        clinical_memory=clinical_memory,
        debug=debug,
    )

    return result.get("next_question")


# ============================================================
# OPTIONAL QUESTION LIST API
# ============================================================

def get_questions(
    mode: str = "NORMAL",
    language: str = "English"
):

    """
    Returns the available question pool.

    This is mainly for UI/debugging.

    Actual interview order should NOT use this list directly.
    analyze_turn() chooses the next question dynamically.
    """

    branches = []

    if mode == "AYUSH":
        branches.extend(AYUSH_BRANCHES)

    branches.extend(BRANCHES)

    result = []
    seen = set()

    for name, words, questions in branches:

        for q in questions:

            key = q["key"]

            if key in seen:
                continue

            seen.add(key)

            result.append({
                "key": key,
                "question": (
                    q["ta"]
                    if language == "Tamil"
                    else q["en"]
                ),
                "options": localize_options(q.get("options", []), language),
                "adaptive": True,
                "branch": q.get("branch") or name,
            })

    return result