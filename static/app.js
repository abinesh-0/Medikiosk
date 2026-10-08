/*
 * MediKiosk SIH 26047 - Judge Demo UI
 *
 * PATIENT LANGUAGE RULE
 * ---------------------
 * English selected:
 *   Patient UI + questions + options + voice = English
 *
 * Tamil selected:
 *   Patient UI + questions + options + help + validation + voice = Tamil
 *
 * Doctor / Staff / Hospital Admin:
 *   English
 *
 * IMPORTANT FIXES
 * ---------------
 * 1. Question option buttons use addEventListener()
 *    instead of inline JSON onclick.
 *
 * 2. SpeechSynthesis voice list is loaded asynchronously.
 *
 * 3. Tamil voice is explicitly searched using ta-IN / ta-*.
 *
 * 4. Selected option is displayed in the answer box.
 *
 * 5. Backend receives routing context so existing
 *    deterministic routing continues to work.
 */


/* =========================================================
   GLOBAL APPLICATION STATE
========================================================= */

const A = {

  lang:
    localStorage.mk_lang || 'English',

  token:
    localStorage.mk_token || '',

  role:
    '',

  case:
    null,

  questionIndex:
    0,

  questions:
    [],

  mode:
    'NORMAL',

  selectedRouteKey:
    '',

  lastDoctor:
    null,
  
  answers:{},

  // Adaptive interview state. Existing UI/state behavior remains unchanged.
  questionHistory: [],
  currentQuestion: null
};


/* =========================================================
   UI TRANSLATIONS
========================================================= */

const I = {

  English: {

    choose:
      'Choose language',

    tamil:
      'Tamil',

    english:
      'English',

    access:
      'Choose access',

    patient:
      'Patient',

    doctor:
      'Doctor',

    staff:
      'Staff',

    admin:
      'Hospital Admin',

    continue:
      'Continue',

    start:
      'Start',

    back:
      'Back',

    name:
      'Patient name',

    age:
      'Age',

    gender:
      'Gender',

    phone:
      'Phone (optional)',

    address:
      'Area / address (optional)',

    pid:
      'Existing Patient ID (optional)',

    select:
      'Select',

    male:
      'Male',

    female:
      'Female',

    other:
      'Other',

    normal:
      'Normal Consultation',

    normalD:
      'General medical consultation',

    ayush:
      'AYUSH Consultation',

    ayushD:
      'Ayurveda / Siddha / other AYUSH care',

    voice:
      '🔊 Hear question',

    mic:
      '🎙 Speak answer',

    next:
      'Next',

    history:
      'Previous medical history?',

    yes:
      'Yes',

    no:
      'No',

    upload:
      'Upload / scan report',

    scan:
      'Open camera scanner',

    finish:
      'Finish history',

    summary:
      'Clinical summary',

    route:
      'Department',

    token:
      'Patient token',

    print:
      'Print token',

    call:
      'Call patient',

    startC:
      'Start consultation',

    complete:
      'Complete patient',

    save:
      'Save review',

    dashboard:
      'Dashboard',

    logout:
      'Logout',

    active:
      'ACTIVE',

    waiting:
      'WAITING',

    triage:
      'TRIAGE',

    dept:
      'Department',

    email:
      'Department email',

    pass:
      'Department password',

    doctorName:
      'Current doctor name',

    shift:
      'Shift',

    login:
      'Secure login',

    staffEmail:
      'Staff email',

    staffPass:
      'Staff password',

    adminEmail:
      'Admin email',

    adminPass:
      'Admin password',

    manage:
      'Manage departments',

    create:
      'Create department',

    deptName:
      'Department name',

    newEmail:
      'Department email',

    newPass:
      'Department password',

    stats:
      'Hospital overview',

    audit:
      'Security & audit log',

    progress:
      'Question',

    answer:
      'Answer',

    placeholder:
      'Type or use voice',

    scanTitle:
      'Scan paper medical records',

    scanText:
      'Capture prescriptions, lab reports or discharge summaries before the doctor sees the patient.',

    scanHelp:
      'For this offline prototype, paste sample extracted text here if the uploaded document is an image/PDF.',

    clinicalSummary:
      'Clinical summary',

    safety:
      'Safety screening',

    aiDraft:
      'AI-assisted draft; clinician verification required.',

    noHistoryDoc:
      'No previous medical history document provided.',

    queue:
      'Today’s patient queue',

    patientHistory:
      'Patient history',

    doctorNote:
      'Doctor note',

    safetyAlerts:
      'Safety alerts',

    patientQueue:
      'Patient queue',

    departments:
      'Departments',

    patients:
      'Patients',

    cases:
      'Cases',

    routeReady:
      'Your case has been routed to the appropriate department.',

    tokenReady:
      'Please wait for your token to be called.',

    required:
      'Please complete the required fields.',

    answerRequired:
      'Please answer the question.',

    browserVoiceUnavailable:
      'Browser voice input is not available. You can type your answer.',

    cameraHelp:
      'Camera scanner uses your device camera. After capture, select the image as the medical document.',

    saved:
      'Saved',

    noCases:
      'No assigned cases',

    noAlerts:
      'No active red-flag alerts'

  },


  Tamil: {

    choose:
      'மொழியைத் தேர்வு செய்யுங்கள்',

    tamil:
      'தமிழ்',

    english:
      'English',

    access:
      'யார் தொடர்கிறீர்கள்?',

    patient:
      'நோயாளர்',

    doctor:
      'மருத்துவர்',

    staff:
      'பணியாளர்',

    admin:
      'மருத்துவமனை நிர்வாகம்',

    continue:
      'தொடரவும்',

    start:
      'தொடங்குங்கள்',

    back:
      'பின்',

    name:
      'நோயாளர் பெயர்',

    age:
      'வயது',

    gender:
      'பாலினம்',

    phone:
      'தொலைபேசி (விருப்பம்)',

    address:
      'பகுதி / முகவரி (விருப்பம்)',

    pid:
      'முந்தைய நோயாளர் அடையாள எண் (விருப்பம்)',

    select:
      'தேர்வு செய்யுங்கள்',

    male:
      'ஆண்',

    female:
      'பெண்',

    other:
      'மற்றவை',

    normal:
      'பொது மருத்துவ ஆலோசனை',

    normalD:
      'பொதுவான உடல்நலப் பிரச்சனைக்கான ஆலோசனை',

    ayush:
      'ஆயுஷ் ஆலோசனை',

    ayushD:
      'ஆயுர்வேதம் / சித்தா / பிற ஆயுஷ் சேவைக்கான ஆலோசனை',

    voice:
      '🔊 கேள்வியைக் கேளுங்கள்',

    mic:
      '🎙 பதிலைப் பேசுங்கள்',

    next:
      'அடுத்து',

    history:
      'முந்தைய மருத்துவ வரலாறு உள்ளதா?',

    yes:
      'ஆம்',

    no:
      'இல்லை',

    upload:
      'மருத்துவ அறிக்கையைப் பதிவேற்ற / ஸ்கேன் செய்யவும்',

    scan:
      'கேமரா ஸ்கேனரைத் திறக்கவும்',

    finish:
      'மருத்துவ வரலாற்றை முடிக்கவும்',

    summary:
      'மருத்துவச் சுருக்கம்',

    route:
      'துறை',

    token:
      'நோயாளர் டோக்கன்',

    print:
      'டோக்கனை அச்சிடுங்கள்',

    call:
      'நோயாளியை அழைக்கவும்',

    startC:
      'ஆலோசனையைத் தொடங்குங்கள்',

    complete:
      'நோயாளியை முடிக்கவும்',

    save:
      'மருத்துவர் மதிப்பாய்வைச் சேமிக்கவும்',

    dashboard:
      'முகப்பு',

    logout:
      'வெளியேறுங்கள்',

    active:
      'செயலில்',

    waiting:
      'காத்திருக்கிறது',

    triage:
      'அவசர பரிசோதனை',

    dept:
      'துறை',

    email:
      'துறை மின்னஞ்சல்',

    pass:
      'துறை கடவுச்சொல்',

    doctorName:
      'தற்போதைய மருத்துவர் பெயர்',

    shift:
      'பணி நேரம்',

    login:
      'பாதுகாப்பான உள்நுழைவு',

    staffEmail:
      'பணியாளர் மின்னஞ்சல்',

    staffPass:
      'பணியாளர் கடவுச்சொல்',

    adminEmail:
      'நிர்வாக மின்னஞ்சல்',

    adminPass:
      'நிர்வாக கடவுச்சொல்',

    manage:
      'துறைகளை நிர்வகிக்கவும்',

    create:
      'துறையை உருவாக்கவும்',

    deptName:
      'துறை பெயர்',

    newEmail:
      'துறை மின்னஞ்சல்',

    newPass:
      'துறை கடவுச்சொல்',

    stats:
      'மருத்துவமனை நிலவரம்',

    audit:
      'பாதுகாப்பு மற்றும் செயல்பாட்டு பதிவு',

    progress:
      'கேள்வி',

    answer:
      'பதில்',

    placeholder:
      'தட்டச்சு செய்யவும் அல்லது பேசவும்',

    scanTitle:
      'காகித மருத்துவ அறிக்கைகளை ஸ்கேன் செய்யவும்',

    scanText:
      'மருத்துவர் பார்ப்பதற்கு முன் மருந்துச் சீட்டு, ஆய்வக அறிக்கை அல்லது டிஸ்சார்ஜ் சுருக்கத்தைப் பதிவு செய்யுங்கள்.',

    scanHelp:
      'இந்த offline prototype-ல் படம்/PDF பதிவேற்றினால், மாதிரி மருத்துவ உரையை கீழே ஒட்டலாம்.',

    clinicalSummary:
      'மருத்துவச் சுருக்கம்',

    safety:
      'பாதுகாப்பு பரிசோதனை',

    aiDraft:
      'AI உதவியுடன் உருவாக்கப்பட்ட வரைவு; மருத்துவர் சரிபார்ப்பு அவசியம்.',

    noHistoryDoc:
      'முந்தைய மருத்துவ வரலாற்று அறிக்கை வழங்கப்படவில்லை.',

    queue:
      'இன்றைய நோயாளர் வரிசை',

    patientHistory:
      'நோயாளர் மருத்துவ வரலாறு',

    doctorNote:
      'மருத்துவர் குறிப்பு',

    safetyAlerts:
      'அவசர எச்சரிக்கைகள்',

    patientQueue:
      'நோயாளர் வரிசை',

    departments:
      'துறைகள்',

    patients:
      'நோயாளர்கள்',

    cases:
      'வழக்குகள்',

    routeReady:
      'உங்கள் தகவல்கள் பொருத்தமான மருத்துவத் துறைக்கு அனுப்பப்பட்டுள்ளன.',

    tokenReady:
      'உங்கள் டோக்கன் அழைக்கப்படும் வரை தயவுசெய்து காத்திருக்கவும்.',

    required:
      'தேவையான தகவல்களை முழுமையாக உள்ளிடுங்கள்.',

    answerRequired:
      'கேள்விக்கு பதில் அளிக்கவும்.',

    browserVoiceUnavailable:
      'உங்கள் உலாவியில் குரல் உள்ளீடு கிடைக்கவில்லை. பதிலை தட்டச்சு செய்யலாம்.',

    cameraHelp:
      'கேமரா ஸ்கேனர் உங்கள் சாதன கேமராவைப் பயன்படுத்தும். படம் எடுத்த பிறகு அதை மருத்துவ அறிக்கையாகத் தேர்வு செய்யுங்கள்.',

    saved:
      'சேமிக்கப்பட்டது',

    noCases:
      'ஒதுக்கப்பட்ட நோயாளர்கள் இல்லை',

    noAlerts:
      'செயலில் உள்ள அவசர எச்சரிக்கைகள் இல்லை'

  }

};


/* =========================================================
   TAMIL QUESTION SET
========================================================= */

const TAMIL_QUESTION_SETS = {

  NORMAL: [

    {
      key:
        'main_problem',

      q:
        'இன்று உங்களுக்கு உள்ள முக்கியமான உடல்நலப் பிரச்சனை என்ன?',

      o: [

        [
          'காய்ச்சல்',
          'fever'
        ],

        [
          'இருமல் அல்லது மூச்சுத்திணறல்',
          'breathing'
        ],

        [
          'மார்பு அல்லது இதயம் தொடர்பான பிரச்சனை',
          'chest'
        ],

        [
          'வலி',
          'pain'
        ],

        [
          'வயிற்றுப் பிரச்சனை',
          'stomach'
        ],

        [
          'வேறு பிரச்சனை',
          'other'
        ]

      ]

    },


    {
      key:
        'onset',

      q:
        'இந்தப் பிரச்சனை எப்போது தொடங்கியது?',

      o: [

        [
          'இன்று',
          'today'
        ],

        [
          '1–3 நாட்களுக்கு முன்பு',
          '1-3 days'
        ],

        [
          'ஒரு வாரத்திற்கும் மேலாக',
          'more than a week'
        ],

        [
          'நீண்ட நாட்களாக',
          'longer'
        ]

      ]

    },


    {
      key:
        'severity',

      q:
        'இந்தப் பிரச்சனை எவ்வளவு தீவிரமாக உள்ளது?',

      o: [

        [
          'லேசாக',
          'mild'
        ],

        [
          'மிதமாக',
          'moderate'
        ],

        [
          'தீவிரமாக',
          'severe'
        ]

      ]

    },


    {
      key:
        'trend',

      q:
        'இந்தப் பிரச்சனை எப்படி உள்ளது?',

      o: [

        [
          'முன்பை விட நன்றாக உள்ளது',
          'better'
        ],

        [
          'மோசமாகி வருகிறது',
          'worse'
        ],

        [
          'அதே நிலையில் உள்ளது',
          'same'
        ]

      ]

    }

  ],


  AYUSH: [

    {
      key:
        'ayush_concern',

      q:
        'உங்களுக்கு உள்ள முக்கியமான உடல்நலப் பிரச்சனை என்ன?',

      o: [

        [
          'வலி',
          'pain'
        ],

        [
          'செரிமானப் பிரச்சனை',
          'digestive'
        ],

        [
          'தூக்கம் அல்லது மனஅழுத்தப் பிரச்சனை',
          'sleep stress'
        ],

        [
          'பொதுவான உடல்நலப் பிரச்சனை',
          'wellness'
        ]

      ]

    },


    {
      key:
        'ayush_onset',

      q:
        'இந்தப் பிரச்சனை எப்போது தொடங்கியது?',

      o: [

        [
          'இன்று',
          'today'
        ],

        [
          'சில நாட்களுக்கு முன்பு',
          'few days'
        ],

        [
          'சில வாரங்களுக்கு முன்பு',
          'few weeks'
        ],

        [
          'நீண்ட நாட்களாக',
          'longer'
        ]

      ]

    },


    {
      key:
        'agni',

      q:
        'உங்கள் பசி மற்றும் செரிமானம் எப்படி உள்ளது?',

      o: [

        [
          'நன்றாக உள்ளது',
          'good'
        ],

        [
          'குறைந்துள்ளது',
          'reduced'
        ],

        [
          'சீராக இல்லை',
          'irregular'
        ],

        [
          'தெரியவில்லை',
          'not sure'
        ]

      ]

    },


    {
      key:
        'ahara_vihara',

      q:
        'உங்கள் உணவு, தூக்கம் மற்றும் தினசரி வாழ்க்கை முறையைப் பற்றி சொல்லுங்கள்.',

      o: [

        [
          'சீராக உள்ளது',
          'regular'
        ],

        [
          'சமீபத்தில் மாற்றம் ஏற்பட்டுள்ளது',
          'changed'
        ],

        [
          'விளக்க உதவி வேண்டும்',
          'need help'
        ]

      ]

    }

  ]

};


/* =========================================================
   ENGLISH QUESTION SET
========================================================= */

const ENGLISH_QUESTION_SETS = {

  NORMAL: [

    {
      key:
        'main_problem',

      q:
        'What is your main health problem today?',

      o: [

        [
          'Fever',
          'fever'
        ],

        [
          'Cough or breathing problem',
          'breathing'
        ],

        [
          'Chest or heart-related symptom',
          'chest'
        ],

        [
          'Pain',
          'pain'
        ],

        [
          'Stomach problem',
          'stomach'
        ],

        [
          'Other',
          'other'
        ]

      ]

    },


    {
      key:
        'onset',

      q:
        'When did it start?',

      o: [

        [
          'Today',
          'today'
        ],

        [
          '1–3 days',
          '1-3 days'
        ],

        [
          'More than a week',
          'more than a week'
        ],

        [
          'Longer',
          'longer'
        ]

      ]

    },


    {
      key:
        'severity',

      q:
        'How severe is it?',

      o: [

        [
          'Mild',
          'mild'
        ],

        [
          'Moderate',
          'moderate'
        ],

        [
          'Severe',
          'severe'
        ]

      ]

    },


    {
      key:
        'trend',

      q:
        'Is it getting better, worse or about the same?',

      o: [

        [
          'Better',
          'better'
        ],

        [
          'Worse',
          'worse'
        ],

        [
          'Same',
          'same'
        ]

      ]

    }

  ],


  AYUSH: [

    {
      key:
        'ayush_concern',

      q:
        'What is your main health concern?',

      o: [

        [
          'Pain',
          'pain'
        ],

        [
          'Digestive problem',
          'digestive'
        ],

        [
          'Sleep or stress',
          'sleep stress'
        ],

        [
          'General wellness',
          'wellness'
        ]

      ]

    },


    {
      key:
        'ayush_onset',

      q:
        'When did this problem start?',

      o: [

        [
          'Today',
          'today'
        ],

        [
          'A few days',
          'few days'
        ],

        [
          'A few weeks',
          'few weeks'
        ],

        [
          'Longer',
          'longer'
        ]

      ]

    },


    {
      key:
        'agni',

      q:
        'How is your appetite and digestion?',

      o: [

        [
          'Good',
          'good'
        ],

        [
          'Reduced',
          'reduced'
        ],

        [
          'Irregular',
          'irregular'
        ],

        [
          'Not sure',
          'not sure'
        ]

      ]

    },


    {
      key:
        'ahara_vihara',

      q:
        'Tell us about your food, sleep and daily routine.',

      o: [

        [
          'Regular',
          'regular'
        ],

        [
          'Changes recently',
          'changed'
        ],

        [
          'Need help explaining',
          'need help'
        ]

      ]

    }

  ]

};


/* =========================================================
   DEPARTMENT TRANSLATION
========================================================= */

const routeLabels = {

  'General Medicine':
    'பொது மருத்துவம்',

  'Cardiology':
    'இதய மருத்துவம்',

  'Pulmonology':
    'நுரையீரல் மருத்துவம்',

  'Orthopaedics':
    'எலும்பியல் மருத்துவம்',

  'Dermatology':
    'தோல் மருத்துவம்',

  'Ayurveda':
    'ஆயுர்வேதம்'

};


/* =========================================================
   BASIC HELPERS
========================================================= */

const t = key => {

  return (
    (I[A.lang] &&
      I[A.lang][key]) ||

    I.English[key] ||

    key
  );

};


const app =
  document.getElementById('app');


const esc = value => {

  return String(
    value ?? ''
  ).replace(
    /[&<>"']/g,

    ch => ({
      '&':
        '&amp;',

      '<':
        '&lt;',

      '>':
        '&gt;',

      '"':
        '&quot;',

      "'":
        '&#39;'

    }[ch])
  );

};


const tamil = () =>
  A.lang === 'Tamil';


const localRoute = name => {

  if (!tamil()) {
    return name;
  }

  return (
    routeLabels[name] ||
    name
  );

};


/* =========================================================
   SPEECH VOICE MANAGEMENT
========================================================= */

/*
 * Chrome loads speech voices asynchronously.
 *
 * Old implementation:
 *
 *   speechSynthesis.getVoices()
 *
 * immediately after page load.
 *
 * Sometimes that returns [].
 *
 * This version continuously refreshes the voice list.
 */

let availableVoices = [];


function loadVoices() {

  if (
    !('speechSynthesis' in window)
  ) {
    availableVoices = [];
    return;
  }

  availableVoices =
    speechSynthesis.getVoices() || [];

}


/*
 * Chrome / Edge fires this event
 * when voices become available.
 */

if (
  'speechSynthesis' in window
) {

  speechSynthesis.onvoiceschanged =
    () => {

      loadVoices();

    };

}


/*
 * Load once immediately.
 */

loadVoices();


/* =========================================================
   FIND TAMIL VOICE
========================================================= */

function getTamilVoice() {

  loadVoices();


  /*
   * First preference:
   * exact Tamil India voice
   */

  let voice =
    availableVoices.find(
      v =>
        String(v.lang)
          .toLowerCase()
          ===
        'ta-in'
    );


  /*
   * Second preference:
   * any Tamil voice
   */

  if (!voice) {

    voice =
      availableVoices.find(
        v =>
          /^ta[-_]/i.test(
            String(v.lang)
          )
      );

  }


  /*
   * Third preference:
   * some browsers may expose Tamil
   * as just "ta"
   */

  if (!voice) {

    voice =
      availableVoices.find(
        v =>
          String(v.lang)
            .toLowerCase()
            ===
          'ta'
      );

  }


  return voice || null;

}


/* =========================================================
   FIND ENGLISH VOICE
========================================================= */

function getEnglishVoice() {

  loadVoices();


  let voice =
    availableVoices.find(
      v =>
        String(v.lang)
          .toLowerCase()
          ===
        'en-in'
    );


  if (!voice) {

    voice =
      availableVoices.find(
        v =>
          /^en[-_]/i.test(
            String(v.lang)
          )
      );

  }


  return voice || null;

}


/* =========================================================
   TEXT TO SPEECH
========================================================= */

function speak(text) {

  if (
    !('speechSynthesis' in window)
  ) {

    alert(
      tamil()
        ? 'உங்கள் உலாவியில் குரல் வசதி கிடைக்கவில்லை.'
        : 'Speech is not supported by this browser.'
    );

    return;

  }


  const cleanText =
    String(text || '').trim();


  if (!cleanText) {
    return;
  }


  /*
   * Stop previous speech.
   */

  speechSynthesis.cancel();


  /*
   * Small delay helps Chrome
   * after cancel().
   */

  setTimeout(
    () => {

      const utterance =
        new SpeechSynthesisUtterance(
          cleanText
        );


      if (tamil()) {

        /*
         * IMPORTANT:
         * Tamil language.
         */

        utterance.lang =
          'ta-IN';


        /*
         * Slower speed for elderly users.
         */

        utterance.rate =
          0.78;


        utterance.pitch =
          1.0;


        const tamilVoice =
          getTamilVoice();


        if (tamilVoice) {

          utterance.voice =
            tamilVoice;

        }

      } else {

        utterance.lang =
          'en-IN';


        utterance.rate =
          0.88;


        utterance.pitch =
          1.0;


        const englishVoice =
          getEnglishVoice();


        if (englishVoice) {

          utterance.voice =
            englishVoice;

        }

      }


      utterance.onerror =
        () => {

          /*
           * Do not block patient journey
           * if TTS fails.
           */

        };


      speechSynthesis.speak(
        utterance
      );

    },

    100
  );

}

function voiceInput() {
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
        alert(
            tamil()
                ? 'இந்த browser-ல் குரல் மூலம் பதில் சொல்லும் வசதி இல்லை. Typing பயன்படுத்தவும்.'
                : 'Voice input is not supported by this browser. You can type your answer.'
        );
        return;
    }

    const Recognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    const recognition = new Recognition();

    recognition.lang = tamil() ? 'ta-IN' : 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = function (event) {
        const text =
            event.results[0][0].transcript;

        const answerInput =
            document.getElementById('ans');

        if (answerInput) {
            answerInput.value = text;
            answerInput.dispatchEvent(new Event('input', {
                bubbles: true
            }));
        }
    };

    recognition.onerror = function (event) {
        if (event.error !== 'no-speech') {
            alert(
                tamil()
                    ? 'குரலை பெற முடியவில்லை. மீண்டும் முயற்சிக்கவும்.'
                    : 'Could not hear your answer. Please try again.'
            );
        }
    };

    recognition.onend = function () {
        // Recognition finished normally.
    };

    recognition.start();
}


/* =========================================================
   PAGE SHELL
========================================================= */

function shell(
  title,
  body,
  patientScreen = false
) {

  let headerLanguage;


  if (patientScreen) {

    headerLanguage =
      tamil()
        ? 'தமிழ்'
        : 'English';

  } else {

    headerLanguage =
      'Staff portal';

  }


  app.innerHTML = `

    <header>

      <div class="brand">

        <b>
          MediKiosk
        </b>

        <small>
          SIH 26047 • Patient Case-Taking
        </small>

      </div>


      <div>

        <span class="pill">

          ${esc(
            headerLanguage
          )}

        </span>

      </div>

    </header>


    <main>

      <div class="page-title">

        <span class="eyebrow">
          SIH 26047
        </span>

        <h1>
          ${esc(title)}
        </h1>

      </div>


      ${body}

    </main>

  `;

}


/* =========================================================
   LANGUAGE SCREEN
========================================================= */

function lang() {

  app.innerHTML = `

    <div class="hero">

      <div class="hero-card">

        <div class="mark">
          M
        </div>


        <span class="eyebrow">
          SIH 26047 • MEDTECH / HEALTHTECH
        </span>


        <h1>
          மொழியைத் தேர்வு செய்யுங்கள்
          /
          Choose language
        </h1>


        <div class="lang-grid">

          <button
            type="button"
            onclick="setLang('Tamil')">

            தமிழ்

            <small>
              தமிழில் தொடரவும்
            </small>

          </button>


          <button
            type="button"
            onclick="setLang('English')">

            English

            <small>
              Continue in English
            </small>

          </button>

        </div>


        <div class="trust">

          🔒 Secure
          •
          🎙 Voice
          •
          ☝ Touch
          •
          👴 Elder-friendly

        </div>

      </div>

    </div>

  `;

}


/* =========================================================
   SET LANGUAGE
=====================================================*/

function setLang(language) {

  A.lang =
    language;


  localStorage.mk_lang =
    language;


  /*
   * Refresh speech voices
   * after language selection.
   */

  loadVoices();


  access();

}




function access() {

  shell(
    t('access'),

    `

      <div class="access-grid">

        <button
          class="access"
          type="button"
          onclick="patient()">

          👤

          <b>
            ${t('patient')}
          </b>

        </button>


        <button
          class="access"
          type="button"
          onclick="doctor()">

          👨‍⚕️

          <b>
            Doctor
          </b>

        </button>


        <button
          class="access"
          type="button"
          onclick="staff()">

          🧑‍💼

          <b>
            Staff
          </b>

        </button>


        <button
          class="access"
          type="button"
          onclick="admin()">

          🏥

          <b>
            Hospital Admin
          </b>

        </button>

      </div>

    `
  );

}



function patient() {

  shell(

    t('patient'),

    `

      <div class="card form">

        <div class="grid2">

          <label>

            ${t('name')}

            <input
              id="pn"
              autocomplete="name">

          </label>


          <label>

            ${t('age')}

            <input
              id="pa"
              type="number"
              min="0"
              max="120">

          </label>


          <label>

            ${t('gender')}

            <select id="pg">

              <option value="">
                ${t('select')}
              </option>

              <option value="Male">
                ${t('male')}
              </option>

              <option value="Female">
                ${t('female')}
              </option>

              <option value="Other">
                ${t('other')}
              </option>

            </select>

          </label>


          <label>

            ${t('phone')}

            <input
              id="pp"
              inputmode="tel">

          </label>


          <label>

            ${t('address')}

            <input
              id="pad">

          </label>


          <label>

            ${t('pid')}

            <input
              id="pid">

          </label>

        </div>


        <button
          class="primary"
          type="button"
          onclick="startPatient()">

          ${t('start')}

        </button>

      </div>

    `,

    true

  );

}




async function startPatient() {

  const data = {

    name:
      document
        .getElementById('pn')
        .value
        .trim(),

    age:
      document
        .getElementById('pa')
        .value
        .trim(),

    gender:
      document
        .getElementById('pg')
        .value,

    phone:
      document
        .getElementById('pp')
        .value
        .trim(),

    address:
      document
        .getElementById('pad')
        .value
        .trim(),

    patient_id:
      document
        .getElementById('pid')
        .value
        .trim()

  };


  if (
    !data.name ||
    !data.age ||
    !data.gender
  ) {

    alert(
      t('required')
    );

    return;

  }


  const r =
    await post(
      '/api/patient/start',
      data
    );


  if (!r.success) {

    alert(
      patientError(
        r.error
      )
    );

    return;

  }


  A.token =
    r.token;


  localStorage.mk_token =
    A.token;


  consult();

}


function consult() {

  shell(

    t('patient'),

    `

      <div class="mode-grid">

        <button
          type="button"
          onclick="newCase('NORMAL')">

          🩺

          <b>
            ${t('normal')}
          </b>

          <small>
            ${t('normalD')}
          </small>

        </button>


        <button
          type="button"
          onclick="newCase('AYUSH')">

          🌿

          <b>
            ${t('ayush')}
          </b>

          <small>
            ${t('ayushD')}
          </small>

        </button>

      </div>

    `,

    true

  );

}


/* =========================================================
   CREATE CASE
========================================================= */

async function newCase(mode) {

  A.mode = mode;
  A.selectedRouteKey = '';
  A.questionHistory = [];
  A.currentQuestion = null;
  A.answers = {};
  chosen = '';
  chosenRoute = '';

  const r = await post(
    '/api/case/create',
    { mode: mode, language: A.lang }
  );

  if (!r.success) {
    alert(patientError(r.error));
    return;
  }

  A.case = r.case;
  A.questionIndex = 0;
  A.questions = [];

  await question();
}


/* =========================================================
   LOAD NEXT ADAPTIVE QUESTION
========================================================= */

async function loadNextAdaptiveQuestion() {
  if (!A.case) return null;

  const r = await get(
    '/api/case/next-question?case_id=' +
    encodeURIComponent(A.case.id)
  );

  if (!r.success) {
    alert(patientError(r.error));
    return null;
  }

  return r.question || null;
}


/* =========================================================
   QUESTION SCREEN - SERVER DRIVEN ADAPTIVE FLOW
========================================================= */

/* =========================================================
   QUESTION SCREEN - SERVER DRIVEN ADAPTIVE FLOW
========================================================= */

/* =========================================================
   QUESTION SCREEN - SERVER DRIVEN ADAPTIVE FLOW
========================================================= */

let questionSpeechTimer = null;

async function question(autoSpeak = true) {

  if (!A.case) return;

  const q =
    A.currentQuestion ||
    await loadNextAdaptiveQuestion();

  if (!q) {
    historyStep();
    return;
  }

  const uiQuestion = {
    key: q.key,
    q: q.question,

    options: (q.options || []).map(option => ({
      label:
        typeof option === 'object'
          ? String(
              option.label ??
              option.value ??
              ''
            )
          : String(option ?? ''),

      route:
        typeof option === 'object'
          ? String(
              option.route ??
              option.routeKey ??
              ''
            )
          : ''
    })),

    adaptive: q.adaptive,
    reason: q.reason,
    section: q.section
  };


  A.currentQuestion =
    uiQuestion;

  A.questions =
    [uiQuestion];


  const saved =
    A.answers[uiQuestion.key] ||
    null;


  const savedValue =
    saved
      ? String(saved.value || '')
      : '';


  const savedRoute =
    saved
      ? String(saved.routeKey || '')
      : '';


  chosen =
    savedValue;

  chosenRoute =
    savedRoute;

  A.selectedRouteKey =
    savedRoute;


  const options =
    uiQuestion.options
      .map(
        (option, index) => `

          <button
            type="button"
            class="answer-option${
              String(option.label) === savedValue
                ? ' selected'
                : ''
            }"
            data-option-index="${index}">

            ${esc(option.label)}

          </button>

        `
      )
      .join('');


  const backButton =
    A.questionHistory.length > 0
      ? `

        <button
          class="secondary"
          type="button"
          id="backQuestion">

          ← ${t('back')}

        </button>

      `
      : '';


  shell(

    t('patient'),

    `

      <div class="card question">

        <div class="progress">

          ${t('progress')}

          ${A.questionHistory.length + 1}

        </div>


        <h2>
          ${esc(uiQuestion.q)}
        </h2>


        <button
          class="secondary"
          type="button"
          id="hearQuestion">

          ${t('voice')}

        </button>


        <div class="options">

          ${options}

        </div>


        <label>

          ${t('answer')}

          <input
            id="ans"
            value="${esc(savedValue)}"
            placeholder="${esc(t('placeholder'))}"
            autocomplete="off">

        </label>


        <button
          class="secondary"
          type="button"
          id="voiceAnswer">

          ${t('mic')}

        </button>


        <div class="question-actions">

          ${backButton}


          <button
            class="primary"
            type="button"
            id="nextQuestion">

            ${t('next')}

          </button>

        </div>

      </div>

    `,

    true

  );


  const hearButton =
    document.getElementById(
      'hearQuestion'
    );


  if (hearButton) {

    hearButton.addEventListener(
      'click',
      () => {

        if (questionSpeechTimer) {
          clearTimeout(questionSpeechTimer);
          questionSpeechTimer = null;
        }

        speechSynthesis.cancel();

        setTimeout(() => {

          loadVoices();

          if (
            'speechSynthesis' in window &&
            speechSynthesis.paused
          ) {
            speechSynthesis.resume();
          }

          speak(uiQuestion.q);

        }, 100);

      }
    );

  }


  const voiceButton =
    document.getElementById(
      'voiceAnswer'
    );


  if (voiceButton) {

    voiceButton.addEventListener(
      'click',
      () => voiceInput()
    );

  }


  const backButtonElement =
    document.getElementById(
      'backQuestion'
    );


  if (backButtonElement) {

    backButtonElement.addEventListener(
      'click',
      () => goBack()
    );

  }


  const nextButton =
    document.getElementById(
      'nextQuestion'
    );


  if (nextButton) {

    nextButton.addEventListener(
      'click',
      () => sendAns()
    );

  }


  document
    .querySelectorAll(
      '.answer-option'
    )
    .forEach(button => {

      button.addEventListener(
        'click',
        () => {

          const index =
            Number(
              button.dataset.optionIndex
            );


          const selected =
            uiQuestion.options[index];


          if (!selected) return;


          ans(
            selected.label,
            selected.route || ''
          );


          document
            .querySelectorAll(
              '.answer-option'
            )
            .forEach(btn =>
              btn.classList.remove(
                'selected'
              )
            );


          button.classList.add(
            'selected'
          );


          const input =
            document.getElementById(
              'ans'
            );


          if (input) {

            input.value =
              selected.label;

          }

        }
      );

    });


  /*
   * Automatic question voice.
   * Back flow calls question(false),
   * then speaks the restored question itself.
   */

  if (autoSpeak) {

    if (questionSpeechTimer) {
      clearTimeout(
        questionSpeechTimer
      );
    }


    questionSpeechTimer =
      setTimeout(() => {

        questionSpeechTimer =
          null;

        loadVoices();

        if (
          'speechSynthesis' in window &&
          speechSynthesis.paused
        ) {
          speechSynthesis.resume();
        }

        speak(
          uiQuestion.q
        );

      }, 500);

  }

}
/* =========================================================
   SEND ANSWER - UPSERT + FRESH ADAPTIVE CALCULATION
========================================================= */

async function sendAns() {

  const q = A.currentQuestion;
  if (!q) return;

  const input = document.getElementById('ans');
  const value = (input?.value || '').trim();

  if (!value) {
    alert(t('answerRequired'));
    return;
  }

  const old = A.answers[q.key] || {};
  const routeKey = old.routeKey || A.selectedRouteKey || '';

  // Keep only the path that is still active when an earlier answer is edited.
  const activeKeys = A.questionHistory.map(x => x.key);
  activeKeys.push(q.key);

  const r = await post(
    '/api/case/answer',
    {
      case_id: A.case.id,
      question_key: q.key,
      question: q.q,
      answer: value,
      active_question_keys: activeKeys
    }
  );

  if (!r.success) {
    alert(patientError(r.error));
    return;
  }

  // Mirror the server-side branch pruning in the local UI state too.
  // This prevents stale answers from an old branch appearing later.
  const activeSet = new Set(activeKeys);
  Object.keys(A.answers).forEach(key => {
    if (!activeSet.has(key)) delete A.answers[key];
  });

  A.answers[q.key] = {
    value: value,
    routeKey: routeKey,
    serverValue: value
  };

  // Store the exact question answered so Back restores it.
  if (!A.questionHistory.some(x => x.key === q.key)) {
    A.questionHistory.push({ ...q });
  }

  A.questionIndex = A.questionHistory.length;
  A.currentQuestion = null;
  A.selectedRouteKey = '';
  chosen = '';
  chosenRoute = '';

  await question();
}


async function goBack() {

  if (
    !A.questionHistory ||
    A.questionHistory.length === 0
  ) {
    return;
  }


  /*
   * Cancel any pending question speech
   * before restoring the previous question.
   */

  if (questionSpeechTimer) {

    clearTimeout(
      questionSpeechTimer
    );

    questionSpeechTimer =
      null;

  }


  if (
    'speechSynthesis' in window
  ) {

    speechSynthesis.cancel();

  }


  const previous =
    A.questionHistory.pop();


  if (!previous) return;


  A.currentQuestion = {
    ...previous
  };


  A.questionIndex =
    A.questionHistory.length;


  const saved =
    A.answers[previous.key] ||
    {};


  A.selectedRouteKey =
    saved.routeKey || '';


  chosen =
    saved.value || '';


  chosenRoute =
    saved.routeKey || '';


  /*
   * Render previous question
   * WITHOUT automatic speech.
   */

  await question(false);


  /*
   * Speak restored question
   * only after UI is rendered.
   */

  setTimeout(() => {

    loadVoices();

    if (
      'speechSynthesis' in window &&
      speechSynthesis.paused
    ) {

      speechSynthesis.resume();

    }


    speak(
      previous.q
    );

  }, 700);

}

/* =========================================================
   SELECTED ANSWER STATE
========================================================= */

let chosen = '';
let chosenRoute = '';

function ans(label, routeKey = '') {

  chosen = label;
  chosenRoute = routeKey;
  A.selectedRouteKey = routeKey;

  if (A.currentQuestion) {
    A.answers[A.currentQuestion.key] = {
      ...(A.answers[A.currentQuestion.key] || {}),
      value: label,
      routeKey: routeKey
    };
  }
}


/* =========================================================
   PREVIOUS MEDICAL HISTORY
========================================================= */

function historyStep() {

  shell(

    t('history'),

    `

      <div class="card center">

        <h2>
          ${t('history')}
        </h2>


        <div class="yesno">

          <button
            type="button"
            onclick="documentStep()">

            ${t('yes')}

          </button>


          <button
            type="button"
            onclick="summaryStep()">

            ${t('no')}

          </button>

        </div>

      </div>

    `,

    true

  );

}


/* =========================================================
   DOCUMENT SCAN
========================================================= */

function documentStep() {

  shell(

    t('upload'),

    `

      <div class="card">

        <div class="scan-hero">

          <div class="scan-icon">
            📷
          </div>


          <div>

            <h2>
              ${t('scanTitle')}
            </h2>


            <p>
              ${t('scanText')}
            </p>

          </div>

        </div>


        <input
          id="doc"
          type="file"
          accept="image/*,.pdf,.txt,.docx"
          capture="environment">


        <button
          class="secondary"
          type="button"
          onclick="camera()">

          ${t('scan')}

        </button>


        <textarea
          id="doctext"
          rows="7"
          placeholder="${esc(
            t('scanHelp')
          )}"></textarea>


        <button
          class="primary"
          type="button"
          onclick="saveDoc()">

          ${t('finish')}

        </button>

      </div>

    `,

    true

  );

}


/* =========================================================
   CAMERA
========================================================= */

function camera() {

  alert(
    t('cameraHelp')
  );

}


/* =========================================================
   SAVE DOCUMENT
========================================================= */

async function saveDoc() {

  const file =
    document
      .getElementById('doc')
      ?.files
      ?. [0];


  const text =
    document
      .getElementById('doctext')
      ?.value
      ?.trim() ||
    '';


  const r =
    await post(
      '/api/case/document',

      {

        case_id:
          A.case.id,

        name:
          file
            ? file.name
            : (
                tamil()
                  ? 'கேமரா ஸ்கேன்'
                  : 'Camera scan'
              ),

        text:
          text

      }
    );


  if (!r.success) {

    alert(
      patientError(
        r.error
      )
    );

    return;

  }


  summaryStep();

}


/* =========================================================
   SUMMARY
========================================================= */

async function summaryStep() {

  const r =
    await post(
      '/api/case/complete',

      {
        case_id:
          A.case.id
      }
    );


  if (!r.success) {

    alert(
      patientError(
        r.error
      )
    );

    return;

  }


  A.case =
    r.case;


  /*
   * Generate patient token.
   */

  const tok =
    await post(
      '/api/case/token',

      {
        case_id:
          A.case.id
      }
    );


  if (!tok.success) {

    alert(
      patientError(
        tok.error
      )
    );

    return;

  }


  A.case =
    tok.case;


  const department =
    localRoute(
      r.department
    );


  const priority =
    priorityLabel(
      A.case.priority
    );


  const historyText =
    A.case.summary
      ?.previous_medical_history ||
    t('noHistoryDoc');


  shell(

    t('summary'),

    `

      <div class="summary">

        <div class="summary-head">

          <span class="badge">

            ${esc(
              t('route')
            )}

          </span>


          <h2>

            ${esc(
              department
            )}

          </h2>


          <div class="token">

            ${t('token')}

            <strong>

              ${esc(
                A.case.token ||
                ''
              )}

            </strong>

          </div>

        </div>


        <section>

          <h3>
            ${t('clinicalSummary')}
          </h3>


          <p>

            <b>
              ${t('safety')}:
            </b>

            ${esc(
              priority
            )}

          </p>


          <p>

            ${esc(
              A.case.summary
                ?.chief_complaint ||
              (
                tamil()
                  ? 'தகவல் வழங்கப்படவில்லை'
                  : 'Not provided'
              )
            )}

          </p>


          <p>

            ${esc(
              historyText
            )}

          </p>


          <small>

            ${t('aiDraft')}

          </small>

        </section>


        <div class="card center">

          <h3>
            ${t('routeReady')}
          </h3>


          <p>
            ${t('tokenReady')}
          </p>

        </div>


        <button
          class="primary"
          type="button"
          onclick="printToken()">

          🖨 ${t('print')}

        </button>


        <button
          class="secondary"
          type="button"
          onclick="access()">

          ${t('dashboard')}

        </button>

      </div>

    `,

    true

  );

}


/* =========================================================
   PRIORITY TRANSLATION
========================================================= */

function priorityLabel(value) {

  if (!tamil()) {

    return (
      value ||
      'NORMAL'
    );

  }


  const map = {

    URGENT:
      'அவசரம்',

    HIGH:
      'அதிக முன்னுரிமை',

    NORMAL:
      'சாதாரணம்'

  };


  return (

    map[value] ||
    value ||
    'சாதாரணம்'

  );

}


/* =========================================================
   PRINT TOKEN
========================================================= */

function printToken() {

  const title =
    tamil()
      ? 'நோயாளர் டோக்கன்'
      : 'Patient Token';


  const tokenText =
    tamil()
      ? 'டோக்கன் எண்'
      : 'Token Number';


  const deptText =
    tamil()
      ? 'துறை'
      : 'Department';


  const department =
    localRoute(
      A.case
        ?.department_name ||
      A.case
        ?.department ||
      ''
    );


  const w =
    window.open(
      '',
      '_blank'
    );


  if (!w) {

    return;

  }


  w.document.write(`

    <!doctype html>

    <html
      lang="${tamil() ? 'ta' : 'en'}">

    <head>

      <meta
        charset="UTF-8">

      <title>
        ${esc(title)}
      </title>

    </head>


    <body
      style="
        font-family:Arial,sans-serif;
        text-align:center;
        padding:48px
      ">

      <h1>
        MediKiosk
      </h1>


      <h2>
        ${esc(title)}
      </h2>


      <div
        style="
          font-size:72px;
          font-weight:700;
          margin:30px
        ">

        ${esc(
          A.case?.token ||
          ''
        )}

      </div>


      <p>

        ${esc(tokenText)}:

        ${esc(
          A.case?.token ||
          ''
        )}

      </p>


      <p>

        ${esc(deptText)}:

        ${esc(department)}

      </p>

    </body>

    </html>

  `);


  w.document.close();

  w.focus();

  w.print();

}


/* =========================================================
   DOCTOR LOGIN
========================================================= */

function doctor() {

  shell(

    'Doctor Login',

    `

      <div class="card form">

        <label>

          Current doctor name

          <input
            id="dn">

        </label>


        <label>

          Department

          <select id="de">

            ${
              [
                'General Medicine',
                'Cardiology',
                'Pulmonology',
                'Orthopaedics',
                'Dermatology',
                'Ayurveda'
              ]
              .map(
                x =>
                  `<option>
                    ${x}
                  </option>`
              )
              .join('')
            }

          </select>

        </label>


        <label>

          Department email

          <input
            id="deemail">

        </label>


        <label>

          Department password

          <input
            id="depass"
            type="password">

        </label>


        <button
          class="primary"
          type="button"
          onclick="doctorLogin()">

          Secure login

        </button>

      </div>

    `

  );

}


/* =========================================================
   DOCTOR LOGIN ACTION
========================================================= */

async function doctorLogin() {

  const r =
    await post(

      '/api/auth/login',

      {

        type:
          'DOCTOR',

        doctor_name:
          document
            .getElementById(
              'dn'
            )
            .value
            .trim(),

        email:
          document
            .getElementById(
              'deemail'
            )
            .value
            .trim(),

        password:
          document
            .getElementById(
              'depass'
            )
            .value

      }

    );


  if (!r.success) {

    return alert(
      r.error ||
      'Invalid credentials'
    );

  }


  A.token =
    r.token;


  A.role =
    'DOCTOR';


  localStorage.mk_token =
    A.token;


  A.lastDoctor =
    r;


  doctorDash(r);

}


/* =========================================================
   DOCTOR DASHBOARD
========================================================= */

async function doctorDash(
  info = A.lastDoctor || {}
) {

  const r =
    await get(
      '/api/cases'
    );


  const rows =
    (r.cases || [])
      .map(
        c => `

          <div class="row">

            <b>

              ${esc(
                c.token ||
                c.id
              )}

            </b>


            <span>

              ${esc(
                c.status
              )}

              •

              ${esc(
                c.priority
              )}

            </span>


            <button
              type="button"
              onclick="review(${JSON.stringify(c.id)})">

              Open

            </button>

          </div>

        `
      )
      .join('')

    ||

    `

      <div class="empty">

        ${t('noCases')}

      </div>

    `;


  shell(

    'Doctor Dashboard',

    `

      <div class="stats">

        <div>

          <b>

            ${esc(
              info.doctor_name ||
              'Current Doctor'
            )}

          </b>


          <span>

            ${esc(
              info.department ||
              info.department_name ||
              ''
            )}

          </span>

        </div>


        <div>

          <b>

            ${esc(
              info.shift ||
              'Shift'
            )}

          </b>


          <span>
            ACTIVE
          </span>

        </div>

      </div>


      <div class="card">

        <h3>
          Today’s patient queue
        </h3>


        ${rows}

      </div>


      <button
        class="secondary"
        type="button"
        onclick="logoutPortal()">

        Logout

      </button>

    `

  );

}


/* =========================================================
   DOCTOR REVIEW
========================================================= */

async function review(id) {

  const r =
    await get(
      '/api/case?id=' +
      encodeURIComponent(id)
    );


  if (!r.case) {

    return alert(
      r.error ||
      'Case not found'
    );

  }


  const c =
    r.case;


  const answers =
    (c.answers || [])
      .map(
        x => `

          <p>

            <b>

              ${esc(
                x.question
              )}

            </b>

            <br>

            ${esc(
              x.answer
            )}

          </p>

        `
      )
      .join('');


  shell(

    'Clinical Review',

    `

      <div class="card">

        <h2>

          ${esc(
            c.token ||
            c.id
          )}

        </h2>


        <p>

          <b>

            ${esc(
              c.priority
            )}

          </b>

          •

          ${esc(
            c.status
          )}

        </p>


        <h3>
          Patient history
        </h3>


        ${answers}


        <h3>
          Clinical summary
        </h3>


        <p>

          ${esc(
            c.summary
              ?.chief_complaint ||
            'Not provided'
          )}

        </p>


        <textarea
          id="note"
          rows="5"
          placeholder="Doctor note"></textarea>


        <button
          class="primary"
          type="button"
          onclick="
            reviewSave(
              ${JSON.stringify(c.id)},
              'IN_CONSULTATION'
            )
          ">

          Start consultation

        </button>


        <button
          class="secondary"
          type="button"
          onclick="
            reviewSave(
              ${JSON.stringify(c.id)},
              'COMPLETED'
            )
          ">

          Complete patient

        </button>

      </div>

    `

  );

}


/* =========================================================
   DOCTOR REVIEW SAVE
========================================================= */

async function reviewSave(
  id,
  status
) {

  const note =
    document
      .getElementById(
        'note'
      )
      ?.value ||
    '';


  const r =
    await post(

      '/api/case/review',

      {

        case_id:
          id,

        status:
          status,

        note:
          note

      }

    );


  if (!r.success) {

    return alert(
      r.error ||
      'Could not save review'
    );

  }


  alert(
    'Saved'
  );


  doctorDash(
    A.lastDoctor ||
    {}
  );

}


/* =========================================================
   STAFF LOGIN
========================================================= */

function staff() {

  shell(

    'Staff Login',

    `

      <div class="card form">

        <label>

          Staff email

          <input
            id="se">

        </label>


        <label>

          Staff password

          <input
            id="sp"
            type="password">

        </label>


        <button
          class="primary"
          type="button"
          onclick="staffLogin()">

          Secure login

        </button>

      </div>

    `

  );

}


/* =========================================================
   STAFF LOGIN ACTION
========================================================= */

async function staffLogin() {

  const r =
    await post(

      '/api/auth/login',

      {

        type:
          'STAFF',

        email:
          document
            .getElementById(
              'se'
            )
            .value
            .trim(),

        password:
          document
            .getElementById(
              'sp'
            )
            .value

      }

    );


  if (!r.success) {

    return alert(
      r.error ||
      'Invalid credentials'
    );

  }


  A.token =
    r.token;


  A.role =
    'STAFF';


  localStorage.mk_token =
    A.token;


  staffDash();

}


/* =========================================================
   STAFF DASHBOARD
========================================================= */

async function staffDash() {

  const r =
    await get(
      '/api/cases'
    );


  const alerts =
    (r.cases || [])
      .filter(
        c =>
          c.priority ===
            'URGENT' ||

          c.priority ===
            'HIGH'
      )
      .map(
        c => `

          <div class="alert">

            <b>

              ${esc(
                c.token ||
                c.id
              )}

            </b>

            •

            ${esc(
              c.priority
            )}


            <span>

              ${esc(
                c.status
              )}

            </span>

          </div>

        `
      )
      .join('')

    ||

    `

      <div class="empty">

        ${t('noAlerts')}

      </div>

    `;


  shell(

    'Staff Triage Dashboard',

    `

      <div class="card">

        <h3>
          🚨 Safety alerts
        </h3>


        ${alerts}

      </div>


      <div class="card">

        <h3>
          Patient queue
        </h3>


        ${(r.cases || [])
          .map(
            c => `

              <div class="row">

                <b>

                  ${esc(
                    c.token ||
                    c.id
                  )}

                </b>


                <span>

                  ${esc(
                    c.status
                  )}

                  •

                  ${esc(
                    c.department_id ||
                    ''
                  )}

                </span>

              </div>

            `
          )
          .join('')}

      </div>


      <button
        class="secondary"
        type="button"
        onclick="logoutPortal()">

        Logout

      </button>

    `

  );

}


/* =========================================================
   ADMIN LOGIN
========================================================= */

function admin() {

  shell(

    'Hospital Admin Login',

    `

      <div class="card form">

        <label>

          Admin email

          <input
            id="ae"
            value="admin@hospital.local">

        </label>


        <label>

          Admin password

          <input
            id="ap"
            type="password">

        </label>


        <button
          class="primary"
          type="button"
          onclick="adminLogin()">

          Secure login

        </button>

      </div>

    `

  );

}


/* =========================================================
   ADMIN LOGIN ACTION
========================================================= */

async function adminLogin() {

  const r =
    await post(

      '/api/auth/login',

      {

        type:
          'ADMIN',

        email:
          document
            .getElementById(
              'ae'
            )
            .value
            .trim(),

        password:
          document
            .getElementById(
              'ap'
            )
            .value

      }

    );


  if (!r.success) {

    return alert(
      r.error ||
      'Invalid credentials'
    );

  }


  A.token =
    r.token;


  A.role =
    'ADMIN';


  localStorage.mk_token =
    A.token;


  adminDash();

}


/* =========================================================
   ADMIN DASHBOARD
========================================================= */

async function adminDash() {

  const r =
    await get(
      '/api/state'
    );


  const deps =
    (r.departments || [])
      .map(
        d => `

          <div class="row">

            <b>

              ${esc(
                d.name
              )}

            </b>


            <span>

              ${esc(
                d.email
              )}

              •

              ${esc(
                d.shift
              )}

            </span>


            <span>

              ${
                d.active
                  ? 'ACTIVE'
                  : 'INACTIVE'
              }

            </span>

          </div>

        `
      )
      .join('');


  shell(

    'Hospital Admin Dashboard',

    `

      <div class="stats">

        <div>

          <b>

            ${
              r.departments?.length ||
              0
            }

          </b>


          <span>
            Departments
          </span>

        </div>


        <div>

          <b>
            ${r.patients || 0}
          </b>


          <span>
            Patients
          </span>

        </div>


        <div>

          <b>
            ${r.cases || 0}
          </b>


          <span>
            Cases
          </span>

        </div>

      </div>


      <div class="card">

        <h3>
          Manage departments
        </h3>


        ${deps}


        <hr>


        <h3>
          Create department
        </h3>


        <div class="grid2">

          <input
            id="nd"
            placeholder="Department name">


          <input
            id="ne"
            placeholder="Department email">


          <input
            id="np"
            placeholder="Department password"
            type="password">


          <input
            id="ns"
            placeholder="09:00 AM - 01:00 PM">

        </div>


        <button
          class="primary"
          type="button"
          onclick="createDept()">

          Create department

        </button>

      </div>


      <div class="card">

        <h3>
          Security & audit log
        </h3>


        ${(r.audit || [])
          .map(
            x => `

              <div class="row">

                <span>

                  ${esc(
                    x.time
                  )}

                </span>


                <span>

                  ${esc(
                    x.actor
                  )}

                </span>


                <span>

                  ${esc(
                    x.action
                  )}

                </span>

              </div>

            `
          )
          .join('')}

      </div>


      <button
        class="secondary"
        type="button"
        onclick="logoutPortal()">

        Logout

      </button>

    `

  );

}


/* =========================================================
   CREATE DEPARTMENT
========================================================= */

async function createDept() {

  const r =
    await post(

      '/api/admin/department',

      {

        name:
          document
            .getElementById(
              'nd'
            )
            .value
            .trim(),

        email:
          document
            .getElementById(
              'ne'
            )
            .value
            .trim(),

        password:
          document
            .getElementById(
              'np'
            )
            .value,

        shift:
          document
            .getElementById(
              'ns'
            )
            .value
            .trim()

      }

    );


  if (!r.success) {

    return alert(
      r.error ||
      'Could not create department'
    );

  }


  adminDash();

}


/* =========================================================
   LOGOUT
========================================================= */

function logoutPortal() {

  A.token =
    '';

  A.role =
    '';

  A.case =
    null;

  A.questions =
    [];

  A.questionIndex =
    0;

  localStorage.removeItem(
    'mk_token'
  );


  access();

}


/* =========================================================
   PATIENT ERROR TRANSLATION
========================================================= */

function patientError(
  error
) {

  if (!tamil()) {

    return (
      error ||
      'Something went wrong.'
    );

  }


  const map = {

    'Name, age and gender are required':
      'பெயர், வயது மற்றும் பாலினத்தை உள்ளிட வேண்டும்.',

    'Patient session required':
      'நோயாளர் அமர்வு தேவைப்படுகிறது.',

    'Access denied':
      'அனுமதி மறுக்கப்பட்டது.',

    'Case not found':
      'வழக்கு கிடைக்கவில்லை.',

    'Server connection failed.':
      'சேவையகத்துடன் இணைக்க முடியவில்லை.'

  };


  return (

    map[error] ||

    error ||

    'ஏதோ ஒரு பிழை ஏற்பட்டுள்ளது.'

  );

}


/* =========================================================
   POST API
========================================================= */

async function post(
  url,
  data
) {

  try {

    const r =
      await fetch(

        url,

        {

          method:
            'POST',

          headers: {

            'Content-Type':
              'application/json',

            'Authorization':
              'Bearer ' +
              A.token

          },

          body:
            JSON.stringify(
              data
            )

        }

      );


    return await r.json();

  }

  catch (error) {

    console.error(
      error
    );


    return {

      success:
        false,

      error:
        'Server connection failed.'

    };

  }

}


/* =========================================================
   GET API
========================================================= */

async function get(
  url
) {

  try {

    const r =
      await fetch(

        url,

        {

          headers: {

            'Authorization':
              'Bearer ' +
              A.token

          }

        }

      );


    return await r.json();

  }

  catch (error) {

    console.error(
      error
    );


    return {

      success:
        false,

      error:
        'Server connection failed.'

    };

  }

}


/* =========================================================
   INITIALISE
========================================================= */

loadVoices();

lang();