const A={
    lang: localStorage.mk_lang || 'English',
    token: localStorage.mk_token || '',
    role: '',
    case: null,
    session: null,
    questionIndex: 0,
    questions: [],
    answers: {},
    mode: '',
    detectedSymptoms: [],
    patient: null,
    frontTab: (localStorage.mk_front_tab && !['api_connect','doc_chat'].includes(localStorage.mk_front_tab) ) ? localStorage.mk_front_tab : 'intake_bot',
    voiceAutoReply: localStorage.mk_voice_auto !== '0'
};
let patientRecognition = null;
let patientVoiceTimer = null;
let patientVoiceActive = false;
const I={
    English:{
        choose:'Choose language',access:'Choose access',patient:'Patient',doctor:'Doctor',staff:'Staff',admin:'Hospital Admin',
        name:'Patient name',age:'Age',gender:'Gender',phone:'Phone (optional)',address:'Area / address (optional)',pid:'Existing Patient ID (optional)',
        start:'Start',normal:'Normal Consultation',normalD:'General medical consultation',ayush:'AYUSH Consultation',ayushD:'Ayurveda / Siddha / other AYUSH care',
        voice:'🔊 Hear question',mic:'🎙 Speak answer',next:'Next',back:'Back',home:'Home',history:'Previous medical history?',yes:'Yes',no:'No',
        upload:'Upload / scan report',finish:'Finish history',summary:'Clinical summary',route:'Department',token:'Patient token',print:'Print token',
        startC:'Start consultation',complete:'Complete patient',save:'Save review',dashboard:'Dashboard',logout:'Logout',active:'ACTIVE',
        dept:'Department',email:'Department email',pass:'Department password',doctorName:'Doctor name',shift:'Shift',login:'Secure login',
        staffEmail:'Staff email',staffPass:'Staff password',adminEmail:'Admin email',adminPass:'Admin password',manage:'Manage departments',
        create:'Create department',deptName:'Department name',newEmail:'Department email',newPass:'Department password',stats:'Hospital overview',
        audit:'Security & audit log',answer:'Answer',placeholder:'Type or use voice',interview:'Adaptive clinical interview',
        docChat:'AI Doc Analyzer & Chat',docChatD:'OCR scan reports/prescriptions & interactive AI clinical Q&A',
        setupBot:'Set Up Intake Chatbot',setupBotD:'Start patient consultation intake with adaptive clinical questioning',
        connectApi:'Connect APIs (Gemini & OpenRouter)',connectApiD:'Live ping test, manage keys & select models',
        voiceAssign:'Voice Assignment',voiceAssignD:'Configure Tamil/English voice synthesis & speech input'
    },
    Tamil:{
        choose:'மொழியை தேர்வு செய்யுங்கள்',access:'யார் தொடர்கிறீர்கள்?',patient:'நோயாளர்',doctor:'மருத்துவர்',staff:'பணியாளர்',admin:'மருத்துவமனை நிர்வாகம்',
        name:'நோயாளர் பெயர்',age:'வயது',gender:'பாலினம்',phone:'தொலைபேசி (விருப்பம்)',address:'பகுதி / முகவரி',pid:'முந்தைய Patient ID (விருப்பம்)',
        start:'தொடங்குங்கள்',normal:'பொது மருத்துவ ஆலோசனை',normalD:'பொதுவான மருத்துவ பிரச்சனைக்காக',ayush:'AYUSH ஆலோசனை',ayushD:'ஆயுர்வேதம் / சித்தா / பிற AYUSH சேவைக்காக',
        voice:'🔊 கேள்வியை கேளுங்கள்',mic:'🎙 பதிலை பேசுங்கள்',next:'அடுத்து',back:'பின்',home:'முகப்பு',history:'முந்தைய மருத்துவ வரலாறு உள்ளதா?',yes:'ஆம்',no:'இல்லை',
        upload:'அறிக்கையை upload செய்யவும்',finish:'முடிக்கவும்',summary:'மருத்துவ சுருக்கம்',route:'துறை',token:'நோயாளர் token',print:'Token print',
        startC:'ஆலோசனை தொடங்கு',complete:'முடிக்கவும்',save:'Review சேமிக்கவும்',dashboard:'Dashboard',logout:'வெளியேறு',active:'ACTIVE',
        dept:'துறை',email:'துறை மின்னஞ்சல்',pass:'துறை கடவுச்சொல்',doctorName:'மருத்துவர் பெயர்',shift:'பணி நேரம்',login:'பாதுகாப்பான உள்நுழைவு',
        staffEmail:'Staff மின்னஞ்சல்',staffPass:'Staff கடவுச்சொல்',adminEmail:'Admin மின்னஞ்சல்',adminPass:'Admin கடவுச்சொல்',manage:'துறைகளை நிர்வகிக்கவும்',
        create:'துறை உருவாக்கவும்',deptName:'துறை பெயர்',newEmail:'துறை மின்னஞ்சல்',newPass:'துறை கடவுச்சொல்',stats:'மருத்துவமனை நிலவரம்',
        audit:'Audit log',answer:'பதில்',placeholder:'தட்டச்சு செய்யவும் அல்லது பேசவும்',interview:'தகவமைப்பு மருத்துவ நேர்காணல்',
        docChat:'AI ஆவண பகுப்பாய்வு & அரட்டை',docChatD:'மருத்துவ அறிக்கைகள் OCR & AI நேரடி ஆவண கலந்துரையாடல்',
        setupBot:'மருத்துவ உட்கொள்ளல் சாட்பாட்',setupBotD:'தகவமைப்பு மருத்துவ நேர்காணல் & மருத்துவர் சுருக்கம்',
        connectApi:'AI API அமைப்புகள் (Gemini & OpenRouter)',connectApiD:'Gemini 3.6 & OpenRouter நேரடி இணைப்பு சோதனை & அமைப்புகள்',
        voiceAssign:'குரல் தேர்வு & அமைப்புகள்',voiceAssignD:'தமிழ் / ஆங்கில குரல் ஒலிப்பு & மைக்ரோஃபோன் அமைப்பு'
    }
};

let voiceConfig = {
    tamilVoice: localStorage.mk_voice_ta || '',
    englishVoice: localStorage.mk_voice_en || '',
    rate: parseFloat(localStorage.mk_voice_rate || '1.0'),
    pitch: parseFloat(localStorage.mk_voice_pitch || '1.0')
};

let apiState = {
    gemini: { has_key: true, status: 'CONFIGURED', model: 'gemini-3.6-flash' },
    openrouter: { has_key: true, status: 'CONFIGURED', model: 'meta-llama/llama-3.3-70b-instruct' }
};

const t=k=>I[A.lang]?.[k]||k,app=document.getElementById('app');
function esc(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#039;')}

let ttsActive = false;
let ttsPaused = false;
let currentVoiceText = '';
let currentVoiceLang = '';
let questionSpeechTimer = null;
let navigationHistory = [];
let currentScreen = {key:'home',render:()=>lang()};

function navigateTo(key,render){
    if(currentScreen && currentScreen.key!==key){
        currentScreen.formState=captureFormState();
        navigationHistory.push(currentScreen);
    }
    currentScreen={key,render};
    render();
}

function captureFormState(){
    const state={};
    app.querySelectorAll('input[id],textarea[id],select[id]').forEach(element=>{
        if(element.type!=='password'&&element.type!=='file'){
            state[element.id]=element.value;
        }
    });
    return state;
}

function restoreFormState(state){
    if(!state) return;
    for(const [id,value] of Object.entries(state)){
        const element=document.getElementById(id);
        if(element) element.value=value;
    }
}

function goBack(){
    const previous=navigationHistory.pop();
    if(!previous) return;
    if(currentScreen?.key==='patient-question'){
        if(questionSpeechTimer){
            clearTimeout(questionSpeechTimer);
            questionSpeechTimer=null;
        }
        stopTTS();
    }
    currentScreen=previous;
    previous.render();
    restoreFormState(previous.formState);
}

function pauseTTS(){
    if('speechSynthesis' in window && speechSynthesis.speaking && !speechSynthesis.paused){
        speechSynthesis.pause();
        ttsPaused = true;
        updateTTSControlsUI('PAUSED');
    }
}

function resumeTTS(){
    if('speechSynthesis' in window && speechSynthesis.paused){
        speechSynthesis.resume();
        ttsPaused = false;
        updateTTSControlsUI('SPEAKING');
    }
}

function stopTTS(){
    if('speechSynthesis' in window){
        speechSynthesis.cancel();
    }
    ttsActive = false;
    ttsPaused = false;
    currentVoiceText = '';
    updateTTSControlsUI('STOPPED');
}

function updateTTSControlsUI(state){
    const isTa = (typeof docChatLang !== 'undefined' && docChatLang === 'Tamil');
    const headerStopBtn = document.getElementById('doc-tts-stop-btn');
    const headerPauseBtn = document.getElementById('doc-tts-pause-btn');
    const statusBadge = document.getElementById('doc-speaking-badge');

    if(state === 'SPEAKING'){
        if(headerStopBtn) headerStopBtn.style.display = 'inline-flex';
        if(headerPauseBtn){
            headerPauseBtn.style.display = 'inline-flex';
            headerPauseBtn.innerHTML = `⏸ ${isTa ? 'இடைநிறுத்து' : 'Pause'}`;
        }
        if(statusBadge){
            statusBadge.innerHTML = isTa ? '● பேசுகிறது' : '● Speaking';
            statusBadge.style.color = '#e53e3e';
        }
    } else if(state === 'PAUSED'){
        if(headerStopBtn) headerStopBtn.style.display = 'inline-flex';
        if(headerPauseBtn){
            headerPauseBtn.style.display = 'inline-flex';
            headerPauseBtn.innerHTML = `▶️ ${isTa ? 'தொடரவும்' : 'Resume'}`;
        }
        if(statusBadge){
            statusBadge.innerHTML = isTa ? '⏸ இடைநிறுத்தப்பட்டது' : '⏸ Paused';
            statusBadge.style.color = '#d97706';
        }
    } else { // STOPPED
        if(headerStopBtn) headerStopBtn.style.display = 'none';
        if(headerPauseBtn) headerPauseBtn.style.display = 'none';
        if(statusBadge){
            statusBadge.innerHTML = isTa ? '● நிறுத்தப்பட்டது' : '● Stopped';
            statusBadge.style.color = '#718096';
        }
        document.querySelectorAll('.btn-inline-tts-pause').forEach(btn => {
            btn.style.display = 'none';
        });
        document.querySelectorAll('.btn-inline-tts-stop').forEach(btn => {
            btn.style.display = 'none';
        });
    }
}

function toggleInlineTTS(btn, txt, lang){
    if(ttsActive && !ttsPaused){
        pauseTTS();
    } else if(ttsActive && ttsPaused){
        resumeTTS();
    } else {
        speak(txt, lang);
    }
}

function speak(text, explicitLang){
    if(!('speechSynthesis' in window)) return;
    speechSynthesis.cancel();
    ttsActive = true;
    ttsPaused = false;
    currentVoiceText = text;
    currentVoiceLang = explicitLang;

    const u = new SpeechSynthesisUtterance(text);
    const voices = speechSynthesis.getVoices();
    const curLang = (typeof docChatLang !== 'undefined') ? docChatLang : A.lang;
    const useTamil = explicitLang ? (explicitLang === 'Tamil') : (curLang === 'Tamil');

    if(useTamil){
        u.lang = 'ta-IN';
        if(voiceConfig.tamilVoice){
            const v = voices.find(x => x.name === voiceConfig.tamilVoice);
            if(v) u.voice = v;
        } else {
            const v = voices.find(x => x.lang && x.lang.toLowerCase().startsWith('ta'));
            if(v) u.voice = v;
        }
    } else {
        u.lang = 'en-IN';
        if(voiceConfig.englishVoice){
            const v = voices.find(x => x.name === voiceConfig.englishVoice);
            if(v) u.voice = v;
        }
    }

    u.rate = voiceConfig.rate || 1.0;
    u.pitch = voiceConfig.pitch || 1.0;

    u.onstart = () => {
        ttsActive = true;
        ttsPaused = false;
        updateTTSControlsUI('SPEAKING');
    };

    u.onpause = () => {
        ttsPaused = true;
        updateTTSControlsUI('PAUSED');
    };

    u.onresume = () => {
        ttsPaused = false;
        updateTTSControlsUI('SPEAKING');
    };

    u.onend = u.onerror = () => {
        ttsActive = false;
        ttsPaused = false;
        updateTTSControlsUI('STOPPED');
    };

    speechSynthesis.speak(u);
}

/**
 * CLIENT-SIDE language detection.
 * Detects Tamil Unicode, Tanglish, and English.
 * Returns 'Tamil' or 'English'.
 * This is the PRIMARY language signal sent to the backend.
 */
function detectMessageLanguage(text){
    if(!text || !text.trim()) return A.lang || 'English';

    // 1. Tamil Unicode characters
    if(/[\u0B80-\u0BFF]/.test(text)) return 'Tamil';

    const t = text.toLowerCase().trim();

    // 2. Strong Tanglish word patterns (frequently used in Tamil spoken in English letters)
    const tanglishStrong = [
        /\b(enna|epdi|eppadi|eppo|eppothu|enga|engae|yen|yean|edhuku|ethuku|yaaru|yaar)\b/,
        /\b(irukku|iruku|irukanga|illai|illa|seri|seri|venuma|vendam|venda)\b/,
        /\b(evlo|evalavu|romba|konjam|niraiya|adhigama|kuravaga|kuranja)\b/,
        /\b(idhu|ithu|adhu|athu|indha|andha|inga|anga|avan|aval|avanga)\b/,
        /\b(sollunga|solunga|sollu|paaru|paathu|theriyuma|theriyala|theriyathu)\b/,
        /\b(marundhu|marunthu|maathirai|mathirai|valikudhu|valikuthu|vali)\b/,
        /\b(report|blood|sugar|bp|hemoglobin|platelet|wbc|rbc)\s+(la|le|oda|ku|ah|aa)\b/,
        /\b(normal|abnormal|low|high|ok)\s*(ah|aa|dha|tha|na|naa)\b/,
        /\b(enna|en)\s+(irukku|solludu|pannudu|aaguthu)\b/,
        /\b(naan|naanum|ungaluku|ungaloda|unaku|unoda)\b/,
        /\b(paakalam|parkalam|seyyalam|seyalam|mudiyuma|mudiyathu)\b/,
        /\b(doctor|maamiyal|doctor|vaidhiyan|vaithiyan)\b.*\b(kitta|kita|pakkam)\b/,
        /\b(intha|antha|ithu|adhu)\s+(report|test|result|value)\b/,
        /\b(oda|ku|la|le)\s+(enna|evlo|evvalo|ethanai)\b/,
        /(ah|aa)\s*\?/,
        /\b(nalla|nallaa|ketta|kettaa|seri|seeri)\b/,
        /\b(avlo|avvalo|appadi|ippadi|ipdi|apdi)\b/,
        /\b(maruthuvar|maruthuvam|hospital|clinic)\s*(ku|kku|la|le|pakkam)\b/
    ];
    for(const pat of tanglishStrong){
        if(pat.test(t)) return 'Tamil';
    }

    // 3. If user's UI language is Tamil, treat ambiguous short inputs as Tamil
    if(A.lang === 'Tamil' && t.split(' ').length <= 4) return 'Tamil';

    return 'English';
}

function shell(title,body,options={}){
    app.innerHTML=`<header>
        <div class="brand" style="cursor:pointer" onclick="goHome()"><b>MediKiosk</b><small>SIH 26047 • AI-assisted clinical intake</small></div>
        <div style="display:flex;align-items:center;gap:10px">
            <span class="status-pill online" onclick="openApiModal()" title="AI Status">🟢 Local Gemma 4 E4B</span>
            <span class="status-pill ready" onclick="openVoiceModal()" title="Voice Settings">🎙 Voice</span>
            <span class="pill">${A.lang}</span>
            ${navigationHistory.length&&!options.hideBack?`<button type="button" class="secondary" style="padding:6px 12px;font-size:12px;margin:0" onclick="goBack()">← ${t('back')}</button>`:''}
            <button type="button" class="secondary" style="padding:6px 12px;font-size:12px;margin:0" onclick="goHome()">🏠 Home</button>
        </div>
    </header>
    <main><div class="page-title"><span class="eyebrow">SIH 26047</span><h1>${title}</h1></div>${body}</main>`;
}

function goHome(){
    navigationHistory=[];
    currentScreen={key:'home',render:()=>lang()};
    if(questionSpeechTimer){
        clearTimeout(questionSpeechTimer);
        questionSpeechTimer = null;
    }
    stopTTS();
    A.case = null;
    A.questions = [];
    A.questionIndex = 0;
    A.questionHistory = [];
    A.currentQuestion = null;
    A.answers = {};
    A.selectedRouteKey = '';
    if(typeof chosen !== 'undefined') chosen = '';
    if(typeof chosenRoute !== 'undefined') chosenRoute = '';
    lang();
}

async function refreshApiStatus(){
    try {
        const r = await fetch('/api/ai/config').then(x=>x.json());
        if(r.success){
            apiState = r;
            const elG = document.getElementById('gemini-badge');
            const elO = document.getElementById('openrouter-badge');
            const isOnline = (r.ollama && r.ollama.status === 'ONLINE') || (r.gemini && r.gemini.has_key);
            if(elG) {
                elG.className = isOnline ? 'status-pill online' : 'status-pill ready';
                elG.textContent = isOnline ? '🟢 Gemma 4 E4B Active' : '🟡 Ollama Offline';
            }
            if(elO) {
                elO.className = 'status-pill online';
                elO.textContent = '⚡ 100% Local AI';
            }
        }
    } catch(e){}
}

function lang(resetNavigation=true){
    if(resetNavigation){
        navigationHistory=[];
        currentScreen={key:'home',render:()=>lang()};
    }
    app.innerHTML = `
    <div class="hero">
      <div class="hero-card wide">
        <div class="top-bar">
          <div style="display:flex;align-items:center;gap:10px">
            <div class="mark" style="width:44px;height:44px;font-size:22px;border-radius:12px">M</div>
            <div style="text-align:left">
              <b style="font-size:16px;color:#0b756b">MediKiosk</b>
              <div style="font-size:11px;color:#6d8487">SIH 26047 • AI HEALTHCARE KIOSK</div>
            </div>
          </div>
          <div class="api-status-group">
            <span id="gemini-badge" class="status-pill online" title="Local Gemma 4 E4B Active via Ollama">
              🟢 Gemma 4 E4B Active
            </span>
            <span id="openrouter-badge" class="status-pill online" title="100% Local AI Inference">
              ⚡ 100% Local AI
            </span>
            <span class="status-pill ready" onclick="switchFrontTab('voice_assign')" title="Configure Voice Output & Mic" style="cursor:pointer">
              🎙️ Voice Config
            </span>
            <div class="lang-toggle">
              <button class="${A.lang==='Tamil'?'active':''}" onclick="setLangInstant('Tamil')">தமிழ்</button>
              <button class="${A.lang==='English'?'active':''}" onclick="setLangInstant('English')">English</button>
            </div>
          </div>
        </div>

        <span class="eyebrow">SIH 26047 • HEALTHCARE KIOSK & CLINICAL AI</span>
        <h1 style="margin:12px 0 6px 0">${A.lang==='Tamil' ? 'மெடிகியோஸ்க் AI சுகாதார தளம்' : 'MediKiosk AI Healthcare Portal'}</h1>
        <p style="color:#5e7577;margin:0 auto 16px auto;max-width:680px;font-size:14px">
          ${A.lang==='Tamil' 
            ? 'அதிநவீன மருத்துவ ஆவண பகுப்பாய்வு, AI நோயாளி அரட்டை & குரல் அமைப்புகள் அனைத்தும் ஒரே பக்கத்தில்.' 
            : 'Interactive medical document analyzer, clinical consultation chatbot & voice synthesis directly on your front page.'}
        </p>

        <!-- Front Page Tabs -->
        <div class="front-tabs">
          ${currentScreen?.key.startsWith('home-tab-')&&navigationHistory.length?`<button type="button" class="secondary" onclick="goBack()">← ${t('back')}</button>`:''}
          <button class="front-tab-btn ${(A.frontTab||'intake_bot')==='intake_bot'?'active':''}" onclick="switchFrontTab('intake_bot')">
            🤖 ${A.lang==='Tamil'?'நோயாளி நேர்காணல்':'Intake Chatbot'}
          </button>
          <button class="front-tab-btn ${A.frontTab==='doc_chat'?'active':''}" onclick="switchFrontTab('doc_chat')">
            📄 ${A.lang==='Tamil'?'AI ஆவண அரட்டை':'AI Doc Chatbot'}
          </button>
          <button class="front-tab-btn ${A.frontTab==='voice_assign'?'active':''}" onclick="switchFrontTab('voice_assign')">
            🎙️ ${A.lang==='Tamil'?'குரல் தேர்வு':'Voice Assignment'}
          </button>
        </div>

        <!-- Active Tab Content Area -->
        <div id="front-tab-container">
          ${renderFrontTabContent()}
        </div>

        <!-- Portal Access now lives inside intake_bot tab -->

        <div class="trust" style="font-size:13px;margin-top:20px">
          🔒 Secure • 🎙 Voice Enabled • ☝ Touch Friendly • 🧠 Adaptive Clinical Intake • 🤖 Local Gemma 4 E4B (Ollama)
        </div>
      </div>
    </div>
    <div id="modal-root"></div>
    `;
    refreshApiStatus();
}

function switchFrontTab(tab){
    if(tab === 'api_connect') tab = 'intake_bot';
    const previousTab=A.frontTab||'intake_bot';
    if(tab===previousTab) return lang(false);
    currentScreen.render=()=>{
        A.frontTab=previousTab;
        localStorage.mk_front_tab=previousTab;
        lang(false);
    };
    A.frontTab = tab;
    localStorage.mk_front_tab = tab;
    navigateTo(`home-tab-${tab}`,()=>{
        A.frontTab=tab;
        localStorage.mk_front_tab=tab;
        lang(false);
    });
}

function renderFrontTabContent(){
    const tab = A.frontTab || 'intake_bot';

    if(tab === 'doc_chat'){
        const isTa = (docChatLang === 'Tamil');
        const activeCount = (patientSession?.reports && patientSession.reports.length) || (currentDocAnalysis ? 1 : 0);
        const dtStr = currentDocAnalysis ? translateDocType(currentDocAnalysis.analysis?.document_type) : (isTa ? 'அறிக்கை' : 'Report');
        const badgeLabel = isTa
            ? (activeCount > 1 ? `✓ ${activeCount} அறிக்கைகள் தயார்` : `✓ ${dtStr} தயார்`)
            : (activeCount > 1 ? `✓ ${activeCount} Reports Ready` : `✓ ${currentDocAnalysis?.analysis?.document_type || 'Report'} Ready`);
        return `
        <div class="doc-chat-wrapper" style="margin-top:10px">
          <!-- Left: Document Upload & Extraction -->
          <div class="doc-panel">
            <h3 id="doc-panel-title" style="margin:0 0 10px 0;font-size:16px;color:#102a2d">📄 ${isTa?'மருத்துவ அறிக்கை பதிவேற்றம்':'Upload Medical Report'}</h3>

            <div class="sample-docs-bar">
              <span id="doc-sample-label" style="font-size:11px;font-weight:700;color:#0b756b;align-self:center">${isTa?'மாதிரி:':'Sample:'}</span>
              <button id="sample-btn-blood" onclick="loadSampleDoc('blood_test')">🩸 ${isTa?'இரத்த பரிசோதனை':'Blood Test'}</button>
              <button id="sample-btn-rx" onclick="loadSampleDoc('prescription')">💊 ${isTa?'மருந்துச் சீட்டு':'Prescription'}</button>
              <button id="sample-btn-discharge" onclick="loadSampleDoc('discharge')">🏥 ${isTa?'டிஸ்சார்ஜ் சுருக்கம்':'Discharge'}</button>
            </div>

            <!-- Dual Intake Options: Upload vs Scan -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">
              <button id="doc-btn-upload" class="primary" style="margin:0;padding:12px 10px;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:6px" onclick="document.getElementById('direct-file-input').click()">
                <span>📄</span> <span id="doc-btn-upload-text">${isTa?'அறிக்கை பதிவேற்று':'Upload Report'}</span>
              </button>
              <button id="doc-btn-scan" class="primary" style="margin:0;padding:12px 10px;font-size:13px;font-weight:700;background:#0d655d;display:flex;align-items:center;justify-content:center;gap:6px" onclick="openMedicalReportScanner()">
                <span>🖨️</span> <span id="doc-btn-scan-text">${isTa?'அறிக்கை ஸ்கேன் செய்':'Scan Medical Report'}</span>
              </button>
            </div>
            <div id="doc-scan-helper" style="font-size:11px;color:#6b8284;margin:-4px 0 10px 2px">
              ${isTa?'இணைக்கப்பட்ட மருத்துவ ஆவண ஸ்கேனர் அல்லது கேமரா மூலம் காகித அறிக்கையை ஸ்கேன் செய்யவும்.':'Scan a physical medical report using the connected scanner / camera.'}
            </div>

            <div class="doc-upload-zone" id="doc-drop-zone"
                 onclick="document.getElementById('direct-file-input').click()"
                 ondragover="event.preventDefault(); this.classList.add('dragover');"
                 ondragleave="this.classList.remove('dragover');"
                 ondrop="event.preventDefault(); this.classList.remove('dragover'); handleDropUpload(event);"
                 style="padding:16px;margin-bottom:10px">
              <input id="direct-file-input" type="file" accept=".pdf,.png,.jpg,.jpeg,.docx,.txt" style="display:none" onchange="handleDirectFileUpload(this)">
              <div style="font-size:24px;margin-bottom:4px" id="doc-upload-icon">📂</div>
              <b id="doc-upload-title" style="color:#0b756b;font-size:13px">${isTa?'அறிக்கை கோப்பை பதிவேற்ற கிளிக் செய்யவும் அல்லது இழுத்து விடவும்':'Click or drag & drop image / PDF report'}</b>
              <div id="doc-upload-sub" style="font-size:11px;color:#6b8284">${isTa?'PNG, JPG, PDF, DOCX (அதிகபட்சம் 16MB)':'PNG, JPG, PDF, DOCX (Max 16MB)'}</div>
            </div>

            <!-- Multi-Report Container for Active Patient -->
            <div id="doc-reports-list" class="doc-reports-container" style="display:${(patientSession?.reports && patientSession.reports.length)?'flex':'none'}"></div>

            <textarea id="direct-doc-text" rows="3" placeholder="${isTa?'அல்லது மருந்துச் சீட்டு / ஆய்வக அறிக்கை உரையை இங்கு ஒட்டவும்...':'Or paste prescription / lab report text here...'}" style="font-size:12px"></textarea>

            <div style="display:flex;gap:8px;margin-top:10px">
              <button id="analyze-btn" class="primary" style="flex:1;margin:0;padding:10px" onclick="runDirectDocAnalyze()">
                ✨ ${isTa?'AI கொண்டு பகுப்பாய்வு செய்':'Analyze with AI'}
              </button>
              <button id="doc-clear-btn" class="secondary" style="margin:0;padding:10px" onclick="clearDocAnalyzer()">${isTa?'அழி':'Clear'}</button>
            </div>

            <!-- Analysis Output -->
            <div id="doc-analysis-results" style="display:${currentDocAnalysis?'block':'none'}">
              <div class="doc-facts-box" id="doc-facts-content"></div>
            </div>
          </div>

          <!-- Right: Document Chatbot Stream -->
          <div class="chat-window">
            <div class="chat-window-head">
              <div style="display:flex;align-items:center;gap:8px">
                <span class="mark" style="width:28px;height:28px;font-size:14px;border-radius:8px">AI</span>
                <div>
                  <b id="doc-chatbot-title" style="font-size:13px;color:#102a2d">${isTa?'மருத்துவ ஆவண சாட்பாட்':'AI Document Chatbot'}</b>
                  <div id="doc-chatbot-sub" style="font-size:10px;color:#0b756b">● ${isTa?'உள்ளூர் AI உதவியாளர் (Gemma 4 E4B)':'Local AI Assistant (Gemma 4 E4B)'}</div>
                </div>
              </div>
              <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
                <span id="doc-active-badge" style="display:${activeCount>0?'inline-flex':'none'};font-size:11px;padding:3px 9px;border-radius:12px;background:#e6f4ea;color:#137333;font-weight:700">
                  ${badgeLabel}
                </span>
                <div class="lang-toggle" id="doc-lang-toggle" style="margin:0">
                  <button id="doc-btn-ta" class="${isTa?'active':''}" onclick="setDocChatLang('Tamil')">தமிழ்</button>
                  <button id="doc-btn-en" class="${!isTa?'active':''}" onclick="setDocChatLang('English')">English</button>
                </div>
                <button id="voice-toggle-btn" class="secondary" style="padding:4px 8px;font-size:11px;margin:0" onclick="toggleVoiceAutoReply()">
                  ${A.voiceAutoReply !== false ? (isTa ? '🔊 குரல் பதில்: ஆன்' : '🔊 Voice Reply: ON') : (isTa ? '🔈 குரல் பதில்: ஆஃப்' : '🔈 Voice Reply: OFF')}
                </button>
                <button id="doc-read-aloud-btn" class="secondary" style="padding:4px 8px;font-size:11px;margin:0" onclick="speakDocContext()">🔊 ${isTa?'வாசிக்கவும்':'Read Aloud'}</button>
                <button id="doc-tts-pause-btn" class="secondary" style="padding:4px 8px;font-size:11px;margin:0;display:none" onclick="ttsPaused ? resumeTTS() : pauseTTS()">⏸ ${isTa?'இடைநிறுத்து':'Pause'}</button>
                <button id="doc-tts-stop-btn" class="secondary" style="padding:4px 8px;font-size:11px;margin:0;display:none;color:#c5221f" onclick="stopTTS()">⏹ ${isTa?'நிறுத்து':'Stop'}</button>
              </div>
            </div>

            <div class="chat-stream" id="doc-chat-stream">
              <div class="chat-bubble bot" id="doc-chat-welcome">
                ${isTa
                  ? 'வணக்கம்! இடதுபுறத்தில் ஒரு மருத்துவ அறிக்கையை பதிவேற்றவும் அல்லது மாதிரியைத் தேர்ந்தெடுக்கவும். நான் அதை ஆய்வு செய்து, உங்கள் கேள்விகளுக்கு எளிய முறையில் பதிலளிப்பேன்.'
                  : 'Hello! Upload a medical report on the left or select a sample. I will extract findings and answer any questions about your diagnosis, tests, and medications.'}
              </div>
            </div>

            <!-- Suggested chips - Language aware -->
            <div class="chat-prompt-chips" id="doc-chat-chips">
              ${isTa ? `
              <button onclick="askDocQuick('இந்த அறிக்கையை எளிய தமிழில் விளக்குங்கள்')">💡 எளிதாக விளக்கு</button>
              <button onclick="askDocQuick('எந்த test result abnormal-ஆக உள்ளது?')">⚠️ Abnormal values?</button>
              <button onclick="askDocQuick('என் report-ல் உள்ள medications என்ன?')">💊 மருந்துகள்</button>
              <button onclick="askDocQuick('நான் எந்த doctor-ஐ பார்க்க வேண்டும்?')">👨‍⚕️ எந்த doctor?</button>
              <button onclick="askDocQuick('என் report-ல் உள்ள முக்கியமான விவரங்கள் என்ன?')">📋 முக்கிய விவரங்கள்</button>
              ` : `
              <button onclick="askDocQuick('Explain this report in simple words')">💡 Explain simply</button>
              <button onclick="askDocQuick('Are any of my test results abnormal?')">⚠️ Any abnormal values?</button>
              <button onclick="askDocQuick('What are the prescribed medications?')">💊 Medications</button>
              <button onclick="askDocQuick('Which doctor specialty should I visit?')">👨‍⚕️ Which doctor?</button>
              <button onclick="askDocQuick('தமிழில் இந்த அறிக்கையின் முக்கிய விவரங்களை விளக்குங்கள்')">🇮🇳 தமிழில் விளக்குக</button>
              `}
            </div>

            <!-- Input Bar -->
            <div class="chat-input-bar">
              <input id="doc-chat-input" placeholder="${isTa?'கேள்வி கேட்கவும் (அல்லது மைக் அழுத்தவும்)...':'Ask anything about this report...'}" onkeydown="if(event.key==='Enter')sendDocChatMessage()">
              <button id="doc-chat-mic" class="chat-mic-btn" onclick="toggleDocChatMic()" title="Voice input">🎙️</button>
              <button id="doc-chat-send-btn" class="chat-send-btn" onclick="sendDocChatMessage()">${isTa?'அனுப்பு':'Send'}</button>
            </div>
          </div>
        </div>
        `;
    }

    if(tab === 'intake_bot'){
        const isTamil = A.lang === 'Tamil';
        return `
        <div class="intake-dual-layout">

          <!-- LEFT: Patient language-selection card -->
          <div class="intake-lang-card">

            <div class="intake-logo-mark">M</div>
            <div class="intake-brand-sub">SIH 26047 &bull; HEALTHCARE KIOSK</div>

            <h2 class="intake-lang-heading">
              ${ isTamil ? 'மொழியைத் தேர்வு செய்யுங்கள்' : 'Choose language' }
            </h2>

            <div class="intake-lang-grid">
              <button class="intake-lang-btn" onclick="selectIntakeLang('Tamil')">
                <span class="intake-lang-label">தமிழ்</span>
                <span class="intake-lang-sub">தமிழில் தொடரவும்</span>
              </button>
              <button class="intake-lang-btn" onclick="selectIntakeLang('English')">
                <span class="intake-lang-label">English</span>
                <span class="intake-lang-sub">Continue in English</span>
              </button>
            </div>

            <div class="intake-trust-bar">
              🔒 Secure &nbsp;&bull;&nbsp; 🎙 Voice &nbsp;&bull;&nbsp; ☝ Touch &nbsp;&bull;&nbsp; 🧠 Adaptive &nbsp;&bull;&nbsp; 🤖 OpenRouter AI
            </div>

          </div>

          <!-- RIGHT: Portal Access card -->
          <div class="portal-access-card">
            <div class="portal-access-header">
              <div class="portal-access-icon">⚕️</div>
              <div>
                <div class="portal-access-title">${ isTamil ? 'தொகுதி அணுகல்' : 'Portal Access' }</div>
                <div class="portal-access-subtitle">${ isTamil ? 'பணியாளர் / நிர்வாக உள்நுழைவு' : 'Staff & Admin Login' }</div>
              </div>
            </div>

            <div class="portal-btn-list">

              <button class="portal-entry-btn" onclick="doctor()">
                <span class="portal-entry-icon">👨‍⚕️</span>
                <span class="portal-entry-body">
                  <span class="portal-entry-label">${ isTamil ? 'மருத்துவர்' : 'Doctor' }</span>
                  <span class="portal-entry-desc">${ isTamil ? 'மருத்துவர் டாஷ்போர்டு' : 'Open Doctor Dashboard' }</span>
                </span>
                <span class="portal-entry-arrow">›</span>
              </button>

              <button class="portal-entry-btn" onclick="staff()">
                <span class="portal-entry-icon">🧑‍💼</span>
                <span class="portal-entry-body">
                  <span class="portal-entry-label">${ isTamil ? 'பணியாளர்' : 'Staff' }</span>
                  <span class="portal-entry-desc">${ isTamil ? 'பணியாளர் டாஷ்போர்டு' : 'Open Staff Dashboard' }</span>
                </span>
                <span class="portal-entry-arrow">›</span>
              </button>

              <button class="portal-entry-btn" onclick="admin()">
                <span class="portal-entry-icon">🏥</span>
                <span class="portal-entry-body">
                  <span class="portal-entry-label">${ isTamil ? 'மருத்துவமனை நிர்வாகி' : 'Hospital Admin' }</span>
                  <span class="portal-entry-desc">${ isTamil ? 'நிர்வாக பலகை' : 'Hospital Administration' }</span>
                </span>
                <span class="portal-entry-arrow">›</span>
              </button>

            </div>
          </div>

        </div>
        `;
    }

    if(tab === 'voice_assign'){
        const voices = ('speechSynthesis' in window) ? speechSynthesis.getVoices() : [];
        const tamilVoices = voices.filter(v => v.lang.includes('ta') || v.name.toLowerCase().includes('tamil'));
        const englishVoices = voices.filter(v => v.lang.includes('en'));

        const optTa = tamilVoices.map(v => `<option value="${esc(v.name)}" ${voiceConfig.tamilVoice===v.name?'selected':''}>${esc(v.name)} (${v.lang})</option>`).join('') ||
            `<option value="">Default System Tamil / Indian Voice</option>`;

        const optEn = englishVoices.map(v => `<option value="${esc(v.name)}" ${voiceConfig.englishVoice===v.name?'selected':''}>${esc(v.name)} (${v.lang})</option>`).join('') ||
            `<option value="">Default System English Voice</option>`;

        return `
        <div style="text-align:left;max-width:820px;margin:10px auto">
          <div class="voice-config-grid">
            <div class="api-provider-card">
              <b>🇮🇳 ${A.lang==='Tamil'?'தமிழ் குரல் அமைப்பு':'Tamil Voice Assignment'}</b>
              <label style="font-size:12px;display:block;margin:8px 0 4px 0">TTS Voice Profile</label>
              <select id="v-ta" style="width:100%;padding:10px;border-radius:10px;border:1px solid #cbdad8">
                ${optTa}
              </select>
              <button class="primary" style="margin-top:14px;padding:9px 14px;font-size:13px" onclick="testVoiceSpeak('Tamil')">
                🔊 ${A.lang==='Tamil'?'தமிழில் ஒலித்துப்பார்':'Test Tamil Voice'}
              </button>
            </div>

            <div class="api-provider-card">
              <b>🌐 ${A.lang==='Tamil'?'ஆங்கில குரல் அமைப்பு':'English Voice Assignment'}</b>
              <label style="font-size:12px;display:block;margin:8px 0 4px 0">TTS Voice Profile</label>
              <select id="v-en" style="width:100%;padding:10px;border-radius:10px;border:1px solid #cbdad8">
                ${optEn}
              </select>
              <button class="primary" style="margin-top:14px;padding:9px 14px;font-size:13px;background:#185abc" onclick="testVoiceSpeak('English')">
                🔊 Test English Voice
              </button>
            </div>
          </div>

          <div class="api-provider-card">
            <b>🎚️ Speech Pitch & Speed (Rate)</b>
            <div class="voice-slider-group">
              <label><span>Speed (Speech Rate)</span><span id="rate-val">${voiceConfig.rate}x</span></label>
              <input id="v-rate" type="range" min="0.7" max="1.4" step="0.1" value="${voiceConfig.rate}" oninput="document.getElementById('rate-val').textContent=this.value+'x'">
            </div>
            <div class="voice-slider-group">
              <label><span>Pitch</span><span id="pitch-val">${voiceConfig.pitch}</span></label>
              <input id="v-pitch" type="range" min="0.8" max="1.3" step="0.1" value="${voiceConfig.pitch}" oninput="document.getElementById('pitch-val').textContent=this.value">
            </div>
          </div>

          <div style="display:flex;justify-content:flex-end;margin-top:12px">
            <button class="primary" onclick="saveVoiceAssignment()">💾 Save Voice Settings</button>
          </div>
        </div>
        `;
    }

    return '';
}

function launchIntakeFromFront(){
    const name = document.getElementById('front-pn')?.value.trim() || '';
    const age = document.getElementById('front-pa')?.value || '';
    const mode = document.querySelector('input[name="front-mode"]:checked')?.value || 'NORMAL';

    A.patientDraft = {
        name: name,
        age: age,
        gender: '',
        phone: '',
        address: '',
        pid: ''
    };
    A.mode = mode;

    patientContinue();
}


/* Called from language-selection card inside Intake Chatbot tab.
   Sets language, then immediately launches the patient intake form. */
function selectIntakeLang(l){
    A.lang = l;
    localStorage.mk_lang = l;
    A.patientDraft = { name:'', age:'', gender:'', phone:'', address:'', pid:'' };
    patient();
}

function setLangInstant(l){
    A.lang = l;
    localStorage.mk_lang = l;
    lang();
}

function startChatbotFlow(){
    patient();
}

function setLang(l){A.lang=l;localStorage.mk_lang=l;patient()}
function access(){patient()}
function patient(){
    A.patientDraft={name:'',age:'',gender:'',phone:'',address:'',pid:''};
    return navigateTo('patient-intake',()=>renderPatient());
}

function renderPatient(){

    stopPatientVoiceFlow();

    shell(t('patient'),`
        <div class="card form elderly-form">

            <div id="voice-status" class="voice-status">
                🔊 ${A.lang==='Tamil'
                    ? 'உங்கள் பெயரை சொல்லுங்கள்'
                    : 'Please say your name'}
            </div>

            <label>${t('name')}
                <input id="pn" class="large-input" autocomplete="name" value="${esc(A.patientDraft.name||'')}">
            </label>

            <label>${t('age')}
                <input id="pa" class="large-input" type="number" min="0" value="${esc(A.patientDraft.age||'')}">
            </label>

            <div id="voice-listening" class="listening">
                🎙 ${A.lang==='Tamil'
                    ? 'கேட்டுக்கொண்டிருக்கிறது...'
                    : 'Listening...'}
            </div>

            <button class="primary large-button" onclick="patientContinue()">
                ${t('next')} →
            </button>
        </div>
    `);

    startPatientVoiceFlow();
}

function speakThen(text, callback){
    if(!('speechSynthesis' in window)){
        callback();
        return;
    }

    speechSynthesis.cancel();

    const u=new SpeechSynthesisUtterance(text);
    u.lang=A.lang==='Tamil'?'ta-IN':'en-IN';

    u.onend=()=>{
        setTimeout(callback,500);
    };

    speechSynthesis.speak(u);
}


function startPatientVoiceFlow(){
    stopPatientVoiceFlow();

    patientVoiceActive = true;

    const prompt = A.lang==='Tamil'
        ? 'உங்கள் பெயரை சொல்லுங்கள்'
        : 'Please say your name';

    speakThen(prompt,()=>{
        if(patientVoiceActive){
            listenForPatient('name');
        }
    });
}

function extractAge(text){

    const direct=text.match(/\b([1-9]|[1-9][0-9]|1[01][0-9]|120)\b/);

    if(direct){
        return parseInt(direct[1],10);
    }

    const words={
        'one':1,'two':2,'three':3,'four':4,'five':5,
        'ten':10,'twenty':20,'thirty':30,'forty':40,
        'fifty':50,'sixty':60,'seventy':70,'eighty':80,
        'ninety':90,

        'ஒன்று':1,'இரண்டு':2,'மூன்று':3,'நான்கு':4,'ஐந்து':5,
        'பத்து':10,'இருபது':20,'முப்பது':30,'நாற்பது':40,
        'ஐம்பது':50,'அறுபது':60,'எழுபது':70,'எண்பது':80,
        'தொண்ணூறு':90
    };

    const clean=text.toLowerCase().trim();

    if(words[clean]) return words[clean];

    return null;
}

function stopPatientVoiceFlow(){
    patientVoiceActive = false;

    if(patientVoiceTimer){
        clearTimeout(patientVoiceTimer);
        patientVoiceTimer = null;
    }

    if(patientRecognition){
        try{
            patientRecognition.onresult = null;
            patientRecognition.onend = null;
            patientRecognition.onerror = null;
            patientRecognition.stop();
        }catch(e){}

        patientRecognition = null;
    }

    if('speechSynthesis' in window){
        speechSynthesis.cancel();
    }
}

function listenForPatient(type){

    if(!patientVoiceActive) return;

    if(!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)){
        return;
    }

    const R=window.SpeechRecognition || window.webkitSpeechRecognition;
    const r=new R();

    patientRecognition=r;

    r.lang=A.lang==='Tamil' ? 'ta-IN' : 'en-IN';
    r.continuous=false;
    r.interimResults=false;
    r.maxAlternatives=3;

    const status=document.getElementById('voice-status');

    const question = type==='name'
        ? (A.lang==='Tamil'
            ? 'உங்கள் பெயரை சொல்லுங்கள்'
            : 'Please say your name')
        : (A.lang==='Tamil'
            ? 'உங்கள் வயது என்ன?'
            : 'What is your age?');

    if(status){
        status.textContent='🎙 '+question;
    }

    r.onresult=e=>{

        if(!patientVoiceActive) return;

        const text=(e.results[0][0].transcript || '').trim();

        if(!text){
            retryPatientVoice(type);
            return;
        }

        if(type==='name'){

            const input=document.getElementById('pn');

            if(!input) return;

            input.value=text;
            A.patientDraft.name=text;

            // NAME RECEIVED → immediately move to AGE
            patientVoiceActive=true;

            speakThen(
                A.lang==='Tamil'
                    ? 'உங்கள் வயது என்ன?'
                    : 'What is your age?',
                ()=>{
                    if(patientVoiceActive){
                        listenForPatient('age');
                    }
                }
            );

        }else{

            const age=extractAge(text);
            const input=document.getElementById('pa');

            if(age && age>=1 && age<=120){

                input.value=age;
                A.patientDraft.age=age;

                // AGE RECEIVED → STOP INTAKE VOICE
                stopPatientVoiceFlow();

                // Go directly to gender
                setTimeout(()=>{
                    patientGender();
                },200);

            }else{

                retryPatientVoice('age');
            }
        }
    };

    r.onend=()=>{

        if(!patientVoiceActive) return;

        const currentValue =
            type==='name'
                ? document.getElementById('pn')?.value.trim()
                : document.getElementById('pa')?.value.trim();

        // If user typed the value manually,
        // DO NOT repeat the voice question.
        if(currentValue){

            if(type==='name'){

                A.patientDraft.name=currentValue;

                speakThen(
                    A.lang==='Tamil'
                        ? 'உங்கள் வயது என்ன?'
                        : 'What is your age?',
                    ()=>{
                        if(patientVoiceActive){
                            listenForPatient('age');
                        }
                    }
                );

            }else{

                const age=extractAge(currentValue);

                if(age && age>=1 && age<=120){

                    A.patientDraft.age=age;
                    stopPatientVoiceFlow();

                    setTimeout(()=>{
                        patientGender();
                    },200);

                }
            }

            return;
        }

        // Nothing entered → repeat
        patientVoiceTimer=setTimeout(()=>{
            if(patientVoiceActive){
                retryPatientVoice(type);
            }
        },800);
    };

    r.onerror=()=>{

        if(!patientVoiceActive) return;

        patientVoiceTimer=setTimeout(()=>{
            if(patientVoiceActive){
                retryPatientVoice(type);
            }
        },800);
    };

    try{
        r.start();
    }catch(e){

        patientVoiceTimer=setTimeout(()=>{
            if(patientVoiceActive){
                retryPatientVoice(type);
            }
        },1000);
    }
}


function retryPatientVoice(type){

    const question = type==='name'
        ? (A.lang==='Tamil'
            ? 'உங்கள் பெயர் எனக்கு கிடைக்கவில்லை'
            : 'Please say your name')
        : (A.lang==='Tamil'
            ? 'உங்கள் வயது எனக்கு கிடைக்கவில்லை'
            : 'What is your age');

    speakThen(question,()=>{
        listenForPatient(type);
    });
}

function patientContinue(){

    const name=document.getElementById('pn')?.value.trim();
    const age=document.getElementById('pa')?.value.trim();

    if(!name || !age){
        return alert(
            A.lang==='Tamil'
            ? 'பெயர் மற்றும் வயதை சொல்லுங்கள்.'
            : 'Please provide your name and age.'
        );
    }

    A.patientDraft.name=name;
    A.patientDraft.age=age;

    // User manually continued → stop voice completely
    stopPatientVoiceFlow();

    patientGender();
}

function patientGender(){
    return navigateTo('patient-gender',()=>renderPatientGender());
}

function renderPatientGender(){
    // Gender page வந்தவுடன் intake voice முழுமையாக STOP
    stopPatientVoiceFlow();

    shell(t('patient'),`
        <div class="card form elderly-form">
            <h2>${A.lang==='Tamil'?'பாலினத்தை தேர்வு செய்யுங்கள்':'Choose gender'}</h2>

            <div class="gender-buttons">
                <button onclick="selectGender('Male')">
                    👨<br>
                    ${A.lang==='Tamil' ? 'ஆண்' : 'Male'}
                </button>

                <button onclick="selectGender('Female')">
                    👩<br>
                    ${A.lang==='Tamil' ? 'பெண்' : 'Female'}
                </button>

                <button onclick="selectGender('Other')">
                    👤<br>
                    ${A.lang==='Tamil' ? 'மற்றவை' : 'Other'}
                </button>
            </div>

            <div class="optional-section">
                <label>${t('phone')}
                    <input id="pp" class="large-input" type="tel" value="${esc(A.patientDraft.phone||'')}">
                </label>

                <label>${t('address')}
                    <input id="pad" class="large-input" value="${esc(A.patientDraft.address||'')}">
                </label>

                <label>${t('pid')}
                    <input id="pid" class="large-input" value="${esc(A.patientDraft.pid||'')}">
                </label>
            </div>

            ${navigationHistory.length?`<button type="button" class="secondary large-button" onclick="backFromPatientGender()">← ${t('back')}</button>`:''}
        </div>
    `,{hideBack:true});
}

function backFromPatientGender(){
    A.patientDraft.phone=document.getElementById('pp')?.value||'';
    A.patientDraft.address=document.getElementById('pad')?.value||'';
    A.patientDraft.pid=document.getElementById('pid')?.value||'';
    goBack();
}

function selectGender(gender){
    A.patientDraft.gender=gender;

    A.patientDraft.phone=document.getElementById('pp')?.value||'';
    A.patientDraft.address=document.getElementById('pad')?.value||'';
    A.patientDraft.pid=document.getElementById('pid')?.value||'';

    startPatient();
}

function patientVoice(target){
    if(!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)){
        return alert(
            A.lang==='Tamil'
            ? 'இந்த browser-ல் voice input இல்லை.'
            : 'Voice input is unavailable in this browser.'
        );
    }

    const R=window.SpeechRecognition||window.webkitSpeechRecognition;
    const r=new R();

    r.lang=A.lang==='Tamil'?'ta-IN':'en-IN';
    r.interimResults=false;
    r.maxAlternatives=1;

    r.onresult=e=>{
        const text=e.results[0][0].transcript.trim();
        document.getElementById(target).value=text;
    };

    r.start();
}
async function startPatient(){
    const p=A.patientDraft;

    const r=await post('/api/kiosk/patient-start',{
        name:p.name,
        age:p.age,
        gender:p.gender,
        phone:p.phone,
        address:p.address,
        patient_id:p.pid,
        language:A.lang
    });

    if(!r.success)return alert(r.error);

    A.token=r.token?.access_token||r.token;
    A.patient=r.patient;
    localStorage.mk_token=A.token;
    consult();
}
function consult(){return navigateTo('consultation',()=>renderConsult())}
function renderConsult(){shell(t('access'),`<div class="mode-grid"><button onclick="newCase('NORMAL')">🩺<b>${t('normal')}</b><small>${t('normalD')}</small></button><button onclick="newCase('AYUSH')">🌿<b>${t('ayush')}</b><small>${t('ayushD')}</small></button></div>`)}
async function newCase(mode){const r=await post('/api/kiosk/start',{mode,language:A.lang});if(!r.success)return alert(r.error);A.case=r.case;A.mode=mode;A.answers={};A.questions=[];A.questionIndex=0;const s=await post(`/api/conversation/${A.case.id}/session`,{});if(!s.success)return alert(s.error);A.session=s.session;A.questions=[s.next_question];question()}
function question(trackHistory=true){
    if(trackHistory){
        return navigateTo('patient-question',()=>question(false));
    }
    if(questionSpeechTimer){
        clearTimeout(questionSpeechTimer);
        questionSpeechTimer = null;
    }
    const q=A.questions[A.questionIndex];
    if(!q) return historyStep();
    const saved=A.answers[q.key]?.answer||'';
    const opts=(q.options||[]).map((o,i)=>`<button type="button" class="answer-option ${saved===o?'selected':''}" data-i="${i}">${esc(o)}</button>`).join('');

    shell(t('patient'),`
    <div class="card question">
      <div class="progress">
        ${A.lang==='Tamil'?'கேள்வி':'Question'} ${A.questionIndex+1}
        <span style="float:right">${esc(q.adaptive?t('interview'):'CORE')}</span>
      </div>
      <h2>${esc(q.question)}</h2>

      <div style="margin:8px 0 14px 0">
        <button class="secondary" id="hear" style="display:inline-flex;align-items:center;gap:6px;padding:8px 14px;font-size:13px;font-weight:700">
          🔊 ${A.lang==='Tamil'?'கேள்வியை மீண்டும் கேள்':'Hear Question Again'}
        </button>
      </div>

      <div class="options">${opts}</div>

      <div style="margin:14px 0 10px 0">
        <label style="font-weight:700;display:block;margin-bottom:6px">${t('answer')}</label>
        <div style="display:flex;gap:8px;align-items:center">
          <input id="ans" value="${esc(saved)}" placeholder="${esc(t('placeholder'))}" style="flex:1;margin:0;padding:12px;border-radius:12px" onkeydown="if(event.key==='Enter')sendAns()">
          <button type="button" class="primary" id="mic" style="margin:0;padding:12px 18px;white-space:nowrap;display:inline-flex;align-items:center;gap:6px">
            🎙️ ${t('mic')}
          </button>
        </div>
      </div>

      <div style="display:flex;gap:12px;margin-top:18px">
        <button class="secondary" id="home">🏠 ${t('home')}</button>
        ${A.questionIndex>0||navigationHistory.length?`<button type="button" class="secondary" id="back">← ${t('back')}</button>`:''}
        <button class="primary" id="next">${t('next')} →</button>
      </div>
    </div>

    <div class="card">
      <b>${A.lang==='Tamil'?'நேரலை பாதுகாப்பு கண்காணிப்பு':'LIVE SAFETY VIEW'}</b>
      <p>${A.lang==='Tamil'?'முன்னுரிமை':'Priority'}: <strong>${esc(A.case.priority||'NORMAL')}</strong></p>
      <p>${A.lang==='Tamil'?'துறை':'Department'}: <strong>${esc(A.case.recommended_department||'Pending')}</strong></p>
      <p>${A.lang==='Tamil'?'பதில்கள்':'Answers'}: <strong>${Object.keys(A.answers).length}</strong></p>
      <small>${A.lang==='Tamil'?'சிவப்பு கொடிகள் திரையிடல் சமிக்ஞைகள்; மருத்துவர் சரிபார்ப்பு தேவை.':'Red flags are screening signals; clinician verification required.'}</small>
    </div>
    `,{hideBack:true});

    document.getElementById('hear')?.addEventListener('click',()=>speak(q.question));
    document.getElementById('mic')?.addEventListener('click',voiceInput);
    document.getElementById('home')?.addEventListener('click',goHome);
    document.getElementById('back')?.addEventListener('click',()=>{
        if(A.questionIndex>0){
            A.questionIndex--;
            question(false);
        }else{
            goBack();
        }
    });
    document.querySelectorAll('.answer-option').forEach(b=>b.addEventListener('click',()=>{
        document.getElementById('ans').value=q.options[+b.dataset.i];
        document.querySelectorAll('.answer-option').forEach(x=>x.classList.remove('selected'));
        b.classList.add('selected');
    }));
    document.getElementById('next').addEventListener('click',sendAns);
    questionSpeechTimer = setTimeout(()=>{
        questionSpeechTimer = null;
        speak(q.question);
    },250);
}

let intakeMicActive = false;
let intakeRecognition = null;
function voiceInput(){
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SpeechRecognition) return alert('Browser voice input is unavailable. Please use Chrome or Edge.');
    const btn = document.getElementById('mic');
    const input = document.getElementById('ans');

    if(intakeMicActive){
        if(intakeRecognition) intakeRecognition.stop();
        intakeMicActive = false;
        if(btn){
            btn.innerHTML = `🎙️ ${t('mic')}`;
            btn.className = 'primary';
        }
        return;
    }

    try {
        intakeRecognition = new SpeechRecognition();
        intakeRecognition.continuous = false;
        intakeRecognition.interimResults = true;
        intakeRecognition.lang = A.lang === 'Tamil' ? 'ta-IN' : 'en-IN';

        intakeRecognition.onstart = () => {
            intakeMicActive = true;
            if(btn){
                btn.innerHTML = `⏹ Listening...`;
                btn.className = 'primary pulse-mic';
            }
            if(input) input.placeholder = A.lang==='Tamil' ? 'கேட்கிறது... பேசுங்கள்...' : 'Listening... Speak your answer now!';
        };

        intakeRecognition.onresult = (e) => {
            let res = '';
            for(let i=0; i<e.results.length; i++){
                res += e.results[i][0].transcript;
            }
            if(input) input.value = res;
        };

        intakeRecognition.onerror = (e) => {
            intakeMicActive = false;
            if(btn){
                btn.innerHTML = `🎙️ ${t('mic')}`;
                btn.className = 'primary';
            }
        };

        intakeRecognition.onend = () => {
            intakeMicActive = false;
            if(btn){
                btn.innerHTML = `🎙️ ${t('mic')}`;
                btn.className = 'primary';
            }
        };

        intakeRecognition.start();
    } catch(err){
        alert('Could not start microphone: ' + err.message);
    }
}
async function sendAns(){

    const q = A.questions[A.questionIndex];
    const input = document.getElementById('ans');
    const v = (input?.value || '').trim();

    if(!v){
        alert(
            A.lang==='Tamil'
            ? 'தயவுசெய்து பதிலை சொல்லுங்கள் அல்லது type செய்யுங்கள்.'
            : 'Please provide an answer.'
        );
        return;
    }

    const btn = document.getElementById('next');
    if(btn){
        btn.disabled = true;
        btn.textContent =
            A.lang==='Tamil'
            ? 'உங்கள் பதிலை புரிந்துகொள்கிறோம்...'
            : 'Analyzing your answer...';
    }

    try{

        const r = await post(
            `/api/conversation/${A.case.id}/message`,
            {
                session_id: A.session.id,
                question_key: q.key,
                text: v,
                input_type: 'TEXT'
            }
        );

        console.log('AI interview response:', r);

        if(!r || !r.success){

            alert(
                r?.error ||
                (A.lang==='Tamil'
                    ? 'பதிலை process செய்ய முடியவில்லை.'
                    : 'Unable to process the answer.')
            );

            return;
        }

        // Save answer locally
        A.answers[q.key] = {
            question: q.question,
            answer: v
        };

        // Update safety/routing
        A.case.priority =
            r.priority || A.case.priority;

        A.case.recommended_department =
            r.department || A.case.recommended_department;

        if(r.flags?.length){
            showFlags(r.flags);
        }

        // Structured decision: continue -> next_question, complete -> final_summary
        if(r.status === 'continue' || r.next_question){
            if(r.next_question){
                A.questions =
                    A.questions.slice(
                        0,
                        A.questionIndex + 1
                    );

                A.questions.push(r.next_question);

                A.questionIndex++;

                question();

                return;
            }
        }

        // Interview finished (status: complete -> final_summary)
        if(r.final_summary || r.summary){
            A.finalSummary = r.final_summary || r.summary;
        }
        historyStep();

    }catch(err){

        console.error('sendAns error:',err);

        alert(
            A.lang==='Tamil'
            ? 'Server-ல் பதிலை process செய்யும்போது error ஏற்பட்டது.'
            : 'A server error occurred while processing the answer.'
        );

    }finally{

        const b=document.getElementById('next');

        if(b){
            b.disabled=false;
            b.textContent =
                `${t('next')} →`;
        }
    }
}
function showFlags(flags){const urgent=flags.some(f=>['HIGH','URGENT'].includes(f.severity));if(urgent)alert('⚠️ Potential urgent symptom detected. Staff triage attention required.')}
let selectedHistoryFile = null;

function handleHistoryFileSelect(input){
    if(input.files && input.files[0]){
        selectedHistoryFile = input.files[0];
        const statusEl = document.getElementById('history-selected-filename');
        if(statusEl){
            statusEl.style.display = 'block';
            statusEl.textContent = `✓ Selected: ${selectedHistoryFile.name}`;
        }
    }
}

function handleHistoryDropUpload(e){
    if(e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]){
        selectedHistoryFile = e.dataTransfer.files[0];
        const statusEl = document.getElementById('history-selected-filename');
        if(statusEl){
            statusEl.style.display = 'block';
            statusEl.textContent = `✓ Selected: ${selectedHistoryFile.name}`;
        }
    }
}

function clearHistoryForm(){
    selectedHistoryFile = null;
    const fileInput = document.getElementById('history-file-input');
    if(fileInput) fileInput.value = '';
    const textInput = document.getElementById('history-text-input');
    if(textInput) textInput.value = '';
    const statusEl = document.getElementById('history-selected-filename');
    if(statusEl){ statusEl.style.display = 'none'; statusEl.textContent = ''; }
    const resultCard = document.getElementById('history-status-card');
    if(resultCard) resultCard.style.display = 'none';
}

function loadSampleHistoryDoc(type){
    const isTa = A.lang === 'Tamil';
    const textInput = document.getElementById('history-text-input');
    if(!textInput) return;
    if(type === 'prescription'){
        textInput.value = isTa 
            ? "முந்தைய மருந்துசீட்டு:\n1. Tab. Paracetamol 650mg - 1-0-1 (3 நாட்கள்)\n2. Tab. Amoxicillin 500mg - 1-0-1 (5 நாட்கள்)\nடாக்டர் குறிப்பு: இரத்த அழுத்தம் 130/85, டைப் 2 நீரிழிவு நோய் வரலாறு."
            : "Previous Prescription:\n1. Tab. Paracetamol 650mg - 1-0-1 (3 days)\n2. Tab. Amoxicillin 500mg - 1-0-1 (5 days)\nDoctor Note: BP 130/85, History of Type 2 Diabetes.";
    } else if(type === 'discharge'){
        textInput.value = isTa
            ? "டிஸ்சார்ஜ் சுருக்கம்:\nநோயாளி: திரு. குமார் (48/ஆண்)\nஅனுமதித்த காரணம்: கடுமையான காய்ச்சல் மற்றும் வயிற்று வலி\nஅறுவை சிகிச்சை: Appendectomy (15/04/2024)\nதற்போதைய நிலை: சீரானது, மருந்துகள் தொடர்கின்றன."
            : "Discharge Summary:\nPatient: Mr. Kumar (48/Male)\nAdmission Reason: Acute Fever and Abdominal Pain\nSurgical Procedure: Appendectomy (15/04/2024)\nStatus: Recovered, continuing oral medications.";
    } else {
        textInput.value = isTa
            ? "ஆய்வக அறிக்கை:\nHemoglobin: 11.2 gm/dL (குறைவு)\nTotal WBC: 9200 /cmm\nPlatelet Count: 240,000 /cmm\nFasting Blood Sugar: 142 mg/dL (அதிகம்)"
            : "Lab Report History:\nHemoglobin: 11.2 gm/dL (Low)\nTotal WBC: 9200 /cmm\nPlatelet Count: 240,000 /cmm\nFasting Blood Sugar: 142 mg/dL (Elevated)";
    }
}

function openHistoryScanner(){
    const input = document.getElementById('history-file-input');
    if(input) input.click();
}

function historyStep(){
    return navigateTo('medical-history-choice',()=>renderHistoryStep());
}

function renderHistoryStep(){
    const count=Object.keys(A.answers).length;
    const capturedMsg=A.lang==='Tamil'?`${count} தகவல்கள் பதிவு செய்யப்பட்டன.`:`${count} adaptive answers captured.`;
    shell(t('history'),`<div class="card center"><h2>${t('history')}</h2><p>${capturedMsg}</p><div class="yesno"><button onclick="documentStep()">${t('yes')}</button><button onclick="summaryStep()">${t('no')}</button></div></div>`);
}

function documentStep(){
    selectedHistoryFile = null;
    return navigateTo('medical-history-document',()=>renderDocumentStep());
}

function renderDocumentStep(){
    const isTa = A.lang === 'Tamil';
    shell(t('upload'), `
    <div class="doc-panel" style="max-width:720px;margin:0 auto">
        <h3 id="history-panel-title" style="margin:0 0 10px 0;font-size:16px;color:#102a2d">
            📄 ${isTa ? 'முந்தைய மருத்துவ வரலாறு பதிவேற்றம்' : 'Upload Medical History'}
        </h3>

        <div class="sample-docs-bar" style="display:flex;gap:8px;margin-bottom:12px">
            <span id="history-sample-label" style="font-size:11px;font-weight:700;color:#0b756b;align-self:center">
                ${isTa ? 'மாதிரி:' : 'Sample:'}
            </span>
            <button id="history-sample-rx" class="secondary" style="padding:4px 8px;font-size:11px;margin:0" onclick="loadSampleHistoryDoc('prescription')">💊 ${isTa ? 'மருந்துச் சீட்டு' : 'Prescription'}</button>
            <button id="history-sample-discharge" class="secondary" style="padding:4px 8px;font-size:11px;margin:0" onclick="loadSampleHistoryDoc('discharge')">🏥 ${isTa ? 'டிஸ்சார்ஜ் சுருக்கம்' : 'Discharge'}</button>
            <button id="history-sample-lab" class="secondary" style="padding:4px 8px;font-size:11px;margin:0" onclick="loadSampleHistoryDoc('lab')">🩸 ${isTa ? 'ஆய்வக அறிக்கை' : 'Lab Report'}</button>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">
            <button class="primary" style="margin:0;padding:12px 10px;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:6px" onclick="document.getElementById('history-file-input').click()">
                <span>📄</span> <span>${isTa ? 'வரலாறு பதிவேற்று' : 'Upload Medical History'}</span>
            </button>
            <button class="primary" style="margin:0;padding:12px 10px;font-size:13px;font-weight:700;background:#0d655d;display:flex;align-items:center;justify-content:center;gap:6px" onclick="openHistoryScanner()">
                <span>🖨️</span> <span>${isTa ? 'வரலாறு ஸ்கேன் செய்' : 'Scan Medical History'}</span>
            </button>
        </div>

        <div class="doc-upload-zone" id="history-drop-zone"
             onclick="document.getElementById('history-file-input').click()"
             ondragover="event.preventDefault(); this.classList.add('dragover');"
             ondragleave="this.classList.remove('dragover');"
             ondrop="event.preventDefault(); this.classList.remove('dragover'); handleHistoryDropUpload(event);"
             style="padding:16px;margin-bottom:10px;border:2px dashed #0b756b;border-radius:8px;text-align:center;cursor:pointer;background:#f9fdfc">
            <input id="history-file-input" type="file" accept=".pdf,.png,.jpg,.jpeg,.docx,.txt" style="display:none" onchange="handleHistoryFileSelect(this)">
            <div style="font-size:24px;margin-bottom:4px">📂</div>
            <b style="color:#0b756b;font-size:13px">
                ${isTa ? 'மருத்துவ வரலாறு கோப்பை பதிவேற்ற கிளிக் செய்யவும் அல்லது இழுத்து விடவும்' : 'Click or drag & drop image / PDF medical history'}
            </b>
            <div style="font-size:11px;color:#6b8284">
                ${isTa ? 'PNG, JPG, PDF, DOCX (அதிகபட்சம் 16MB)' : 'PNG, JPG, PDF, DOCX (Max 16MB)'}
            </div>
        </div>

        <div id="history-selected-filename" style="display:${selectedHistoryFile?'block':'none'};font-size:12px;color:#0b756b;font-weight:bold;margin-bottom:8px">${selectedHistoryFile?`✓ Selected: ${esc(selectedHistoryFile.name)}`:''}</div>

        <textarea id="history-text-input" rows="3" placeholder="${isTa ? 'அல்லது முந்தைய மருந்துச் சீட்டு / மருத்துவ வரலாறு உரையை இங்கு ஒட்டவும்...' : 'Or paste prescription / medical history text here...'}" style="font-size:12px;width:100%;padding:8px;border:1px solid #c0d8d5;border-radius:6px"></textarea>

        <div style="display:flex;gap:8px;margin-top:10px">
            <button id="history-save-btn" class="primary" style="flex:1;margin:0;padding:10px" onclick="saveDoc()">
                ✨ ${isTa ? 'மருத்துவ வரலாற்றை பதிவு செய்' : 'Process Medical History'}
            </button>
            <button class="secondary" style="margin:0;padding:10px" onclick="clearHistoryForm()">${isTa ? 'அழி' : 'Clear'}</button>
            <button class="secondary" style="margin:0;padding:10px" onclick="summaryStep()">${isTa ? 'தவிர்' : 'Skip'}</button>
        </div>

        <div id="history-status-card" style="display:none;margin-top:14px;padding:14px;background:#f0f8f7;border:1px solid #bce3df;border-radius:8px">
            <h4 style="margin:0 0 8px 0;color:#0b756b">${isTa ? 'பதிவு செய்யப்பட்ட மருத்துவ வரலாறு சுருக்கம்' : 'Medical History Summary Extracted'}</h4>
            <pre id="history-status-pre" style="white-space:pre-wrap;font-size:12px;color:#102a2d;max-height:220px;overflow-y:auto;background:#fff;padding:10px;border-radius:6px;border:1px solid #d0e7e4"></pre>
            <button class="primary" style="margin-top:12px;width:100%" onclick="summaryStep()">
                ${isTa ? 'சுருக்கத்திற்கு செல்லவும் →' : 'Continue to Summary →'}
            </button>
        </div>
    </div>
    `);
}

async function saveDoc(){
    const isTa = A.lang === 'Tamil';
    const f = selectedHistoryFile || document.getElementById('history-file-input')?.files[0] || document.getElementById('doc')?.files[0];
    const textVal = document.getElementById('history-text-input')?.value?.trim() || '';

    if(!f && !textVal){
        return summaryStep();
    }

    const saveBtn = document.getElementById('history-save-btn');
    if(saveBtn){
        saveBtn.disabled = true;
        saveBtn.textContent = isTa ? '✨ பகுப்பாய்வு செய்கிறது...' : '✨ Processing...';
    }

    try {
        const fd = new FormData();
        if(f) fd.append('file', f);
        if(textVal) fd.append('text', textVal);

        const r = await fetch(`/api/documents/${A.case.id}/medical-history`, {
            method: 'POST',
            headers: { Authorization: 'Bearer ' + A.token },
            body: fd
        }).then(x => x.json());

        if(!r.success){
            alert(r.error || (isTa ? 'மருத்துவ வரலாற்றை பதிவேற்ற முடியவில்லை.' : 'Failed to process medical history.'));
            if(saveBtn){
                saveBtn.disabled = false;
                saveBtn.textContent = isTa ? '✨ மருத்துவ வரலாற்றை பதிவு செய்' : 'Process Medical History';
            }
            return;
        }

        const card = document.getElementById('history-status-card');
        const pre = document.getElementById('history-status-pre');
        if(card && pre){
            card.style.display = 'block';
            pre.textContent = r.history_summary || (isTa ? 'முந்தைய மருத்துவ வரலாறு வெற்றிகரமாக பதிவு செய்யப்பட்டது.' : 'Medical history summary recorded successfully.');
        } else {
            summaryStep();
        }
    } catch(err){
        console.error('saveDoc error:', err);
        summaryStep();
    } finally {
        if(saveBtn){
            saveBtn.disabled = false;
            saveBtn.textContent = isTa ? '✨ மருத்துவ வரலாற்றை பதிவு செய்' : 'Process Medical History';
        }
    }
}
async function summaryStep(){
    const r=await post(`/api/conversation/${A.case.id}/complete`,{});
    if(!r.success)return alert(r.error||(A.lang==='Tamil'?'மருத்துவ நேர்காணலை முடிக்க இயலவில்லை.':'Unable to complete intake'));
    A.case=r.case;
    const q=r.case?.queue_number||r.queue?.queue_number;
    const token=q?`${(r.department||'GM').replace(/[^A-Z]/gi,'').slice(0,2).toUpperCase()}-${String(q).padStart(3,'0')}`:(r.case.case_number||'READY');
    const result={
        department:r.department,
        priority:r.priority||A.case.priority,
        doctorName:r.assignment?.doctor_name,
        summary:r.summary,
        token
    };
    navigateTo('intake-summary',()=>renderIntakeSummary(result));
}

function renderIntakeSummary(result){
    const isTa=A.lang==='Tamil';
    const priorLbl=isTa?'முன்னுரிமை':'Priority';
    const docLbl=isTa?'நியமிக்கப்பட்ட மருத்துவர்':'Assigned doctor';
    const triageLbl=isTa?'முன்னுரிமை / காத்திரு':'Triage / queue';
    const sumTitle=isTa?'AI மருத்துவ சுருக்கம்':'AI Clinical Summary';
    const sumFooter=isTa?'AI ஆவண வரைவு; மருத்துவர் சரிபார்ப்பு தேவை.':'AI-assisted draft; clinician verification required.';
    shell(t('summary'),`<div class="summary"><div class="summary-head"><span class="badge">${t('route')}</span><h2>${esc(result.department||'General Medicine')}</h2><div class="token">${t('token')}<strong>${esc(result.token)}</strong></div><p>${priorLbl}: <b>${esc(result.priority)}</b></p><p>${docLbl}: <b>${esc(result.doctorName||triageLbl)}</b></p></div><section><h3>${sumTitle}</h3><pre>${esc(result.summary||'')}</pre><small>${sumFooter}</small></section><button class="primary" onclick="printToken('${esc(result.token)}')">🖨 ${t('print')}</button><button type="button" class="secondary" onclick="patient()">${t('dashboard')}</button></div>`);
}
async function summaryStep(){const r=await post(`/api/conversation/${A.case.id}/complete`,{});if(!r.success)return alert(r.error||(A.lang==='Tamil'?'மருத்துவ நேர்காணலை முடிக்க இயலவில்லை.':'Unable to complete intake'));A.case=r.case;const q=r.case?.queue_number||r.queue?.queue_number;const token=q?`${(r.department||'GM').replace(/[^A-Z]/gi,'').slice(0,2).toUpperCase()}-${String(q).padStart(3,'0')}`:(r.case.case_number||'READY');const isTa=A.lang==='Tamil';const priorLbl=isTa?'முன்னுரிமை':'Priority';const docLbl=isTa?'நியமிக்கப்பட்ட மருத்துவர்':'Assigned doctor';const triageLbl=isTa?'முன்னுரிமை / காத்திரு':'Triage / queue';const sumTitle=isTa?'AI மருத்துவ சுருக்கம்':'AI Clinical Summary';const sumFooter=isTa?'AI ஆவண வரைவு; மருத்துவர் சரிபார்ப்பு தேவை.':'AI-assisted draft; clinician verification required.';shell(t('summary'),`<div class="summary"><div class="summary-head"><span class="badge">${t('route')}</span><h2>${esc(r.department||'General Medicine')}</h2><div class="token">${t('token')}<strong>${esc(token)}</strong></div><p>${priorLbl}: <b>${esc(r.priority||A.case.priority)}</b></p><p>${docLbl}: <b>${esc(r.assignment?.doctor_name||triageLbl)}</b></p></div><section><h3>${sumTitle}</h3><pre>${esc(r.summary||A.finalSummary||'')}</pre><small>${sumFooter}</small></section><button class="primary" onclick="printToken('${esc(token)}')">🖨 ${t('print')}</button><button class="secondary" onclick="patient()">${t('dashboard')}</button></div>`)}
function printToken(tok){const w=open('','_blank');w.document.write(`<h1>MediKiosk</h1><h2>Patient Token</h2><h1>${esc(tok)}</h1>`);w.print()}
function doctor(){return navigateTo('doctor-login',()=>shell(t('doctor'),`<div class="card form"><label>${t('doctorName')}<input id="dn" placeholder="Dr. Name"></label><label>${t('email')}<input id="deemail"></label><label>${t('pass')}<input id="depass" type="password"></label><button class="primary" onclick="doctorLogin()">${t('login')}</button></div>`))}
async function doctorLogin(){const r=await post('/api/auth/login',{type:'DOCTOR',email:deemail.value,password:depass.value});if(!r.success)return alert(r.error);A.token=r.access_token;A.role='DOCTOR';localStorage.mk_token=A.token;doctorDash(r.user)}
async function doctorDash(user){
    const r=await get('/api/doctor/cases');
    if(!r.success)return alert(r.error);
    const rows=r.cases.map(c=>`<div class="row"><b>${esc(c.case_number)}</b><span>${esc(c.status)} • ${esc(c.priority)} • ${esc(c.recommended_department||'')}</span><button type="button" onclick="review(${c.id})">Open</button></div>`).join('')||'<div class="empty">No assigned cases</div>';
    const render=()=>shell(t('doctor'),`<div class="stats"><div><b>${esc(user.full_name)}</b><span>Doctor</span></div><div><b>${r.cases.length}</b><span>Assigned cases</span></div><div><b>AI + Rules</b><span>Clinical decision support</span></div></div><div class="card"><h3>Today’s patient queue</h3>${rows}</div><button type="button" class="secondary" onclick="patient()">${t('logout')}</button>`);
    navigateTo('doctor-dashboard',render);
}
async function review(id){
    const r=await get('/api/doctor/case/'+id);
    if(!r.success)return alert(r.error);
    const c=r.case;
    const hist=(r.history&&Object.entries(r.history).filter(([k,v])=>v).map(([k,v])=>`<p><b>${esc(k)}</b><br>${esc(v)}</p>`).join(''))||'';
    const render=()=>shell(t('summary'),`<div class="card"><h2>${esc(c.case_number)}</h2><p><b>${esc(c.priority)}</b> • ${esc(c.status)}</p><h3>Patient</h3><p>${esc(r.patient.full_name)} • ${esc(r.patient.age)} • ${esc(r.patient.gender)}</p><h3>Clinical history</h3>${hist}<h3>AI summary</h3><pre>${esc(r.summary?.summary_text||'No summary')}</pre><textarea id="note" rows="5" placeholder="Doctor note"></textarea><button type="button" class="primary" onclick="reviewSave(${id},'IN_PROGRESS')">${t('startC')}</button><button type="button" class="secondary" onclick="reviewSave(${id},'COMPLETED')">${t('complete')}</button></div>`);
    navigateTo(`doctor-case-${id}`,render);
}
async function reviewSave(id,status){const r=await fetch('/api/doctor/case/'+id+'/review',{method:'PATCH',headers:{'Content-Type':'application/json',Authorization:'Bearer '+A.token},body:JSON.stringify({status:status==='COMPLETED'?'CONFIRMED':'EDITED',doctor_notes:document.getElementById('note').value,summary_text:document.querySelector('pre')?.textContent||''})}).then(x=>x.json());if(!r.success)return alert(r.error);doctorDash({full_name:'Doctor'})}
function staff(){return navigateTo('staff-login',()=>shell(t('staff'),`<div class="card form"><label>${t('staffEmail')}<input id="se" value="staff@hospital.local"></label><label>${t('staffPass')}<input id="sp" type="password"></label><button class="primary" onclick="staffLogin()">${t('login')}</button></div>`))}
async function staffLogin(){const r=await post('/api/auth/login',{type:'STAFF',email:se.value,password:sp.value});if(!r.success)return alert(r.error);A.token=r.access_token;A.role='TRIAGE';localStorage.mk_token=A.token;staffDash()}
async function staffDash(){
    const r=await get('/api/triage/cases');
    if(!r.success)return alert(r.error);
    const alerts=r.cases.filter(c=>['HIGH','URGENT'].includes(c.priority)).map(c=>`<div class="alert"><b>${esc(c.case_number)}</b> • ${esc(c.priority)}<span>${esc(c.status)}</span><br><small>Safety attention required</small></div>`).join('')||'<div class="empty">No active red-flag alerts</div>';
    const render=()=>shell(t('staff'),`<div class="card"><h3>🚨 Safety alerts</h3>${alerts}</div><div class="card"><h3>Patient queue</h3>${r.cases.map(c=>`<div class="row"><b>${esc(c.case_number)}</b><span>${esc(c.priority)} • ${esc(c.recommended_department||'')}</span><span>${esc(c.status)}</span></div>`).join('')}</div>`);
    navigateTo('staff-dashboard',render);
}
function admin(){return navigateTo('admin-login',()=>shell(t('admin'),`<div class="card form"><label>${t('adminEmail')}<input id="ae" value="admin@hospital.local"></label><label>${t('adminPass')}<input id="ap" type="password"></label><button class="primary" onclick="adminLogin()">${t('login')}</button></div>`))}
async function adminLogin(){const r=await post('/api/auth/login',{type:'ADMIN',email:ae.value,password:ap.value});if(!r.success)return alert(r.error);A.token=r.access_token;A.role='ADMIN';localStorage.mk_token=A.token;adminDash()}
async function adminDash(){
    const r=await get('/api/admin/state');
    if(!r.success)return alert(r.error);
    const deps=r.departments.map(d=>`<div class="row"><b>${esc(d.name)}</b><span>${esc(d.email||'')}</span><span>${d.is_active?'ACTIVE':'INACTIVE'}</span><button type="button" onclick="changeDept(${d.id})">Edit login</button></div>`).join('');
    const render=()=>shell(t('admin'),`<div class="stats"><div><b>${r.stats.departments}</b><span>Departments</span></div><div><b>${r.stats.patients}</b><span>Patients</span></div><div><b>${r.stats.cases}</b><span>Cases</span></div></div><div class="card"><h3>${t('manage')}</h3>${deps}<hr><h3>${t('create')}</h3><div class="grid2"><input id="nd" placeholder="${t('deptName')}"><input id="ne" placeholder="${t('newEmail')}"><input id="np" placeholder="${t('newPass')}" type="password"><input id="ns" placeholder="Doctor name"></div><button type="button" class="primary" onclick="createDept()">${t('create')}</button></div><div class="card"><h3>${t('audit')}</h3>${r.audit.map(x=>`<div class="row"><span>${esc(x.created_at||'')}</span><span>${esc(x.user_id||'')}</span><span>${esc(x.action||'')}</span></div>`).join('')}</div>`);
    navigateTo('admin-dashboard',render);
}
async function createDept(){const r=await post('/api/admin/department',{name:nd.value,email:ne.value,password:np.value,doctor_name:ns.value});if(!r.success)return alert(r.error);adminDash()}
async function changeDept(id){const email=prompt('New department/doctor email (leave blank to keep current):','');const password=prompt('New password (8+ chars, leave blank to keep current):','');if(!email&&!password)return;const r=await fetch('/api/admin/department/'+id,{method:'PATCH',headers:{'Content-Type':'application/json',Authorization:'Bearer '+A.token},body:JSON.stringify({email,password})}).then(x=>x.json());if(!r.success)return alert(r.error);adminDash()}
async function post(url,data){

    const token = A.token || localStorage.mk_token || '';

    const headers = {
        'Content-Type':'application/json'
    };

    if(token){
        headers.Authorization = 'Bearer ' + token;
    }

    const r = await fetch(url,{
        method:'POST',
        headers:headers,
        body:JSON.stringify(data)
    });

    const raw = await r.text();

    console.log('API STATUS:',r.status);
    console.log('API RESPONSE:',raw);

    if(!r.ok){
        throw new Error(`HTTP ${r.status}: ${raw}`);
    }

    return JSON.parse(raw);
}
async function get(url){const r=await fetch(url,{headers:{Authorization:'Bearer '+A.token}});return r.json()}

/* ─── MODAL CONTROLLER ─── */
function closeModal(){
    const root = document.getElementById('modal-root');
    if(root) root.innerHTML = '';
}

/* ─── CONNECT ALL APIS (GEMINI & OPENROUTER) ─── */
function openApiModal(){
    // Connect API dashboard removed from kiosk UI as requested
}

async function testApiProvider(provider){
    const isGemini = provider === 'GEMINI';
    const keyInput = document.getElementById(isGemini ? 'api-gk' : 'api-ok');
    const modelSelect = document.getElementById(isGemini ? 'api-gm' : 'api-om');
    const loadEl = document.getElementById(isGemini ? 'gemini-ping-load' : 'openrouter-ping-load');
    const resEl = document.getElementById(isGemini ? 'gemini-test-res' : 'openrouter-test-res');

    const key = keyInput ? keyInput.value.trim() : '';
    const model = modelSelect ? modelSelect.value : '';

    loadEl.style.display = 'inline';
    resEl.className = 'api-test-output';
    resEl.style.display = 'none';

    try {
        const r = await fetch('/api/ai/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider, api_key: key, model })
        }).then(x => x.json());

        loadEl.style.display = 'none';
        resEl.style.display = 'block';

        if(r.success){
            resEl.className = 'api-test-output show ok';
            resEl.innerHTML = `<b>✅ Connected!</b> Latency: <b>${r.latency_ms} ms</b> • Model: <code>${r.model}</code> • Response: <i>"${esc(r.message)}"</i>`;
        } else {
            resEl.className = 'api-test-output show err';
            resEl.innerHTML = `<b>❌ Connection failed:</b> ${esc(r.error || 'Check API key & model')}`;
        }
    } catch(err){
        loadEl.style.display = 'none';
        resEl.className = 'api-test-output show err';
        resEl.style.display = 'block';
        resEl.innerHTML = `<b>❌ Request error:</b> ${esc(err.message)}`;
    }
}

async function saveApiKeys(){
    const gk = document.getElementById('api-gk')?.value.trim() || '';
    const gm = document.getElementById('api-gm')?.value || '';
    const ok = document.getElementById('api-ok')?.value.trim() || '';
    const om = document.getElementById('api-om')?.value || '';

    const payload = {};
    if(gk) payload.gemini_key = gk;
    if(gm) payload.gemini_model = gm;
    if(ok) payload.openrouter_key = ok;
    if(om) payload.openrouter_model = om;

    try {
        const r = await fetch('/api/ai/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(x => x.json());

        alert(r.message || 'API settings applied successfully!');
        closeModal();
        refreshApiStatus();
    } catch(err){
        alert('Failed to save API config: ' + err.message);
    }
}

/* ─── VOICE ASSIGNMENT (TTS & MIC) ─── */
let micTestRecognition = null;
let micIsListening = false;

function openVoiceModal(){
    const root = document.getElementById('modal-root');
    if(!root) return;

    const voices = ('speechSynthesis' in window) ? speechSynthesis.getVoices() : [];

    const tamilVoices = voices.filter(v => v.lang.includes('ta') || v.name.toLowerCase().includes('tamil'));
    const englishVoices = voices.filter(v => v.lang.includes('en'));

    const optTa = tamilVoices.map(v => `<option value="${esc(v.name)}" ${voiceConfig.tamilVoice===v.name?'selected':''}>${esc(v.name)} (${v.lang})</option>`).join('') ||
        `<option value="">Default System Tamil / Indian Voice</option>`;

    const optEn = englishVoices.map(v => `<option value="${esc(v.name)}" ${voiceConfig.englishVoice===v.name?'selected':''}>${esc(v.name)} (${v.lang})</option>`).join('') ||
        `<option value="">Default System English Voice</option>`;

    root.innerHTML = `
    <div class="mk-modal-overlay" onclick="if(event.target===this)closeModal()">
      <div class="mk-modal">
        <div class="mk-modal-head">
          <h2>🎙️ Voice Assignment & Speech Controls</h2>
          <button class="close-modal-btn" onclick="closeModal()">✕</button>
        </div>

        <p style="color:#5e7577;font-size:14px;margin-top:0">
          Configure text-to-speech audio voices for Tamil and English, and adjust speech pitch & speed rate.
        </p>

        <div class="voice-config-grid">
          <div class="api-provider-card">
            <b>🇮🇳 Tamil Voice Assignment</b>
            <label style="font-size:12px;display:block;margin:8px 0 4px 0">TTS Voice Profile</label>
            <select id="v-ta" style="width:100%;padding:10px;border-radius:10px;border:1px solid #cbdad8">
              ${optTa}
            </select>
            <button class="primary" style="margin-top:14px;padding:9px 14px;font-size:13px" onclick="testVoiceSpeak('Tamil')">
              🔊 Test Tamil Voice
            </button>
          </div>

          <div class="api-provider-card">
            <b>🌐 English Voice Assignment</b>
            <label style="font-size:12px;display:block;margin:8px 0 4px 0">TTS Voice Profile</label>
            <select id="v-en" style="width:100%;padding:10px;border-radius:10px;border:1px solid #cbdad8">
              ${optEn}
            </select>
            <button class="primary" style="margin-top:14px;padding:9px 14px;font-size:13px;background:#185abc" onclick="testVoiceSpeak('English')">
              🔊 Test English Voice
            </button>
          </div>
        </div>

        <div class="api-provider-card">
          <b>🎚️ Speech Pitch & Speed (Rate)</b>
          <div class="voice-slider-group">
            <label><span>Speed (Speech Rate)</span><span id="rate-val">${voiceConfig.rate}x</span></label>
            <input id="v-rate" type="range" min="0.7" max="1.4" step="0.1" value="${voiceConfig.rate}" oninput="document.getElementById('rate-val').textContent=this.value+'x'">
          </div>
          <div class="voice-slider-group">
            <label><span>Pitch</span><span id="pitch-val">${voiceConfig.pitch}</span></label>
            <input id="v-pitch" type="range" min="0.8" max="1.3" step="0.1" value="${voiceConfig.pitch}" oninput="document.getElementById('pitch-val').textContent=this.value">
          </div>
        </div>

        <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:16px">
          <button class="secondary" style="margin:0" onclick="closeModal()">Close</button>
          <button class="primary" style="margin:0" onclick="saveVoiceAssignment()">💾 Save Voice Settings</button>
        </div>
      </div>
    </div>
    `;
}

function testVoiceSpeak(lang){
    if(!('speechSynthesis' in window)){
        alert('Web Speech Synthesis is not supported in this browser.');
        return;
    }
    speechSynthesis.cancel();
    const isTa = lang === 'Tamil';
    const text = isTa 
        ? 'வணக்கம், நான் மெடிகியோஸ்க் குரல் உதவியாளர். உங்கள் உடல்நல விவரங்களை எளிதாக பதிவு செய்யலாம்.'
        : 'Hello, I am MediKiosk clinical voice assistant. You can speak or type your symptoms comfortably.';

    const u = new SpeechSynthesisUtterance(text);
    const voices = speechSynthesis.getVoices();
    const selTa = document.getElementById('v-ta')?.value;
    const selEn = document.getElementById('v-en')?.value;

    if(isTa){
        u.lang = 'ta-IN';
        if(selTa){
            const v = voices.find(x => x.name === selTa);
            if(v) u.voice = v;
        }
    } else {
        u.lang = 'en-IN';
        if(selEn){
            const v = voices.find(x => x.name === selEn);
            if(v) u.voice = v;
        }
    }
    u.rate = parseFloat(document.getElementById('v-rate')?.value || voiceConfig.rate || '1.0');
    u.pitch = parseFloat(document.getElementById('v-pitch')?.value || voiceConfig.pitch || '1.0');
    speechSynthesis.speak(u);
}

function toggleMicTest(){
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SpeechRecognition){
        alert('Web Speech Recognition is not supported by your browser. Please use Chrome or Edge.');
        return;
    }

    const btn = document.getElementById('mic-test-btn');
    const status = document.getElementById('mic-status-text');
    const box = document.getElementById('mic-transcript-box');

    if(micIsListening){
        if(micTestRecognition){
            micTestRecognition.stop();
        }
        micIsListening = false;
        if(btn) btn.textContent = '🎙️ Start Speaking';
        if(status) status.textContent = 'Mic stopped.';
        return;
    }

    try {
        micTestRecognition = new SpeechRecognition();
        micTestRecognition.continuous = false;
        micTestRecognition.interimResults = true;
        micTestRecognition.lang = A.lang === 'Tamil' ? 'ta-IN' : 'en-IN';

        micTestRecognition.onstart = () => {
            micIsListening = true;
            if(btn){
                btn.textContent = '⏹ Stop Listening';
                btn.className = 'primary';
            }
            if(status) status.textContent = 'Listening... Speak now!';
        };

        micTestRecognition.onresult = (e) => {
            let res = '';
            for(let i=0; i<e.results.length; i++){
                res += e.results[i][0].transcript;
            }
            if(box) box.textContent = `"${res}"`;
        };

        micTestRecognition.onerror = (e) => {
            if(status) status.textContent = 'Mic error: ' + e.error;
            micIsListening = false;
            if(btn){
                btn.textContent = '🎙️ Start Speaking';
                btn.className = 'secondary';
            }
        };

        micTestRecognition.onend = () => {
            micIsListening = false;
            if(btn){
                btn.textContent = '🎙️ Start Speaking';
                btn.className = 'secondary';
            }
            if(status) status.textContent = 'Recognition complete.';
        };

        micTestRecognition.start();
    } catch(err){
        alert('Could not start microphone: ' + err.message);
    }
}

function saveVoiceAssignment(){
    const selTa = document.getElementById('v-ta')?.value || '';
    const selEn = document.getElementById('v-en')?.value || '';
    const rate = parseFloat(document.getElementById('v-rate')?.value || '1.0');
    const pitch = parseFloat(document.getElementById('v-pitch')?.value || '1.0');

    voiceConfig.tamilVoice = selTa;
    voiceConfig.englishVoice = selEn;
    voiceConfig.rate = rate;
    voiceConfig.pitch = pitch;

    localStorage.mk_voice_ta = selTa;
    localStorage.mk_voice_en = selEn;
    localStorage.mk_voice_rate = String(rate);
    localStorage.mk_voice_pitch = String(pitch);

    alert('Voice settings saved successfully!');
    closeModal();
}

/* ─── AI DOC ANALYZER & CHATBOT ─── */
let docChatLang = localStorage.getItem('mk_doc_lang') || 'Tamil';
let patientSession = { name: null, reports: [] };
let currentDocAnalysis = null;
let docChatHistory = [];
let docChatMicActive = false;
let docChatRecognition = null;
let patientReportHistory = [];

function translateDocType(dt){
    if(!dt) return docChatLang === 'Tamil' ? 'மருத்துவ அறிக்கை' : 'Medical Report';
    const s = dt.toLowerCase();
    if(docChatLang === 'Tamil'){
        if(s.includes('blood') || s.includes('lab') || s.includes('test')) return 'இரத்த பரிசோதனை அறிக்கை';
        if(s.includes('presc') || s.includes('rx')) return 'மருந்துச் சீட்டு';
        if(s.includes('discharge')) return 'டிஸ்சார்ஜ் சுருக்கம்';
        return 'மருத்துவ அறிக்கை';
    }
    return dt;
}

function isPatientNameMismatch(existingName, newName){
    if(!existingName || !newName) return false;
    const clean = s => s.toLowerCase().replace(/^(mr|mrs|ms|dr|master|selvi|shri|smt)\.?\s+/i, '').replace(/[^a-z0-9]/g, '').trim();
    const c1 = clean(existingName);
    const c2 = clean(newName);
    if(!c1 || !c2 || c1 === 'uncertain' || c2 === 'uncertain' || c1 === 'verifiedpatient' || c2 === 'verifiedpatient') return false;
    if(c1.includes(c2) || c2.includes(c1)) return false;
    return true;
}

function updateActiveBadge(){
    const activeBadge = document.getElementById('doc-active-badge');
    if(!activeBadge) return;
    const isTa = (docChatLang === 'Tamil');
    const count = (patientSession?.reports && patientSession.reports.length) || (currentDocAnalysis ? 1 : 0);
    if(count === 0){
        activeBadge.style.display = 'none';
        return;
    }
    activeBadge.style.display = 'inline-flex';
    if(count > 1){
        activeBadge.textContent = isTa ? `✓ ${count} அறிக்கைகள் தயார்` : `✓ ${count} Reports Ready`;
    } else {
        const dt = currentDocAnalysis?.analysis?.document_type || 'Report';
        activeBadge.textContent = isTa ? `✓ ${translateDocType(dt)} தயார்` : `✓ ${dt} Ready`;
    }
}

function setDocChatLang(lang){
    docChatLang = lang;
    localStorage.setItem('mk_doc_lang', lang);
    const isTa = (lang === 'Tamil');

    // Update toggle buttons in header
    const btnTa = document.getElementById('doc-btn-ta');
    const btnEn = document.getElementById('doc-btn-en');
    if(btnTa) btnTa.className = isTa ? 'active' : '';
    if(btnEn) btnEn.className = !isTa ? 'active' : '';

    // ── LEFT CARD GLOBAL UPDATES ──
    const panelTitle = document.getElementById('doc-panel-title');
    if(panelTitle) panelTitle.innerHTML = `📄 ${isTa ? 'மருத்துவ அறிக்கை பதிவேற்றம்' : 'Upload Medical Report'}`;

    const sampleLbl = document.getElementById('doc-sample-label');
    if(sampleLbl) sampleLbl.textContent = isTa ? 'மாதிரி:' : 'Sample:';

    const btnBlood = document.getElementById('sample-btn-blood');
    if(btnBlood) btnBlood.innerHTML = `🩸 ${isTa ? 'இரத்த பரிசோதனை' : 'Blood Test'}`;

    const btnRx = document.getElementById('sample-btn-rx');
    if(btnRx) btnRx.innerHTML = `💊 ${isTa ? 'மருந்துச் சீட்டு' : 'Prescription'}`;

    const btnDischarge = document.getElementById('sample-btn-discharge');
    if(btnDischarge) btnDischarge.innerHTML = `🏥 ${isTa ? 'டிஸ்சார்ஜ் சுருக்கம்' : 'Discharge'}`;

    const uploadBtnTxt = document.getElementById('doc-btn-upload-text');
    if(uploadBtnTxt) uploadBtnTxt.textContent = isTa ? 'அறிக்கை பதிவேற்று' : 'Upload Report';

    const scanBtnTxt = document.getElementById('doc-btn-scan-text');
    if(scanBtnTxt) scanBtnTxt.textContent = isTa ? 'அறிக்கை ஸ்கேன் செய்' : 'Scan Medical Report';

    const scanHelper = document.getElementById('doc-scan-helper');
    if(scanHelper) scanHelper.textContent = isTa ? 'இணைக்கப்பட்ட மருத்துவ ஆவண ஸ்கேனர் அல்லது கேமரா மூலம் காகித அறிக்கையை ஸ்கேன் செய்யவும்.' : 'Scan a physical medical report using the connected scanner / camera.';

    const uploadTitle = document.getElementById('doc-upload-title');
    if(uploadTitle && (!uploadTitle.dataset.fileName)){
        uploadTitle.textContent = isTa ? 'அறிக்கை கோப்பை பதிவேற்ற கிளிக் செய்யவும் அல்லது இழுத்து விடவும்' : 'Click or drag & drop image / PDF report';
    }

    const uploadSub = document.getElementById('doc-upload-sub');
    if(uploadSub && (!uploadTitle || !uploadTitle.dataset.fileName)){
        uploadSub.textContent = isTa ? 'PNG, JPG, PDF, DOCX (அதிகபட்சம் 16MB)' : 'PNG, JPG, PDF, DOCX (Max 16MB)';
    } else if(uploadSub && uploadTitle && uploadTitle.dataset.fileName){
        uploadSub.textContent = isTa ? 'பகுப்பாய்வு செய்யப்பட்டது (Vision OCR)' : 'Preprocessed & Grounded (Vision OCR)';
    }

    const textInput = document.getElementById('direct-doc-text');
    if(textInput){
        textInput.placeholder = isTa ? 'அல்லது மருந்துச் சீட்டு / ஆய்வக அறிக்கை உரையை இங்கு ஒட்டவும்...' : 'Or paste prescription / lab report text here...';
    }

    const analyzeBtn = document.getElementById('analyze-btn');
    if(analyzeBtn && !analyzeBtn.disabled){
        analyzeBtn.innerHTML = `✨ ${isTa ? 'AI கொண்டு பகுப்பாய்வு செய்' : 'Analyze with AI'}`;
    }

    const clearBtn = document.getElementById('doc-clear-btn');
    if(clearBtn) clearBtn.textContent = isTa ? 'அழி' : 'Clear';

    // ── RIGHT CARD GLOBAL UPDATES ──
    const botTitle = document.getElementById('doc-chatbot-title');
    if(botTitle) botTitle.textContent = isTa ? 'மருத்துவ ஆவண சாட்பாட்' : 'AI Document Chatbot';

    const botSub = document.getElementById('doc-chatbot-sub');
    if(botSub) botSub.textContent = `● ${isTa ? 'உள்ளூர் AI உதவியாளர் (Gemma 4 E4B)' : 'Local AI Assistant (Gemma 4 E4B)'}`;

    const voiceBtn = document.getElementById('voice-toggle-btn');
    if(voiceBtn){
        voiceBtn.textContent = (A.voiceAutoReply !== false)
            ? (isTa ? '🔊 குரல் பதில்: ஆன்' : '🔊 Voice Reply: ON')
            : (isTa ? '🔈 குரல் பதில்: ஆஃப்' : '🔈 Voice Reply: OFF');
    }

    const readAloudBtn = document.getElementById('doc-read-aloud-btn');
    if(readAloudBtn) readAloudBtn.innerHTML = `🔊 ${isTa ? 'வாசிக்கவும்' : 'Read Aloud'}`;

    const chatInput = document.getElementById('doc-chat-input');
    if(chatInput){
        chatInput.placeholder = isTa ? 'கேள்வி கேட்கவும் (அல்லது மைக் அழுத்தவும்)...' : 'Ask anything about this report...';
    }

    const sendBtn = document.getElementById('doc-chat-send-btn');
    if(sendBtn) sendBtn.textContent = isTa ? 'அனுப்பு' : 'Send';

    // Update initial welcome bubble if conversation hasn't had user messages yet
    if(docChatHistory.length === 0){
        const welcomeBubble = document.getElementById('doc-chat-welcome') || document.querySelector('#doc-chat-stream .chat-bubble.bot');
        if(welcomeBubble){
            welcomeBubble.textContent = isTa
                ? 'வணக்கம்! இடதுபுறத்தில் ஒரு மருத்துவ அறிக்கையை பதிவேற்றவும் அல்லது மாதிரியைத் தேர்ந்தெடுக்கவும். நான் அதை ஆய்வு செய்து, உங்கள் கேள்விகளுக்கு எளிய முறையில் பதிலளிப்பேன்.'
                : 'Hello! Upload a medical report on the left or select a sample. I will extract findings and answer any questions about your diagnosis, tests, and medications.';
        }
    }

    // Refresh dynamic widgets
    updateActiveBadge();
    renderDocPromptChips();
    renderReportList();
    renderDocFactsBox();
}

function renderDocPromptChips(){
    const container = document.getElementById('doc-chat-chips');
    if(!container) return;
    if(docChatLang === 'Tamil'){
        container.innerHTML = `
            <button onclick="askDocQuick('இந்த அறிக்கையை எளிய தமிழில் விளக்குங்கள்')">💡 எளிதாக விளக்கு</button>
            <button onclick="askDocQuick('எந்த test result abnormal-ஆக உள்ளது?')">⚠️ Abnormal values?</button>
            <button onclick="askDocQuick('என் report-ல் உள்ள medications என்ன?')">💊 மருந்துகள்</button>
            <button onclick="askDocQuick('நான் எந்த doctor-ஐ பார்க்க வேண்டும்?')">👨‍⚕️ எந்த doctor?</button>
            <button onclick="askDocQuick('என் report-ல் உள்ள முக்கியமான விவரங்கள் என்ன?')">📋 முக்கிய விவரங்கள்</button>
        `;
    } else {
        container.innerHTML = `
            <button onclick="askDocQuick('Explain this report in simple words')">💡 Explain simply</button>
            <button onclick="askDocQuick('Are any of my test results abnormal?')">⚠️ Any abnormal values?</button>
            <button onclick="askDocQuick('What are the prescribed medications?')">💊 Medications</button>
            <button onclick="askDocQuick('Which doctor specialty should I visit?')">👨‍⚕️ Which doctor?</button>
            <button onclick="askDocQuick('தமிழில் இந்த அறிக்கையின் முக்கிய விவரங்களை விளக்குங்கள்')">🇮🇳 தமிழில் விளக்குக</button>
        `;
    }
}

function classifyUserIntent(msg, currentDocLang){
    const raw = (msg || '').trim().toLowerCase();

    // Check for explicit language switch requests
    const tamilSwitchPatterns = [
        /^(tamil|தமிழ்|தமிள்)$/i,
        /^(change|switch|translate|speak|explain|tell|reply|convert|talk)\s*(to|in|into)?\s*(tamil|தமிழ்)\b/i,
        /\b(tamil\s*la\s*(explain|sollu|pesu|solunga|pannu|paru))\b/i,
        /\b(in\s*tamil|tamilil|tamil\s*version|tamil\s*please)\b/i,
        /^(தமிழில்\s*(விளக்கு|கூறு|பேசு|சொல்லு|விளக்குக))\b/i
    ];
    for(const p of tamilSwitchPatterns){
        if(p.test(raw)) return { type: 'LANG_COMMAND', targetLang: 'Tamil' };
    }

    const englishSwitchPatterns = [
        /^(english|ஆங்கிலம்)$/i,
        /^(change|switch|translate|speak|explain|tell|reply|convert|talk)\s*(to|in|into)?\s*(english|ஆங்கிலம்)\b/i,
        /\b(english\s*la\s*(explain|sollu|pesu|solunga|pannu|paru))\b/i,
        /\b(in\s*english|english\s*version|english\s*please)\b/i,
        /^(ஆங்கிலத்தில்\s*(விளக்கு|கூறு|பேசு|சொல்லு))\b/i
    ];
    for(const p of englishSwitchPatterns){
        if(p.test(raw)) return { type: 'LANG_COMMAND', targetLang: 'English' };
    }

    // Check for out-of-domain queries
    const outOfDomain = /\b(prime minister|president|weather|forecast|joke|riddle|python|javascript|coding|movie|cricket|football|capital of|who wrote|who invented|write a poem|write code|sing a song|recipe)\b/i;
    if(outOfDomain.test(raw)){
        return { type: 'OUT_OF_DOMAIN' };
    }

    return { type: 'MEDICAL_QUERY' };
}

function renderReportList(){
    const container = document.getElementById('doc-reports-list');
    if(!container) return;

    if(!patientSession.reports || patientSession.reports.length === 0){
        container.innerHTML = '';
        container.style.display = 'none';
        return;
    }

    const isTa = (docChatLang === 'Tamil');
    container.style.display = 'flex';
    const repCount = patientSession.reports.length;
    const repCountStr = isTa
        ? (repCount === 1 ? '1 அறிக்கை செயலில் உள்ளது' : `${repCount} அறிக்கைகள் செயலில் உள்ளன`)
        : `${repCount} ${repCount === 1 ? 'Report' : 'Reports'} Active`;

    let html = `
        <div class="doc-patient-banner">
            <span>👤 ${isTa ? 'நடப்பு நோயாளி:' : 'CURRENT PATIENT:'} <b>${esc(patientSession.name || (isTa ? 'நோயாளி' : 'Active Patient'))}</b></span>
            <span>${repCountStr}</span>
        </div>
    `;

    patientSession.reports.forEach((rep, idx) => {
        let icon = '📄';
        const dt = (rep.document_type || '').toLowerCase();
        if(dt.includes('blood') || dt.includes('lab') || dt.includes('test')) icon = '🩸';
        else if(dt.includes('presc') || dt.includes('rx')) icon = '💊';
        else if(dt.includes('discharge') || dt.includes('hospital')) icon = '🏥';

        html += `
            <div class="report-item-card" id="report-card-${idx}">
                <div class="report-item-info">
                    <div class="report-item-title">
                        <span>${icon}</span>
                        <span>${esc(translateDocType(rep.document_type || 'Medical Report'))}</span>
                    </div>
                    <div class="report-item-meta">
                        📅 ${esc(rep.document_date || 'N/A')} &bull; 📁 ${esc(rep.filename || 'Report')}
                    </div>
                </div>
                <button class="report-item-remove-btn" onclick="removeReport(${idx})" title="${isTa ? 'இந்த அறிக்கையை அகற்று' : 'Remove this report'}">✕</button>
            </div>
        `;
    });

    html += `
        <button class="add-another-report-btn" onclick="document.getElementById('direct-file-input').click()">
            <span>➕</span> ${isTa ? 'அதே நோயாளிக்கு மற்றொரு அறிக்கையைச் சேர்க்கவும்' : 'Add Another Report for Same Patient'}
        </button>
    `;

    container.innerHTML = html;
}

function removeReport(idx){
    if(!patientSession.reports || idx < 0 || idx >= patientSession.reports.length) return;
    patientSession.reports.splice(idx, 1);
    patientReportHistory = patientSession.reports;

    if(patientSession.reports.length === 0){
        clearDocAnalyzer();
        return;
    }

    currentDocAnalysis = patientSession.reports[patientSession.reports.length - 1];
    renderReportList();
    renderDocFactsBox();
    updateActiveBadge();

    const stream = document.getElementById('doc-chat-stream');
    if(stream){
        const notice = document.createElement('div');
        notice.className = 'chat-grounding-notice';
        notice.innerHTML = `🗑️ ${docChatLang === 'Tamil' ? 'அறிக்கை அகற்றப்பட்டது. எஞ்சியவை ஆய்வு செய்யப்பட்டுள்ளன.' : 'Report removed from patient context.'}`;
        stream.appendChild(notice);
        stream.scrollTop = stream.scrollHeight;
    }
}


const SAMPLE_DOCS = {
    blood_test: `SRI RAMAKRISHNA HOSPITAL CLINICAL LABORATORY
Patient: Ramesh Kumar, Age: 52, Gender: Male, Date: 18-Sep-2026
TEST RESULTS:
- Fasting Blood Sugar (FBS): 168 mg/dL (Normal: 70-100) [HIGH]
- Post Prandial Blood Sugar (PPBS): 242 mg/dL (Normal: < 140) [HIGH]
- HbA1c (Glycated Hemoglobin): 8.6 % (Target: < 7.0 %) [ELEVATED - UNCONTROLLED DIABETES]
- Serum Creatinine: 1.4 mg/dL (Normal: 0.7 - 1.2) [BORDERLINE HIGH]
- Blood Urea Nitrogen (BUN): 28 mg/dL (Normal: 7 - 20) [HIGH]
- Total Cholesterol: 238 mg/dL (Normal: < 200) [HIGH]
- Blood Pressure Recorded: 146/92 mmHg [STAGE 1 HYPERTENSION]
Impression: Uncontrolled Type 2 Diabetes Mellitus with early diabetic nephropathy markers and dyslipidemia.
Doctor Note: Immediate lifestyle review, dosage adjustment of anti-diabetic agents, and nephrology follow-up advised.`,

    prescription: `DR. S. MEENAKSHI, MD (GEN MED)
APOLLO MULTISPECIALTY CLINIC
Date: 12-Sep-2026 | Patient: Sangeetha Rajan, 46 F
Diagnosis: Essential Hypertension, Dyspepsia, Chronic Low Back Pain
Rx:
1. Tab Telmisartan 40 mg - 1 tablet once daily morning after food (1-0-0) x 30 days
2. Tab Pantoprazole 40 mg - 1 tablet once daily before breakfast (1-0-0) x 14 days
3. Tab Paracetamol 650 mg - 1 tablet as needed for severe pain (SOS), max 3 per day
4. Cap Calcium with Vitamin D3 - 1 capsule once daily with dinner x 30 days
Special Instructions: Salt-restricted diet (< 5g/day), regular BP tracking twice weekly, avoid empty-stomach NSAIDs.
Review after 4 weeks with BP chart.`,

    discharge: `CITY GENERAL HOSPITAL - DISCHARGE SUMMARY
Admission Date: 14-Sep-2026 | Discharge Date: 17-Sep-2026
Patient: Sundaram P., Age: 61, Male
Final Diagnosis: Unstable Angina, Coronary Artery Disease (CAD), Controlled Hypertension
Presenting Complaints: Retrosternal chest discomfort radiating to left arm with diaphoresis on exertion.
Clinical Course:
- Troponin-I: Negative (0.02 ng/mL)
- 12-lead ECG: T-wave inversion in V4-V6
- 2D Echocardiogram: LVEF 55%, mild anterior wall hypokinesia
- Coronary Angiogram: 70% stenosis in mid-LAD, managed medically.
Discharge Medications:
- Tab Aspirin 75 mg OD after lunch
- Tab Clopidogrel 75 mg OD after lunch
- Tab Atorvastatin 40 mg at bedtime
- Tab Metoprolol Succinate 25 mg OD morning
Red Flags / Alert: Return immediately to Emergency if recurrent chest pain > 10 minutes, breathlessness, or syncope occur.
Follow-up: Cardiology OPD after 7 days.`
};

function openDocChat(trackHistory=true){
    if(trackHistory) return navigateTo('document-chat',()=>openDocChat(false));
    shell(t('docChat'), `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div>
        <p style="margin:0;color:#597174;font-size:14px">
          ${A.lang==='Tamil'
            ? 'மருத்துவ அறிக்கைகள் (PDF, PNG, JPG) பதிவேற்றவும் அல்லது மாதிரியை தேர்வு செய்யவும். AI தானாக பகுப்பாய்வு செய்து கேள்விகளுக்கு பதிலளிக்கும்.'
            : 'Upload a prescription, lab report or discharge summary. AI extracts clinical facts and answers your questions interactively.'}
        </p>
      </div>
      <button type="button" class="secondary" style="margin:0" onclick="goHome()">← ${A.lang==='Tamil'?'முகப்பு பக்கம்':'Back to Home'}</button>
    </div>

    <div class="doc-chat-wrapper">
      <!-- Left Column: Document Upload & Analysis -->
      <div class="doc-panel">
        <h3 style="margin:0 0 12px 0;font-size:18px;color:#102a2d">📄 1. Upload or Select Medical Report</h3>

        <div class="sample-docs-bar">
          <span style="font-size:12px;font-weight:700;color:#0b756b;align-self:center">Sample Reports:</span>
          <button onclick="loadSampleDoc('blood_test')">🩸 Blood Test (HbA1c/Sugar)</button>
          <button onclick="loadSampleDoc('prescription')">💊 Prescription (BP/Meds)</button>
          <button onclick="loadSampleDoc('discharge')">🏥 Discharge Summary (Heart)</button>
        </div>

        <div class="doc-upload-zone" onclick="document.getElementById('direct-file-input').click()">
          <input id="direct-file-input" type="file" accept=".pdf,.png,.jpg,.jpeg,.docx,.txt" style="display:none" onchange="handleDirectFileUpload(this)">
          <div style="font-size:32px;margin-bottom:8px">📂</div>
          <b style="color:#0b756b">Click to upload report image or PDF</b>
          <div style="font-size:12px;color:#6b8284;margin-top:4px">Supports PNG, JPG, PDF, DOCX, TXT (Max 16MB)</div>
        </div>

        <label style="font-size:12px;font-weight:700;color:#456">Or paste medical report text:</label>
        <textarea id="direct-doc-text" rows="5" placeholder="Paste prescription or lab report text here..." style="font-size:13px"></textarea>

        <div style="display:flex;gap:10px;margin-top:12px">
          <button id="analyze-btn" class="primary" style="flex:1;margin:0" onclick="runDirectDocAnalyze()">
            ✨ Analyze with AI
          </button>
          <button class="secondary" style="margin:0" onclick="clearDocAnalyzer()">Clear</button>
        </div>

        <!-- Extraction Results View -->
        <div id="doc-analysis-results" style="display:none">
          <div class="doc-facts-box" id="doc-facts-content"></div>
        </div>
      </div>

      <!-- Right Column: Interactive AI Document Chatbot -->
      <div class="chat-window">
        <div class="chat-window-head">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="mark" style="width:32px;height:32px;font-size:16px;border-radius:8px">AI</span>
            <div>
              <b style="font-size:14px;color:#102a2d">MediKiosk Document Chatbot</b>
              <div style="font-size:11px;color:#0b756b;display:flex;align-items:center;gap:6px">
                <span>● Grounded Assistant</span>
                <span id="doc-speaking-badge" style="color:#718096;font-weight:600">● Stopped</span>
              </div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:6px">
            <button id="doc-tts-stop-btn" class="secondary" style="display:none;padding:4px 10px;font-size:12px;margin:0;background:#fff0f0;color:#c5221f;border-color:#feb2b2;font-weight:700" onclick="stopTTS()">⏹ Stop</button>
            <button class="secondary" style="padding:4px 10px;font-size:12px;margin:0" onclick="speakDocContext()">🔊 Read Summary</button>
          </div>
        </div>

        <div class="chat-stream" id="doc-chat-stream">
          <div class="chat-bubble bot">
            ${A.lang==='Tamil'
              ? 'வணக்கம்! இடதுபுறத்தில் ஒரு மருத்துவ அறிக்கையை பதிவேற்றவும் அல்லது மாதிரியைத் தேர்ந்தெடுக்கவும். நான் அதை படித்து, உங்கள் கேள்விகளுக்கு தெளிவான விளக்கங்களை வழங்குவேன்.'
              : 'Hello! Please upload a medical document or choose a sample on the left. I will analyze the clinical findings, medication dosages, and explain what your test results mean.'}
          </div>
        </div>

        <!-- Quick prompt chips -->
        <div class="chat-prompt-chips">
          <button onclick="askDocQuick('Explain this report in simple words')">💡 Explain in simple terms</button>
          <button onclick="askDocQuick('Are any of my test results abnormal or critical?')">⚠️ Any abnormal values?</button>
          <button onclick="askDocQuick('What are the prescribed medications and dosages?')">💊 List all medications</button>
          <button onclick="askDocQuick('Which doctor specialty should I visit?')">👨‍⚕️ Which doctor to visit?</button>
          <button onclick="askDocQuick('தமிழில் இந்த அறிக்கையின் முக்கிய விவரங்களை விளக்குங்கள்')">🇮🇳 தமிழில் விளக்குக</button>
        </div>

        <!-- Input bar with mic and send -->
        <div class="chat-input-bar">
          <input id="doc-chat-input" placeholder="${A.lang==='Tamil'?'ஆவணம் பற்றி கேளுங்கள் (அல்லது மைக்கை அழுத்தவும்)...':'Ask anything about this medical report...'}" onkeydown="if(event.key==='Enter')sendDocChatMessage()">
          <button id="doc-chat-mic" class="chat-mic-btn" onclick="toggleDocChatMic()" title="Speak your question">🎙️</button>
          <button class="chat-send-btn" onclick="sendDocChatMessage()">Send</button>
        </div>
      </div>
    </div>
    `);

    docChatHistory = [];
    currentDocAnalysis = null;
}

function loadSampleDoc(type){
    const text = SAMPLE_DOCS[type];
    if(!text) return;
    const input = document.getElementById('direct-doc-text');
    if(input){
        input.value = text;
        const nameMap = {
            blood_test: 'Sample_Blood_Test_Ramesh_Kumar.txt',
            prescription: 'Sample_Prescription_Sangeetha_Rajan.txt',
            discharge: 'Sample_Discharge_Sundaram.txt'
        };
        runDirectDocAnalyze(null, nameMap[type] || 'Sample_Report.txt');
    }
}

function handleDirectFileUpload(input){
    const f = input.files[0];
    if(!f) return;
    runDirectDocAnalyze(f);
}

function clearDocAnalyzer(){
    const textInput = document.getElementById('direct-doc-text');
    const fileInput = document.getElementById('direct-file-input');
    const resBox = document.getElementById('doc-analysis-results');
    const uploadTitle = document.getElementById('doc-upload-title');
    const uploadSub = document.getElementById('doc-upload-sub');
    const uploadIcon = document.getElementById('doc-upload-icon');
    const activeBadge = document.getElementById('doc-active-badge');
    const stream = document.getElementById('doc-chat-stream');

    if(textInput) textInput.value = '';
    if(fileInput) fileInput.value = '';
    if(resBox) resBox.style.display = 'none';

    if(uploadTitle){
        delete uploadTitle.dataset.fileName;
        uploadTitle.textContent = (docChatLang === 'Tamil' ? 'அறிக்கை கோப்பை பதிவேற்ற கிளிக் செய்யவும் அல்லது இழுத்து விடவும்' : 'Click or drag & drop image / PDF report');
    }
    if(uploadSub) uploadSub.textContent = (docChatLang === 'Tamil' ? 'PNG, JPG, PDF, DOCX (அதிகபட்சம் 16MB)' : 'PNG, JPG, PDF, DOCX (Max 16MB)');
    if(uploadIcon) uploadIcon.textContent = '📂';
    if(activeBadge) activeBadge.style.display = 'none';

    // COMPLETE STATE RESET - Prevents cross-patient data leakage
    currentDocAnalysis = null;
    docChatHistory = [];
    patientReportHistory = [];
    patientSession = { name: null, reports: [] };

    renderReportList();

    if(stream){
        stream.innerHTML = `<div class="chat-bubble bot" id="doc-chat-welcome">
            ${docChatLang === 'Tamil'
                ? 'அனைத்து அறிக்கைகளும் அழிக்கப்பட்டன. புதிய நோயாளிக்கான மருத்துவ அறிக்கையை பதிவேற்றவும்.'
                : 'All reports cleared. Upload or scan a new medical report anytime.'}
        </div>`;
    }
}

function handleDropUpload(e){
    if(e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0){
        const f = e.dataTransfer.files[0];
        runDirectDocAnalyze(f);
    }
}

function toggleVoiceAutoReply(){
    A.voiceAutoReply = (A.voiceAutoReply === false) ? true : false;
    localStorage.mk_voice_auto = A.voiceAutoReply ? '1' : '0';
    const btn = document.getElementById('voice-toggle-btn');
    if(btn){
        const isTa = (docChatLang === 'Tamil');
        btn.textContent = A.voiceAutoReply 
            ? (isTa ? '🔊 குரல் பதில்: ஆன்' : '🔊 Voice Reply: ON')
            : (isTa ? '🔈 குரல் பதில்: ஆஃப்' : '🔈 Voice Reply: OFF');
    }
}

// ── Medical Report Scanner Workflow ──────────────────────────────
let scannerStream = null;
let scannerVideoDevices = [];
let currentScannerDeviceIndex = 0;

async function openMedicalReportScanner(){
    let modal = document.getElementById('medical-scanner-modal');
    if(!modal){
        modal = document.createElement('div');
        modal.id = 'medical-scanner-modal';
        modal.className = 'scanner-modal-backdrop';
        document.body.appendChild(modal);
    }
    const isTa = (docChatLang === 'Tamil');

    modal.innerHTML = `
      <div class="scanner-modal-card">
        <div class="scanner-head">
          <div style="display:flex;align-items:center;gap:10px">
            <span style="font-size:22px">🖨️</span>
            <div>
              <b style="font-size:15px;color:#fff">${isTa?'மருத்துவ அறிக்கை ஸ்கேனர்':'Medical Report Scanner'}</b>
              <div style="font-size:11px;color:#0bdaaf">● Hospital Document Intake (Multimodal Vision OCR)</div>
            </div>
          </div>
          <button class="close-modal-btn" onclick="closeMedicalScanner()" style="color:#fff">✕</button>
        </div>

        <div class="scanner-viewport-box" id="scanner-viewport">
          <video id="scanner-video" class="scanner-video-feed" autoplay playsinline muted></video>
          <div class="scanner-laser-bar" id="scanner-laser"></div>
          <div class="scanner-doc-frame">
            <span class="scanner-corner tl"></span>
            <span class="scanner-corner tr"></span>
            <span class="scanner-corner bl"></span>
            <span class="scanner-corner br"></span>
            <div class="scanner-frame-label">📄 ${isTa?'அறிக்கையை சட்டத்திற்குள் சீரமைக்கவும்':'ALIGN PHYSICAL REPORT WITHIN FRAME'}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.75);background:rgba(0,0,0,0.5);padding:3px 10px;border-radius:10px">
              Auto-Deskew &bull; Contrast Boost &bull; Handwriting-Aware OCR
            </div>
          </div>

          <!-- Camera Inactive Fallback -->
          <div id="scanner-cam-fallback" style="display:none;position:absolute;inset:0;background:#081314;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:24px;text-align:center">
            <div style="font-size:36px">📷</div>
            <b style="color:#e0ecea">${isTa?'கேமரா கண்டறியப்படவில்லை':'Scanner Camera Stream Inactive'}</b>
            <p style="font-size:12px;color:#859e9c;max-width:360px;margin:0">
              ${isTa?'உங்கள் ஸ்கேனர் அல்லது சாதனத்திலிருந்து கோப்பை நேரடியாகத் தேர்ந்தெடுக்கலாம்.':'You can feed a scanned document image or capture directly from device.'}
            </p>
            <button class="primary" onclick="document.getElementById('scanner-file-feed').click()" style="padding:10px 18px;margin-top:6px">
              📁 ${isTa?'ஸ்கேன் செய்யப்பட்ட கோப்பைத் தேர்ந்தெடு':'Select Scanned Report File'}
            </button>
          </div>

          <!-- Processing Overlay -->
          <div id="scanner-proc-overlay" class="scanner-processing-overlay" style="display:none">
            <div style="font-size:32px">⚙️</div>
            <b style="font-size:15px;color:#0bdaaf">${isTa?'ஆவணம் செயலாக்கப்படுகிறது...':'Preprocessing & Extracting...'}</b>
            <div style="font-size:12px;color:#b5d4cf">
              Rotation correction &bull; Sharpness boost &bull; Handwriting OCR &bull; Clinical Extraction
            </div>
          </div>
        </div>

        <div class="scanner-controls">
          <input type="file" id="scanner-file-feed" accept="image/*,.pdf" style="display:none" onchange="handleScannerFileFeed(this)">
          <button class="secondary" style="margin:0;padding:10px 14px;font-size:12px" onclick="document.getElementById('scanner-file-feed').click()">
            📁 ${isTa?'கோப்பு feed':'Feed File'}
          </button>
          <button class="primary" id="scanner-capture-btn" style="margin:0;padding:12px 24px;font-size:14px;font-weight:800;background:#00a884" onclick="captureScannerSnapshot()">
            📸 ${isTa?'ஸ்கேன் செய்':'Capture & Scan'}
          </button>
          <button class="secondary" id="scanner-switch-btn" style="margin:0;padding:10px 14px;font-size:12px;display:none" onclick="switchScannerCamera()">
            🔄 ${isTa?'மாற்று':'Switch'}
          </button>
        </div>
      </div>
      <canvas id="scanner-canvas" style="display:none"></canvas>
    `;
    modal.style.display = 'flex';
    startScannerCamera();
}

async function startScannerCamera(deviceId){
    const video = document.getElementById('scanner-video');
    const fallback = document.getElementById('scanner-cam-fallback');
    if(!video) return;

    if(scannerStream){
        scannerStream.getTracks().forEach(t => t.stop());
        scannerStream = null;
    }

    if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia){
        if(fallback) fallback.style.display = 'flex';
        return;
    }

    try {
        const constraints = {
            video: deviceId ? { deviceId: { exact: deviceId } } : { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1080 } }
        };
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        scannerStream = stream;
        video.srcObject = stream;
        video.play();
        if(fallback) fallback.style.display = 'none';

        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            scannerVideoDevices = devices.filter(d => d.kind === 'videoinput');
            const switchBtn = document.getElementById('scanner-switch-btn');
            if(switchBtn && scannerVideoDevices.length > 1){
                switchBtn.style.display = 'inline-block';
            }
        } catch(e){}
    } catch(err){
        console.warn('Camera access unavailable, showing file selector fallback:', err);
        if(fallback) fallback.style.display = 'flex';
    }
}

function switchScannerCamera(){
    if(scannerVideoDevices.length <= 1) return;
    currentScannerDeviceIndex = (currentScannerDeviceIndex + 1) % scannerVideoDevices.length;
    startScannerCamera(scannerVideoDevices[currentScannerDeviceIndex].deviceId);
}

function closeMedicalScanner(){
    if(scannerStream){
        scannerStream.getTracks().forEach(t => t.stop());
        scannerStream = null;
    }
    const modal = document.getElementById('medical-scanner-modal');
    if(modal){
        modal.style.display = 'none';
    }
}

function captureScannerSnapshot(){
    const video = document.getElementById('scanner-video');
    const canvas = document.getElementById('scanner-canvas');
    const procOverlay = document.getElementById('scanner-proc-overlay');
    const captureBtn = document.getElementById('scanner-capture-btn');

    if(!video || !canvas) return;

    if(!scannerStream || video.videoWidth === 0){
        document.getElementById('scanner-file-feed')?.click();
        return;
    }

    canvas.width = video.videoWidth || 1280;
    canvas.height = video.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    if(procOverlay) procOverlay.style.display = 'flex';
    if(captureBtn) captureBtn.disabled = true;

    canvas.toBlob(blob => {
        if(!blob){
            alert('Failed to capture frame.');
            closeMedicalScanner();
            return;
        }
        const scannedFile = new File([blob], `scanned_report_${Date.now()}.jpg`, { type: 'image/jpeg' });
        setTimeout(() => {
            closeMedicalScanner();
            runDirectDocAnalyze(scannedFile);
        }, 400);
    }, 'image/jpeg', 0.95);
}

function handleScannerFileFeed(input){
    const f = input.files[0];
    if(!f) return;
    closeMedicalScanner();
    runDirectDocAnalyze(f);
}

function verifyDocPatientName(){
    if(!currentDocAnalysis) return;
    const isTa = (docChatLang === 'Tamil');
    const cur = currentDocAnalysis.analysis?.patient_name || '';
    const updated = prompt(isTa ? 'இந்த அறிக்கைக்கான சரியான நோயாளி பெயரை உறுதிப்படுத்தவும் அல்லது உள்ளிடவும்:' : 'Confirm or enter the correct Patient Name for this report:', cur);
    if(updated && updated.trim()){
        currentDocAnalysis.analysis.patient_name = updated.trim();
        currentDocAnalysis.analysis.patient_identity_verified = true;
        currentDocAnalysis.analysis.identity_confidence = 1.0;
        if(patientSession) patientSession.name = updated.trim();
        renderDocFactsBox();
        renderReportList();
    }
}

function renderDocFactsBox(){
    if(!currentDocAnalysis) return;
    const a = currentDocAnalysis.analysis || {};
    const res = currentDocAnalysis;
    const factsContent = document.getElementById('doc-facts-content');
    if(!factsContent) return;
    const isTa = (docChatLang === 'Tamil');

    let medsHtml = (a.medications && a.medications.length)
        ? a.medications.map(m => `<li><b>${esc(m.name || m)}</b>: ${esc(m.dosage||'')} ${esc(m.frequency||'')}</li>`).join('')
        : `<i>${isTa ? 'கண்டறியப்படவில்லை' : 'None detected'}</i>`;

    let invHtml = (a.investigations && a.investigations.length)
        ? a.investigations.map(i => {
            const isAb = (i.status==='ABNORMAL' || i.status==='CRITICAL') || /high|elevated|positive|abnormal/i.test(String(i.test||''));
            return `<div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:12px">
                <span>${esc(i.test || i)}</span>
                <b style="color:${isAb?'#c5221f':'#0b7a42'}">${esc(i.value||'')} ${i.unit?esc(i.unit):''} ${isAb?'⚠️':''}</b>
            </div>`;
        }).join('')
        : `<i>${isTa ? 'கண்டறியப்படவில்லை' : 'None detected'}</i>`;

    let flagsHtml = (a.red_flags && a.red_flags.length)
        ? a.red_flags.map(f => `<div class="alert" style="padding:8px 12px;margin:4px 0">⚠️ ${esc(f)}</div>`).join('')
        : `<span style="color:#0b7a42;font-weight:700">✓ ${isTa ? 'அவசர எச்சரிக்கைகள் எதுவும் இல்லை' : 'No immediate emergency red flags'}</span>`;

    const isVerified = a.patient_identity_verified && (a.identity_confidence >= 0.8);
    const confPct = Math.round((a.identity_confidence || 0.85) * 100);

    let identityBox = isVerified
        ? `<div class="badge-verified" style="margin-bottom:8px">
             <span>👤 ${isTa ? 'நோயாளி:' : 'Patient:'}</span> <b>${esc(a.patient_name || (isTa ? 'சரிபார்க்கப்பட்ட நோயாளி' : 'Verified Patient'))}</b>
             <span style="font-size:11px;opacity:0.8">(${confPct}% ${isTa ? 'நம்பகத்தன்மை' : 'confidence'} ✓)</span>
           </div>`
        : `<div class="badge-verify-prompt">
             <div>
               <span>👤 ${isTa ? 'நோயாளி:' : 'Patient:'} <b>${esc(a.patient_name || 'Uncertain ???')}</b></span>
               <div style="font-size:11px;opacity:0.85">${isTa ? 'குறைந்த OCR நம்பிக்கை' : 'Low OCR confidence'} (${confPct}%) &bull; ${isTa ? 'சரிபார்க்கவும்' : 'Please verify'}</div>
             </div>
             <button class="secondary" style="margin:0;padding:4px 10px;font-size:11px;font-weight:700" onclick="verifyDocPatientName()">${isTa ? 'சரிபார் / திருத்து' : 'Confirm / Edit'}</button>
           </div>`;

    factsContent.innerHTML = `
        ${identityBox}
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span class="option-tag" style="background:#0b756b;color:#fff">${esc(translateDocType(a.document_type || 'MEDICAL_RECORD'))}</span>
          <span class="option-tag" style="background:#eaf2fe;color:#185abc">${isTa ? 'துறை' : 'Dept'}: ${esc(a.recommended_department || (isTa ? 'பொது மருத்துவம்' : 'General Medicine'))}</span>
        </div>
        <div style="font-size:11px;color:#6b8284;margin-bottom:8px">
          ${a.document_date ? (isTa ? '📅 தேதி: ' : '📅 Date: ') + esc(a.document_date) + ' &bull; ' : ''}
          ${a.doctor_name ? '👨‍⚕️ ' + esc(a.doctor_name) + ' &bull; ' : ''}
          ${a.hospital_name ? '🏥 ' + esc(a.hospital_name) : ''}
        </div>
        <div class="fact-item">
          <b>${isTa ? 'சுருக்கம்:' : 'Summary:'}</b>
          <div>${esc(a.clinical_summary || res.raw_text?.slice(0, 200) || '')}</div>
        </div>
        <div class="fact-item">
          <b>${isTa ? 'நோய் கண்டறிதல் / மருத்துவ பதிவுகள்:' : 'Diagnoses / Documented Impressions:'}</b>
          <div>${(a.conditions || []).map(c => `<span class="pill" style="margin:2px 4px 2px 0">${esc(c)}</span>`).join('') || (isTa ? 'பட்டியலிடப்படவில்லை' : 'None listed')}</div>
        </div>
        <div class="fact-item">
          <b>${isTa ? 'ஆய்வக பரிசோதனை முடிவுகள்:' : 'Investigations & Lab Values:'}</b>
          <div>${invHtml}</div>
        </div>
        <div class="fact-item">
          <b>${isTa ? 'மருந்துகள் & அளவுகள்:' : 'Medications:'}</b>
          <ul style="margin:4px 0;padding-left:18px">${medsHtml}</ul>
        </div>
        <div class="fact-item">
          <b>${isTa ? 'பாதுகாப்பு & எச்சரிக்கைகள்:' : 'Safety Screening:'}</b>
          <div>${flagsHtml}</div>
        </div>
    `;
}

async function runDirectDocAnalyze(file, customFilename){
    const btn = document.getElementById('analyze-btn');
    const text = document.getElementById('direct-doc-text')?.value || '';
    const resContainer = document.getElementById('doc-analysis-results');
    const uploadTitle = document.getElementById('doc-upload-title');
    const uploadSub = document.getElementById('doc-upload-sub');
    const uploadIcon = document.getElementById('doc-upload-icon');
    const isTa = (docChatLang === 'Tamil');

    if(!file && !text.trim()){
        alert(isTa ? 'தயவுசெய்து ஒரு கோப்பைத் தேர்ந்தெடுக்கவும் அல்லது மருத்துவ உரையை உள்ளிடவும்.' : 'Please select a file, scan a document, or paste medical text first.');
        return;
    }

    const docDisplayName = customFilename || (file ? file.name : (isTa ? 'உரை அறிக்கை' : 'Medical Text'));

    if(uploadTitle){
        uploadTitle.dataset.fileName = docDisplayName;
        uploadTitle.textContent = '📄 ' + docDisplayName;
        if(uploadSub) uploadSub.textContent = isTa ? 'செயலாக்கம் மற்றும் பகுப்பாய்வு...' : `Processing & Preprocessing (${file ? Math.round(file.size/1024) + ' KB' : 'Text'})...`;
        if(uploadIcon) uploadIcon.textContent = '⏳';
    }

    if(btn){
        btn.disabled = true;
        btn.textContent = isTa ? '⏳ செயலாக்கப்படுகிறது...' : '⏳ Preprocessing & OCR...';
    }

    try {
        let res;
        if(file){
            const fd = new FormData();
            fd.append('file', file);
            res = await fetch('/api/ai/doc-analyze', {
                method: 'POST',
                body: fd
            }).then(x => x.json());
        } else {
            res = await fetch('/api/ai/doc-analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            }).then(x => x.json());
        }

        if(!res.success){
            if(uploadTitle){
                uploadTitle.textContent = isTa ? '⚠️ பகுப்பாய்வு தோல்வி' : '⚠️ Intake Failed';
                if(uploadSub) uploadSub.textContent = res.error || (isTa ? 'கோப்பு வடிவமைப்பை சரிபார்க்கவும்' : 'Check document format');
                if(uploadIcon) uploadIcon.textContent = '❌';
            }
            alert((isTa ? 'பகுப்பாய்வு பிழை: ' : 'Analysis error: ') + (res.error || 'Could not analyze document'));
            return;
        }

        const a = res.analysis || {};
        const repPatientName = (a.patient_name && a.patient_name !== 'Uncertain ???') ? a.patient_name : null;

        // RULE 9A: Patient mismatch detection
        if(patientSession.name && repPatientName && isPatientNameMismatch(patientSession.name, repPatientName)){
            const promptMsg = isTa
                ? `எச்சரிக்கை: நடப்பு அறிக்கையின் நோயாளி (${patientSession.name}) மற்றும் புதிய அறிக்கையின் நோயாளி (${repPatientName}) வேறுபடுகின்றனர்!\n\nஇரண்டையும் ஒரே நோயாளியாக இணைக்கவா? ('Cancel' அழுத்தினால் புதிய அமர்வாக தொடங்கும்)`
                : `Patient mismatch detected!\n\nExisting report patient: "${patientSession.name}"\nNewly uploaded report patient: "${repPatientName}"\n\nDo you want to combine them anyway? Click Cancel to start fresh for ${repPatientName}.`;
            
            const combine = confirm(promptMsg);
            if(!combine){
                patientSession = { name: repPatientName, reports: [] };
                docChatHistory = [];
                const stream = document.getElementById('doc-chat-stream');
                if(stream){
                    stream.innerHTML = `<div class="chat-bubble bot" id="doc-chat-welcome">
                        ${isTa
                            ? `புதிய நோயாளி <b>${esc(repPatientName)}</b> அறிக்கைக்கான அமர்வு துவங்கப்பட்டது.`
                            : `Fresh session started for new patient <b>${esc(repPatientName)}</b>.`}
                    </div>`;
                }
            }
        }

        if(!patientSession.name && repPatientName){
            patientSession.name = repPatientName;
        }

        const reportEntry = {
            id: Date.now(),
            filename: res.filename || docDisplayName,
            document_type: a.document_type || 'Report',
            document_date: a.document_date || 'N/A',
            patient_name: repPatientName || patientSession.name || (isTa ? 'சரிபார்க்கப்பட்ட நோயாளி' : 'Verified Patient'),
            analysis: a,
            raw_text: res.raw_text || ''
        };

        patientSession.reports.push(reportEntry);
        patientReportHistory = patientSession.reports;
        currentDocAnalysis = reportEntry;

        if(uploadTitle){
            uploadTitle.dataset.fileName = docDisplayName;
            uploadTitle.textContent = '✅ ' + docDisplayName;
            if(uploadSub) uploadSub.textContent = isTa ? 'பகுப்பாய்வு செய்யப்பட்டது (Vision OCR)' : `Preprocessed & Grounded (${res.source || 'Vision OCR'})`;
            if(uploadIcon) uploadIcon.textContent = '📋';
        }

        // Render Fact Cards and Reports List on left side
        resContainer.style.display = 'block';
        renderDocFactsBox();
        renderReportList();
        updateActiveBadge();

        const stream = document.getElementById('doc-chat-stream');
        if(stream){
            const notice = document.createElement('div');
            notice.className = 'chat-grounding-notice';
            notice.innerHTML = `📄 <b>${esc(translateDocType(a.document_type || 'Medical Report'))}</b> ${docChatLang==='Tamil'?'வெற்றிகரமாக இணைக்கப்பட்டுள்ளது. உங்கள் கேள்விகளை கேட்கலாம்.':'loaded and grounded. Ask any question when ready.'}`;
            stream.appendChild(notice);
            stream.scrollTop = stream.scrollHeight;
        }

    } catch(err){
        alert((isTa ? 'செயல்முறை தோல்வியடைந்தது: ' : 'Analysis failed: ') + err.message);
    } finally {
        if(btn){
            btn.disabled = false;
            btn.innerHTML = `✨ ${isTa ? 'AI கொண்டு பகுப்பாய்வு செய்' : 'Analyze with AI'}`;
        }
    }
}

function appendChatMessage(sender, html){
    const stream = document.getElementById('doc-chat-stream');
    if(!stream) return;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.innerHTML = html;
    stream.appendChild(bubble);
    stream.scrollTop = stream.scrollHeight;
}

function askDocQuick(promptText){
    const input = document.getElementById('doc-chat-input');
    if(input){
        input.value = promptText;
        sendDocChatMessage();
    }
}

async function sendDocChatMessage(){
    stopTTS();
    const input = document.getElementById('doc-chat-input');
    if(!input) return;
    const msg = input.value.trim();
    if(!msg) return;

    input.value = '';

    // ── STEP 1: Intent Classification
    const intent = classifyUserIntent(msg, docChatLang);

    // Handle Language-Switch Command (e.g. "tamil la explain pannu", "change to english")
    if(intent.type === 'LANG_COMMAND'){
        appendChatMessage('user', esc(msg));
        setDocChatLang(intent.targetLang);
        const reply = (intent.targetLang === 'Tamil')
            ? 'நிச்சயமாக! இனி விளக்கங்கள் அனைத்தும் தமிழில் வழங்கப்படும். உங்கள் மருத்துவ அறிக்கை பற்றி என்ன தெரிந்து கொள்ள வேண்டும்?'
            : 'Switched to English. How can I help you with your medical report?';
        appendChatMessage('bot', `
            <div style="line-height:1.6">${esc(reply)}</div>
            <div style="margin-top:8px;display:flex;align-items:center;gap:8px">
                <button class="secondary btn-inline-tts" style="padding:3px 8px;font-size:11px;margin:0"
                    onclick="toggleInlineTTS(this, '${esc(reply)}', '${intent.targetLang}')">🔊 ${intent.targetLang==='Tamil'?'வாசிக்கவும்':'Listen'}</button>
                <span style="font-size:10px;padding:2px 8px;border-radius:10px;background:#0b756b15;color:#0b756b;font-weight:700">
                    ⚙️ Language Switch &bull; ${intent.targetLang}
                </span>
            </div>
        `);
        docChatHistory.push({ sender: 'Patient', text: msg });
        docChatHistory.push({ sender: 'AI', text: reply });
        if(A.voiceAutoReply !== false){
            speak(reply, intent.targetLang);
        }
        return;
    }

    // Determine effective language for answer
    // If docChatLang === 'Tamil', patient explicitly picked Tamil -> answer in Tamil
    // If docChatLang === 'English', but user types Tamil or Tanglish -> answer in Tamil
    let effectiveLang = docChatLang;
    if(docChatLang === 'English'){
        const msgLang = detectMessageLanguage(msg);
        if(msgLang === 'Tamil') effectiveLang = 'Tamil';
    }

    // Handle Out-Of-Domain queries
    if(intent.type === 'OUT_OF_DOMAIN'){
        appendChatMessage('user', esc(msg));
        const reply = (effectiveLang === 'Tamil')
            ? 'இந்த மருத்துவ அறிக்கை தொடர்பான தகவல்களுக்கு மட்டுமே என்னால் உதவ முடியும். அறிக்கை பற்றிய உங்கள் கேள்விகளைக் கேட்கவும்.'
            : 'I can only assist with medical questions related to this report. Please ask about your tests, medications, or doctor notes.';
        appendChatMessage('bot', `
            <div style="line-height:1.6">${esc(reply)}</div>
            <div style="margin-top:8px;display:flex;align-items:center;gap:8px">
                <button class="secondary btn-inline-tts" style="padding:3px 8px;font-size:11px;margin:0"
                    onclick="toggleInlineTTS(this, '${esc(reply)}', '${effectiveLang}')">🔊 ${effectiveLang==='Tamil'?'வாசிக்கவும்':'Listen'}</button>
                <span style="font-size:10px;padding:2px 8px;border-radius:10px;background:#c5221f15;color:#c5221f;font-weight:700">
                    🛡️ Medical Guard &bull; ${effectiveLang}
                </span>
            </div>
        `);
        docChatHistory.push({ sender: 'Patient', text: msg });
        docChatHistory.push({ sender: 'AI', text: reply });
        if(A.voiceAutoReply !== false){
            speak(reply, effectiveLang);
        }
        return;
    }

    // Show user message in stream
    appendChatMessage('user', esc(msg));

    // ── STEP 2: Build document context (single or multi-report)
    let docContext = '';
    const activeReports = (patientSession.reports && patientSession.reports.length > 0)
        ? patientSession.reports
        : patientReportHistory;

    if(activeReports.length > 1){
        docContext = `PATIENT: ${patientSession.name || 'Active Patient'}\n` +
                     `TOTAL LOADED REPORTS: ${activeReports.length}\n\n` +
                     activeReports.map((rep, idx) => {
                         const ra = rep.analysis || {};
                         const invStr = (ra.investigations || []).map(i =>
                             `${i.test}: ${i.value||'N/A'} ${i.unit||''} [Ref: ${i.reference_range||'N/A'}] [Status: ${i.status||'N/A'}]`
                         ).join('\n');
                         const medStr = (ra.medications || []).map(m =>
                             `${m.name||''} ${m.dosage||''} ${m.frequency||''}`
                         ).join('\n');
                         return `=== REPORT ${idx+1}: ${ra.document_type || 'Medical Report'} (Date: ${ra.document_date || 'N/A'}, File: ${rep.filename}) ===\n` +
                                `Patient: ${ra.patient_name || 'N/A'} (Age: ${ra.patient_age||'N/A'}, Gender: ${ra.patient_gender||'N/A'}, ID: ${ra.patient_id || 'N/A'})\n` +
                                `Doctor: ${ra.doctor_name||'N/A'}, Hospital: ${ra.hospital_name||'N/A'}\n` +
                                `Conditions: ${(ra.conditions || []).join(', ')}\n` +
                                `LAB RESULTS:\n${invStr || 'None recorded'}\n` +
                                `MEDICATIONS:\n${medStr || 'None recorded'}\n` +
                                `Red Flags: ${(ra.red_flags || []).join(', ') || 'None'}\n` +
                                `Clinical Summary: ${ra.clinical_summary || ''}\n`;
                     }).join('\n\n') +
                     `\nINSTRUCTION: The patient has multiple reports loaded above. Cross-reference between them when relevant.`;
    } else if(currentDocAnalysis){
        const a = currentDocAnalysis.analysis || {};
        const invStr = (a.investigations || []).map(i =>
            `${i.test}: ${i.value||'N/A'} ${i.unit||''} [Ref: ${i.reference_range||'N/A'}] [Status: ${i.status||'N/A'}]`
        ).join('\n');
        const medStr = (a.medications || []).map(m =>
            `${m.name||''} ${m.dosage||''} ${m.frequency||''}`
        ).join('\n');
        docContext = `Document Type: ${a.document_type || 'Medical Report'}\n` +
                     `Patient Name: ${a.patient_name || patientSession.name || 'N/A'}\n` +
                     `Patient Age: ${a.patient_age || 'N/A'}, Gender: ${a.patient_gender || 'N/A'}\n` +
                     `Patient ID: ${a.patient_id || 'N/A'}\n` +
                     `Report Date: ${a.document_date || 'N/A'}\n` +
                     `Doctor: ${a.doctor_name || 'N/A'}, Hospital: ${a.hospital_name || 'N/A'}\n` +
                     `Clinical Summary: ${a.clinical_summary || ''}\n` +
                     `Diagnoses/Conditions: ${(a.conditions || []).join(', ')}\n` +
                     `LAB RESULTS:\n${invStr || 'None'}\n` +
                     `MEDICATIONS:\n${medStr || 'None'}\n` +
                     `Red Flags: ${(a.red_flags || []).join(', ') || 'None'}\n` +
                     `Raw OCR Text (first 1500 chars):\n${(currentDocAnalysis.raw_text || '').slice(0, 1500)}`;
    } else {
        const text = document.getElementById('direct-doc-text')?.value || '';
        docContext = text ? `Report text:\n${text.slice(0, 2000)}` : 'No document uploaded yet.';
    }

    docChatHistory.push({ sender: 'Patient', text: msg });

    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    const thinkingMsg = effectiveLang === 'Tamil' ? 'சிந்திக்கிறேன்...' : 'Thinking...';
    appendChatMessage('bot', `<span id="${typingId}">${thinkingMsg}</span>`);

    try {
        // ── STEP 3: Call backend with effective language
        const r = await fetch('/api/ai/doc-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg,
                document_context: docContext,
                language: effectiveLang,
                history: docChatHistory
            })
        }).then(x => x.json());

        const typingEl = document.getElementById(typingId);
        if(typingEl){
            const botReply = r.reply || (effectiveLang === 'Tamil'
                ? 'மன்னிக்கவும், மீண்டும் முயற்சிக்கவும்.'
                : 'I am ready to assist with your medical report.');
            const replyLang = r.language || effectiveLang;
            docChatHistory.push({ sender: 'AI', text: botReply });

            // ── STEP 4: Render response with correct language badge & inline TTS toggle
            const langBadgeColor = replyLang === 'Tamil' ? '#0b756b' : '#185abc';
            const langBadgeIcon = replyLang === 'Tamil' ? '🇮🇳' : '🌐';
            const listenLabel = replyLang === 'Tamil' ? 'வாசிக்கவும்' : 'Listen';
            typingEl.parentElement.innerHTML = `
                <div style="line-height:1.6">${esc(botReply).replaceAll('\n', '<br>')}</div>
                <div style="margin-top:8px;display:flex;align-items:center;gap:6px;flex-wrap:wrap">
                    <button class="secondary btn-inline-tts-play" style="padding:3px 8px;font-size:11px;margin:0"
                        onclick="speak('${esc(botReply.slice(0, 500)).replaceAll("'", "\\'")}', '${replyLang}')">🔊 ${listenLabel}</button>
                    <button class="secondary btn-inline-tts-pause" style="padding:3px 8px;font-size:11px;margin:0;display:${ttsActive?'inline-block':'none'}"
                        onclick="ttsPaused ? resumeTTS() : pauseTTS()">⏸ ${replyLang==='Tamil'?'இடைநிறுத்து':'Pause'}</button>
                    <button class="secondary btn-inline-tts-stop" style="padding:3px 8px;font-size:11px;margin:0;display:${(ttsActive||ttsPaused)?'inline-block':'none'}"
                        onclick="stopTTS()">⏹ ${replyLang==='Tamil'?'நிறுத்து':'Stop'}</button>
                    <span style="font-size:10px;padding:2px 8px;border-radius:10px;background:${langBadgeColor}15;color:${langBadgeColor};font-weight:700">
                        ${langBadgeIcon} ${esc(r.source || 'AI')} &bull; ${replyLang}
                    </span>
                </div>
            `;

            // ── STEP 5: Auto-speak in the correct language
            if(A.voiceAutoReply !== false){
                speak(botReply, replyLang);
            }
        }
    } catch(err){
        const typingEl = document.getElementById(typingId);
        if(typingEl){
            typingEl.parentElement.innerHTML = `⚠️ Error: ${esc(err.message)}`;
        }
    }
}

function speakText(txt, lang){
    speak(txt, lang || docChatLang);
}

function speakDocContext(){
    if(currentDocAnalysis?.analysis?.clinical_summary){
        speak(currentDocAnalysis.analysis.clinical_summary, docChatLang);
    } else {
        speak(docChatLang==='Tamil' ? 'முதலில் மருத்துவ அறிக்கையை பதிவேற்றவும்.' : 'Please upload or analyze a medical document first.', docChatLang);
    }
}

function toggleDocChatMic(){
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SpeechRecognition){
        alert('Web Speech Recognition is not supported by this browser.');
        return;
    }

    const btn = document.getElementById('doc-chat-mic');
    const input = document.getElementById('doc-chat-input');

    if(docChatMicActive){
        if(docChatRecognition) docChatRecognition.stop();
        docChatMicActive = false;
        if(btn){ btn.className = 'chat-mic-btn'; btn.title = 'Voice input'; }
        return;
    }

    // Recognition language follows docChatLang
    const recognitionLang = (docChatLang === 'Tamil') ? 'ta-IN' : 'en-IN';

    try {
        docChatRecognition = new SpeechRecognition();
        docChatRecognition.continuous = false;
        docChatRecognition.interimResults = true;
        docChatRecognition.lang = recognitionLang;
        docChatRecognition.maxAlternatives = 3;

        docChatRecognition.onstart = () => {
            docChatMicActive = true;
            if(btn){ btn.className = 'chat-mic-btn active'; btn.title = 'Stop recording'; }
            if(input){
                input.placeholder = docChatLang === 'Tamil'
                    ? 'கேட்கிறது... பேசுங்கள்...'
                    : 'Listening... Speak your question!';
            }
        };

        docChatRecognition.onresult = (e) => {
            let res = '';
            for(let i=0; i<e.results.length; i++){
                res += e.results[i][0].transcript;
            }
            if(input) input.value = res;
        };

        docChatRecognition.onerror = (e) => {
            docChatMicActive = false;
            if(btn){ btn.className = 'chat-mic-btn'; btn.title = 'Voice input'; }
            if(input) input.placeholder = docChatLang === 'Tamil'
                ? 'கேள்வி கேட்கவும் (அல்லது மைக் அழுத்தவும்)...'
                : 'Ask anything about this report...';
        };

        docChatRecognition.onend = () => {
            docChatMicActive = false;
            if(btn){ btn.className = 'chat-mic-btn'; btn.title = 'Voice input'; }
            if(input) input.placeholder = docChatLang === 'Tamil'
                ? 'கேள்வி கேட்கவும் (அல்லது மைக் அழுத்தவும்)...'
                : 'Ask anything about this report...';
            if(input && input.value.trim()){
                sendDocChatMessage();
            }
        };

        docChatRecognition.start();
    } catch(err){
        alert('Could not start microphone: ' + err.message);
    }
}

lang();
