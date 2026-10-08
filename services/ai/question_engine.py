import re

from utils.constants import NORMAL_SECTIONS, AYUSH_SECTIONS, NORMAL_TA, AYUSH_TA


def norm(s):
    return re.sub(r'\s+', ' ', str(s or '').strip().lower())


def covered(v):
    return bool(str(v or '').strip())


def _q(key, en, ta, options=None, branch=''):
    return {
        'key': key,
        'en': en,
        'ta': ta,
        'options': options or [],
        'branch': branch
    }


# English equivalents for the Tamil option lists authored in
# BRANCHES / AYUSH_BRANCHES. English sessions must never see
# Tamil touch options (session-language requirement).
OPTION_EN = {
    '1–2 நாட்கள்': '1–2 days',
    '3–5 நாட்கள்': '3–5 days',
    '1 வாரத்துக்கு மேல்': 'More than 1 week',
    '1 வாரத்துக்குள்': 'Within 1 week',
    '1–3 வாரங்கள்': '1–3 weeks',
    '3 வாரங்களுக்கு மேல்': 'More than 3 weeks',
    'தெரியவில்லை': "Don't know",
    'தொடர்ந்து': 'Continuous',
    'வந்து போகிறது': 'Comes and goes',
    'ஆம்': 'Yes',
    'இல்லை': 'No',
    'சில அறிகுறிகள் உள்ளன': 'Some symptoms present',
    'திடீரென': 'Suddenly',
    'மெதுவாக': 'Gradually',
    'அழுத்தம்': 'Pressure',
    'இறுக்கம்': 'Tightness',
    'எரிச்சல்': 'Burning',
    'வலி': 'Pain',
    'சில நேரங்களில்': 'Sometimes',
    'சளி இல்லை': 'No phlegm',
    'வெள்ளை': 'White',
    'மஞ்சள்/பச்சை': 'Yellow/Green',
    'ரத்தம் கலந்தது': 'Mixed with blood',
    'ஓய்வில்': 'At rest',
    'வேலையில்/நடப்பில்': 'With activity',
    'இரண்டிலும்': 'Both',
    'ஒரு பக்கம்': 'One side',
    'இருபக்கம்': 'Both sides',
    'நெற்றி': 'Forehead',
    'பின்பக்கம்': 'Back of head',
    'கண்களைச் சுற்றி': 'Around the eyes',
    'மேல் பகுதி': 'Upper part',
    'கீழ் பகுதி': 'Lower part',
    'வலது பக்கம்': 'Right side',
    'இடது பக்கம்': 'Left side',
    'முழுவதும்': 'All over',
    'நல்லதாகிறது': 'Getting better',
    'மோசமாகிறது': 'Getting worse',
    'அதேபோல்': 'Same',
    'உணவுக்குப் பிறகு': 'After food',
    'உணவுக்கு முன்': 'Before food',
    'மலம் கழித்த பிறகு': 'After bowel movement',
    'தொடர்பு இல்லை': 'No relation',
    'பரவுகிறது': 'Spreading',
    'குறைந்து வருகிறது': 'Reducing',
    'சில உள்ளது': 'Some present',
    'தலை': 'Head',
    'மார்பு': 'Chest',
    'வயிறு': 'Stomach',
    'முதுகு': 'Back',
    'மூட்டு/கால்': 'Joint/Leg',
    'வேறு இடம்': 'Other place',
    'அசைவு': 'Movement',
    'உணவு': 'Food',
    'ஓய்வு': 'Rest',
    'வேறு காரணம்': 'Other reason',
    'சில அளவு': 'Somewhat',
    'தெரியும்': 'Known',
    'பொருந்தாது': 'Not applicable',
    'குறைந்துள்ளது': 'Reduced',
    'அதிகரித்துள்ளது': 'Increased',
    'மாறவில்லை': 'No change',
    'செயல்பாடு': 'Activity',
    'தூக்கம்': 'Sleep',
    'பருவநிலை': 'Season',
    'மாற்றம் உள்ளது': 'Change present',
    'மாற்றம் இல்லை': 'No change',
}


def localize_options(options, language='English'):
    """Return touch options in the session language.

    Option lists are authored in Tamil; Tamil sessions keep them as-is,
    English sessions get the OPTION_EN translation. Unknown strings pass
    through unchanged so no option is ever dropped. Returns a new list
    (never mutates the shared branch data).
    """
    if not options or language == 'Tamil':
        return list(options or [])
    return [OPTION_EN.get(str(o), str(o)) for o in options]


BRANCHES = [

    ('fever', [
        'fever', 'temperature', 'காய்ச்சல்', 'சூடு',
        'kaichal', 'kaichchal', 'joram'
    ], [

        _q(
            'fever_duration',
            'How many days have you had the fever?',
            'காய்ச்சல் எத்தனை நாட்களாக உள்ளது?',
            ['1–2 நாட்கள்', '3–5 நாட்கள்', '1 வாரத்துக்கு மேல்', 'தெரியவில்லை'],
            'fever'
        ),

        _q(
            'fever_pattern',
            'Does the fever stay constant or come and go?',
            'காய்ச்சல் தொடர்ந்து இருக்கிறதா அல்லது வந்து போகிறதா?',
            ['தொடர்ந்து', 'வந்து போகிறது', 'தெரியவில்லை'],
            'fever'
        ),

        _q(
            'fever_associated',
            'Along with the fever, do you have chills, body pain, cough, vomiting or loose stools?',
            'காய்ச்சலுடன் குளிர்ச்சல், உடல் வலி, இருமல், வாந்தி அல்லது வயிற்றுப்போக்கு இருக்கிறதா?',
            ['ஆம்', 'இல்லை', 'சில அறிகுறிகள் உள்ளன'],
            'fever'
        ),

        _q(
            'fever_exposure',
            'Have you travelled recently or been around someone with a similar illness?',
            'சமீபத்தில் பயணம் செய்தீர்களா அல்லது இதே போன்ற உடல்நலப் பிரச்சனை உள்ளவருடன் இருந்தீர்களா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'fever'
        )
    ]),

    ('chest', [
        'chest', 'heart', 'மார்பு', 'இதயம்',
        'படபடப்பு', 'marbu', 'marbu vali', 'nenju vali'
    ], [

        _q(
            'chest_onset',
            'When did the chest problem start, and did it begin suddenly or gradually?',
            'மார்பு பிரச்சனை எப்போது தொடங்கியது? திடீரெனவா அல்லது மெதுவாகவா தொடங்கியது?',
            ['திடீரென', 'மெதுவாக', 'தெரியவில்லை'],
            'chest'
        ),

        _q(
            'chest_character',
            'How would you describe it: pressure, tightness, burning, or pain?',
            'இது அழுத்தம், இறுக்கம், எரிச்சல் அல்லது வலி போல உள்ளதா?',
            ['அழுத்தம்', 'இறுக்கம்', 'எரிச்சல்', 'வலி', 'தெரியவில்லை'],
            'chest'
        ),

        _q(
            'chest_spread',
            'Does it spread to the arm, shoulder, back, neck or jaw?',
            'அசௌகரியம் கை, தோள், முதுகு, கழுத்து அல்லது தாடைக்கு பரவுகிறதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'chest'
        ),

        _q(
            'chest_associated',
            'Do you have sweating, dizziness, nausea or unusual tiredness with it?',
            'இதனுடன் வியர்வை, மயக்கம், வாந்தி உணர்வு அல்லது வழக்கத்திற்கு மாறான சோர்வு உள்ளதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'chest'
        ),

        _q(
            'chest_breathing',
            'Are you having difficulty breathing with it?',
            'இதனுடன் மூச்சுத்திணறல் அல்லது மூச்சு விடுவதில் சிரமம் உள்ளதா?',
            ['ஆம்', 'இல்லை', 'சில நேரங்களில்'],
            'chest'
        )
    ]),

    ('respiratory', [
        'cough', 'breathing', 'breathless', 'wheeze',
        'இருமல்', 'மூச்சு', 'சளி',
        'irumal', 'moochu', 'moochu kashtam'
    ], [

        _q(
            'resp_duration',
            'How long have you had the cough or breathing problem?',
            'இருமல் அல்லது மூச்சுப் பிரச்சனை எத்தனை நாட்களாக உள்ளது?',
            ['1 வாரத்துக்குள்', '1–3 வாரங்கள்', '3 வாரங்களுக்கு மேல்', 'தெரியவில்லை'],
            'respiratory'
        ),

        _q(
            'resp_sputum',
            'Is there phlegm? If yes, what is it like?',
            'சளி இருக்கிறதா? இருந்தால் அது எப்படி உள்ளது?',
            ['சளி இல்லை', 'வெள்ளை', 'மஞ்சள்/பச்சை', 'ரத்தம் கலந்தது', 'தெரியவில்லை'],
            'respiratory'
        ),

        _q(
            'resp_breathing',
            'Do you become breathless at rest or during activity?',
            'ஓய்விலா அல்லது வேலை/நடப்பில் மூச்சுத்திணறல் ஏற்படுகிறதா?',
            ['ஓய்வில்', 'வேலையில்/நடப்பில்', 'இரண்டிலும்', 'இல்லை'],
            'respiratory'
        ),

        _q(
            'resp_wheeze',
            'Do you hear wheezing or have chest tightness?',
            'மூச்சில் சத்தம் அல்லது மார்பு இறுக்கம் உள்ளதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'respiratory'
        )
    ]),

    ('headache', [
        'headache', 'migraine', 'தலைவலி',
        'thala vali', 'thalavali', 'thalaivali'
    ], [

        _q(
            'head_onset',
            'When did the headache begin? Was it sudden or gradual?',
            'தலைவலி எப்போது தொடங்கியது? திடீரெனவா அல்லது மெதுவாகவா தொடங்கியது?',
            ['திடீரென', 'மெதுவாக', 'தெரியவில்லை'],
            'headache'
        ),

        _q(
            'head_location',
            'Where is the pain: one side, both sides, forehead, back of head, or around the eyes?',
            'வலி எங்கு உள்ளது: ஒரு பக்கம், இருபக்கம், நெற்றி, தலையின் பின்பக்கம் அல்லது கண்களைச் சுற்றியா?',
            ['ஒரு பக்கம்', 'இருபக்கம்', 'நெற்றி', 'பின்பக்கம்', 'கண்களைச் சுற்றி'],
            'headache'
        ),

        _q(
            'head_neuro',
            'Do you have weakness, numbness, speech difficulty, fainting or vision change?',
            'பலவீனம், உணர்வின்மை, பேசுவதில் சிரமம், மயக்கம் அல்லது பார்வை மாற்றம் உள்ளதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'headache'
        ),

        _q(
            'head_associated',
            'Do you have vomiting, fever or sensitivity to light?',
            'வாந்தி, காய்ச்சல் அல்லது வெளிச்சத்தை பொறுக்க முடியாமை உள்ளதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'headache'
        )
    ]),

    ('abdomen', [
        'stomach', 'abdominal', 'abdomen', 'gas', 'acidity',
        'வயிறு', 'வயிற்று', 'அமிலம்',
        'vayiru', 'vayiru vali', 'vayithu', 'vayithula'
    ], [

        _q(
            'abd_location',
            'Where exactly is the abdominal discomfort?',
            'வயிற்றில் எந்த இடத்தில் பிரச்சனை உள்ளது?',
            ['மேல் பகுதி', 'கீழ் பகுதி', 'வலது பக்கம்', 'இடது பக்கம்', 'முழுவதும்'],
            'abdomen'
        ),

        _q(
            'abd_onset',
            'When did it start and is it getting better or worse?',
            'எப்போது தொடங்கியது? இப்போது நல்லதாகிறதா அல்லது மோசமாகிறதா?',
            ['நல்லதாகிறது', 'மோசமாகிறது', 'அதேபோல்'],
            'abdomen'
        ),

        _q(
            'abd_food',
            'Is it related to food, meals, or bowel movements?',
            'உணவு அல்லது மலம் கழிப்பதுடன் தொடர்பு உள்ளதா?',
            ['உணவுக்குப் பிறகு', 'உணவுக்கு முன்', 'மலம் கழித்த பிறகு', 'தொடர்பு இல்லை', 'தெரியவில்லை'],
            'abdomen'
        ),

        _q(
            'abd_vomit_stool',
            'Any vomiting, loose stools, constipation, black stool or blood?',
            'வாந்தி, வயிற்றுப்போக்கு, மலச்சிக்கல், கருப்பு மலம் அல்லது ரத்தம் உள்ளதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'abdomen'
        )
    ]),

    ('urinary', [
        'urine', 'urinary', 'burning urine',
        'frequent urination', 'சிறுநீர்',
        'siruneer'
    ], [

        _q(
            'urinary_burning',
            'Do you have burning or pain while passing urine?',
            'சிறுநீர் கழிக்கும் போது எரிச்சல் அல்லது வலி உள்ளதா?',
            ['ஆம்', 'இல்லை'],
            'urinary'
        ),

        _q(
            'urinary_frequency',
            'Are you passing urine more often than usual or urgently?',
            'வழக்கத்தை விட அடிக்கடி அல்லது அவசரமாக சிறுநீர் கழிக்க வேண்டியிருக்கிறதா?',
            ['ஆம்', 'இல்லை'],
            'urinary'
        ),

        _q(
            'urinary_blood',
            'Have you noticed blood in the urine or pain in the side/back?',
            'சிறுநீரில் ரத்தம் அல்லது பக்கவாட்டு/முதுகு வலி உள்ளதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'urinary'
        )
    ]),

    ('skin', [
        'skin', 'rash', 'itch', 'acne', 'eczema',
        'தோல்', 'சொறி', 'அரிப்பு',
        'thol', 'tholi'
    ], [

        _q(
            'skin_onset',
            'When did the skin problem start and how has it changed?',
            'தோல் பிரச்சனை எப்போது தொடங்கியது? எப்படி மாறியுள்ளது?',
            ['பரவுகிறது', 'குறைந்து வருகிறது', 'அதேபோல்', 'தெரியவில்லை'],
            'skin'
        ),

        _q(
            'skin_itch',
            'Is there itching, pain, swelling, discharge or fever?',
            'அரிப்பு, வலி, வீக்கம், நீர்/சீழ் அல்லது காய்ச்சல் உள்ளதா?',
            ['ஆம்', 'இல்லை', 'சில உள்ளது'],
            'skin'
        ),

        _q(
            'skin_trigger',
            'Any new food, medicine, soap, cosmetic, plant or other exposure before it started?',
            'தொடங்குவதற்கு முன் புதிய உணவு, மருந்து, சோப்பு, அழகு சாதனம் அல்லது வேறு பொருளுடன் தொடர்பு இருந்ததா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'skin'
        )
    ]),

    ('pain', [
        'pain', 'வலி', 'ache',
        'vali', 'valikkuthu'
    ], [

        _q(
            'pain_location',
            'Where is the pain exactly?',
            'வலி எந்த இடத்தில் உள்ளது?',
            ['தலை', 'மார்பு', 'வயிறு', 'முதுகு', 'மூட்டு/கால்', 'வேறு இடம்'],
            'pain'
        ),

        _q(
            'pain_onset',
            'Did the pain start suddenly or gradually?',
            'வலி திடீரெனவா அல்லது மெதுவாகவா தொடங்கியது?',
            ['திடீரென', 'மெதுவாக', 'தெரியவில்லை'],
            'pain'
        ),

        _q(
            'pain_trigger',
            'What makes the pain worse or better: movement, food, rest, or something else?',
            'எதனால் வலி அதிகரிக்கிறது அல்லது குறைகிறது: அசைவு, உணவு, ஓய்வு அல்லது வேறு காரணமா?',
            ['அசைவு', 'உணவு', 'ஓய்வு', 'வேறு காரணம்', 'தெரியவில்லை'],
            'pain'
        ),

        _q(
            'pain_function',
            'Does the pain stop you from walking, working, sleeping or normal activities?',
            'வலி நடப்பது, வேலை செய்வது, தூங்குவது அல்லது வழக்கமான செயல்களை பாதிக்கிறதா?',
            ['ஆம்', 'இல்லை', 'சில அளவு'],
            'pain'
        )
    ]),

    ('gyn', [
        'period', 'menstrual', 'pregnancy',
        'மாதவிடாய்', 'கர்ப்பம்'
    ], [

        _q(
            'gyn_cycle',
            'When was your last menstrual period, if applicable?',
            'பொருந்துமானால், கடைசி மாதவிடாய் எப்போது வந்தது?',
            ['தெரியும்', 'தெரியவில்லை', 'பொருந்தாது'],
            'gyn'
        ),

        _q(
            'gyn_bleeding',
            'Any unusually heavy bleeding, severe pain, or bleeding during pregnancy?',
            'வழக்கத்திற்கு மாறான அதிக ரத்தப்போக்கு, கடுமையான வலி அல்லது கர்ப்ப கால ரத்தப்போக்கு உள்ளதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'gyn'
        )
    ])
]


AYUSH_BRANCHES = [

    ('ayush_digestive', [
        'stomach', 'gas', 'acidity', 'constipation',
        'வயிறு', 'அமிலம்', 'மலச்சிக்கல்',
        'vayiru', 'vayithu'
    ], [

        _q(
            'ayush_agni_change',
            'With this problem, how has your appetite or Agni changed?',
            'இந்த பிரச்சனையுடன் உங்கள் பசி அல்லது அக்னி எப்படி மாறியுள்ளது?',
            ['குறைந்துள்ளது', 'அதிகரித்துள்ளது', 'மாறவில்லை', 'தெரியவில்லை'],
            'AYUSH'
        ),

        _q(
            'ayush_koshtha_change',
            'Has your bowel habit or Koshtha changed recently?',
            'சமீபத்தில் உங்கள் மலம் கழிக்கும் பழக்கம் அல்லது கோஷ்டத்தில் மாற்றம் ஏற்பட்டதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'AYUSH'
        ),

        _q(
            'ayush_ahara_trigger',
            'Does any particular food or meal pattern trigger or worsen it?',
            'குறிப்பிட்ட உணவு அல்லது உணவு நேரத்தால் பிரச்சனை அதிகரிக்கிறதா?',
            ['ஆம்', 'இல்லை', 'தெரியவில்லை'],
            'AYUSH'
        )
    ]),

    ('ayush_general', [
        'pain', 'வலி', 'vali'
    ], [

        _q(
            'ayush_nidana_trigger',
            'What food, activity, sleep pattern or season seems to worsen or relieve the symptom?',
            'எந்த உணவு, செயல்பாடு, தூக்கம் அல்லது பருவநிலை அறிகுறியை அதிகரிக்கிறது அல்லது குறைக்கிறது?',
            ['உணவு', 'செயல்பாடு', 'தூக்கம்', 'பருவநிலை', 'தெரியவில்லை'],
            'AYUSH'
        ),

        _q(
            'ayush_vikriti_change',
            'How is this different from your usual health pattern?',
            'இது உங்கள் வழக்கமான உடல்நிலையிலிருந்து எப்படி மாறியுள்ளது?',
            ['மாற்றம் உள்ளது', 'மாற்றம் இல்லை', 'தெரியவில்லை'],
            'AYUSH'
        )
    ])
]


# ---------------------------------------------------------
# SEMANTIC COVERAGE
# ---------------------------------------------------------

def _has_any(text, words):
    text = norm(text)
    return any(norm(w) in text for w in words)


def _duration_already_known(text):
    text = norm(text)

    # Normalize Tanglish Tamil duration variants
    text = re.sub(r'\bnaalaa\b', 'naal', text)
    text = re.sub(r'\bnaala\b', 'naal', text)
    text = re.sub(r'\bnaalava\b', 'naal', text)
    text = re.sub(r'\bvaarama\b', 'vaaram', text)
    text = re.sub(r'\bmaasama\b', 'maasam', text)
    text = re.sub(r'\baandu\b', 'aandu', text)

    patterns = [
        r'\b\d+\s*(day|days|week|weeks|month|months)\b',
        r'\b\d+\s*(naal|nal|vaaram|varam|maasam|aandu|varusham)\b',
        r'\b(oru|rendu|irandu|moon[u]?|naalu|naangu|anju|ainthu|aaru|ezhu|ettu|onpathu|pathu)\s*(naal|nal|vaaram|varam|maasam|aandu|varusham)\b',
        r'(ஒன்று|ஒரு|இரண்டு|மூன்று|நான்கு|ஐந்து|ஆறு|ஏழு|எட்டு|தொன்னவரு|பத்து)\s*(நாட்கள்|நாள்|வாரங்கள்|வாரம்|மாதங்கள்|மாதம்|வருடங்கள்|வருடம்)',
        r'(இன்று|நேற்று|நேத்தி|இன்னிக்கு|அறிஞ்சிக்கு)',
    ]

    return any(re.search(p, text) for p in patterns)


def _symptom_location_known(text, symptom):
    text = norm(text)

    if symptom == 'headache':
        return _has_any(text, [
            'headache',
            'head pain',
            'thala vali',
            'thalavali',
            'thalai vali',
            'தலைவலி',
            'தலை வலி'
        ])

    if symptom == 'abdomen':
        return _has_any(text, [
            'stomach pain',
            'stomach ache',
            'abdominal pain',
            'vayiru vali',
            'vayir vali',
            'vayithula vali',
            'வயிற்றுவலி',
            'வயிற்று வலி',
            'வயிற்றில் வலி'
        ])

    if symptom == 'chest':
        return _has_any(text, [
            'chest pain',
            'chest discomfort',
            'marbu vali',
            'nenju vali',
            'மார்பு வலி',
            'நெஞ்சு வலி'
        ])

    if symptom == 'urinary':
        return _has_any(text, [
            'urine pain',
            'burning urine',
            'siruneer vali',
            'சிறுநீர் வலி'
        ])

    return False


def _specific_location_known(text):
    """
    Detect explicit body locations in natural language.
    """

    location_words = [
        'head', 'thala', 'தலை',
        'chest', 'marbu', 'nenju', 'மார்பு', 'நெஞ்சு',
        'stomach', 'vayiru', 'vayithu', 'வயிறு',
        'back', 'mudugu', 'முதுகு',
        'neck', 'kazhuthu', 'கழுத்து',
        'hand', 'kai', 'கை',
        'leg', 'kaal', 'கால்',
        'right side', 'left side',
        'வலது பக்கம்', 'இடது பக்கம்'
    ]

    return _has_any(text, location_words)


def _question_already_covered(key, text, answers):
    """
    Deterministic protection layer.
    If the patient's natural language already contains
    the information required by a question, remove it
    before OpenRouter sees the candidate.
    """

    text = norm(text)

    if key in answers and covered(answers.get(key)):
        return True

    # Duration
    if key in {
        'fever_duration',
        'resp_duration',
        'head_onset',
        'abd_onset',
        'chest_onset',
        'pain_onset',
        'abd_food',
        'skin_onset'
    }:
        if _duration_already_known(text):
            return True

    # Headache location is already implied by "headache"
    if key == 'head_location':
        if _symptom_location_known(text, 'headache'):
            return True

    # Abdominal location is already implied by "vayiru vali"
    if key == 'abd_location':
        if _symptom_location_known(text, 'abdomen'):
            return True

    # Chest location is already implied by chest pain
    if key == 'chest_character':
        # Do not remove character; this is still useful.
        pass

    # Generic pain location is unnecessary when a specific
    # location was already mentioned.
    if key == 'pain_location':
        if _specific_location_known(text):
            return True

    return False


def _build_known_text(answers):
    if not answers:
        return ''

    return ' '.join(
        norm(v)
        for v in answers.values()
        if covered(v)
    )


def _dedupe_questions(items):
    result = []
    seen = set()

    for q in items:
        key = q.get('key')

        if not key or key in seen:
            continue

        seen.add(key)
        result.append(q)

    return result


def get_relevant_candidates(mode, answers, language='English'):
    """
    Build a candidate pool for OpenRouter.

    IMPORTANT:
    This function does NOT decide the final question.
    OpenRouter still performs the clinical reasoning.

    This layer only removes questions whose answers are
    already clearly present in the patient's natural language.
    """

    answers = answers or {}
    text = _build_known_text(answers)

    branches = []

    if mode == 'AYUSH':
        branches.extend(AYUSH_BRANCHES)

    branches.extend(BRANCHES)

    candidates = []

    for name, words, questions in branches:

        if not _has_any(text, words):
            continue

        for q in questions:

            key = q['key']

            if _question_already_covered(
                key,
                text,
                answers
            ):
                continue

            candidates.append({
                'key': key,
                'question': q['ta'] if language == 'Tamil' else q['en'],
                'branch': q['branch'] or name,
                'options': localize_options(q.get('options', []), language),
                'adaptive': True
            })

    return _dedupe_questions(candidates)[:20]


def next_question(mode, answers, language='English'):

    answers = answers or {}

    # First question
    if not covered(answers.get('chief_complaint')):

        return {
            'key': 'chief_complaint',
            'question': (
                'இன்று உங்களுக்கு முக்கியமாக என்ன உடல்நலப் பிரச்சனை உள்ளது?'
                if language == 'Tamil'
                else 'What is your main health problem today?'
            ),
            'options': [],
            'adaptive': False,
            'reason': 'start'
        }

    candidates = get_relevant_candidates(
        mode,
        answers,
        language
    )

    # Deterministic fallback only.
    # OpenRouter should normally select the final question.
    if candidates:
        q = candidates[0]

        return {
            'key': q['key'],
            'question': q['question'],
            'options': q['options'],
            'adaptive': True,
            'branch': q['branch'],
            'reason': 'symptom_specific'
        }

    core = AYUSH_SECTIONS if mode == 'AYUSH' else NORMAL_SECTIONS
    trans = AYUSH_TA if mode == 'AYUSH' else NORMAL_TA

    for key, en in core:

        if not covered(answers.get(key)):

            return {
                'key': key,
                'question': (
                    trans.get(key, en)
                    if language == 'Tamil'
                    else en
                ),
                'options': [],
                'adaptive': False,
                'reason': 'core_history'
            }

    return None


def get_questions(mode='NORMAL', language='English'):

    core = (
        AYUSH_SECTIONS
        if mode == 'AYUSH'
        else NORMAL_SECTIONS
    )

    trans = (
        AYUSH_TA
        if mode == 'AYUSH'
        else NORMAL_TA
    )

    return [
        {
            'key': k,
            'question': (
                trans.get(k, q)
                if language == 'Tamil'
                else q
            ),
            'options': [],
            'adaptive': False
        }
        for k, q in core
    ]


# Backward-compatible name used by interview_engine.py
def _candidate_questions(mode, answers, language='English'):
    return get_relevant_candidates(
        mode,
        answers,
        language
    )