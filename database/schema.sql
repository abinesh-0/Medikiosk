USE medikiosk;

-- =========================================================
-- 1. USERS
-- =========================================================

CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('PATIENT', 'DOCTOR', 'TRIAGE', 'ADMIN') NOT NULL DEFAULT 'PATIENT',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    last_login_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 2. PATIENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS patients (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NULL,
    abha_id VARCHAR(100) NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    date_of_birth DATE NULL,
    age INT NULL,
    gender ENUM('MALE', 'FEMALE', 'OTHER', 'PREFER_NOT_TO_SAY') NULL,
    phone VARCHAR(20) NULL,
    email VARCHAR(191) NULL,
    address TEXT NULL,
    preferred_language VARCHAR(50) DEFAULT 'English',
    emergency_contact_name VARCHAR(150) NULL,
    emergency_contact_phone VARCHAR(20) NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    CONSTRAINT fk_patient_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL,

    INDEX idx_patient_phone (phone),
    INDEX idx_patient_name (full_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 3. DEPARTMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS departments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 4. DOCTORS
-- =========================================================

CREATE TABLE IF NOT EXISTS doctors (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL UNIQUE,
    department_id BIGINT UNSIGNED NOT NULL,
    doctor_code VARCHAR(50) NOT NULL UNIQUE,
    specialization VARCHAR(150) NOT NULL,
    qualification VARCHAR(255) NULL,
    is_available TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    CONSTRAINT fk_doctor_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_doctor_department
        FOREIGN KEY (department_id)
        REFERENCES departments(id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 5. VISITS
-- =========================================================

CREATE TABLE IF NOT EXISTS visits (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT UNSIGNED NOT NULL,
    visit_number VARCHAR(50) NOT NULL UNIQUE,
    visit_date DATETIME NOT NULL,
    visit_type ENUM('OPD', 'FOLLOW_UP', 'EMERGENCY') DEFAULT 'OPD',
    status ENUM(
        'REGISTERED',
        'INTAKE',
        'TRIAGE',
        'QUEUED',
        'DOCTOR_REVIEW',
        'COMPLETED',
        'CANCELLED'
    ) DEFAULT 'REGISTERED',
    priority ENUM('LOW', 'NORMAL', 'HIGH', 'URGENT') DEFAULT 'NORMAL',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    CONSTRAINT fk_visit_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    INDEX idx_visit_date (visit_date),
    INDEX idx_visit_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 6. CASES
-- =========================================================

CREATE TABLE IF NOT EXISTS cases (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    visit_id BIGINT UNSIGNED NOT NULL UNIQUE,
    case_number VARCHAR(50) NOT NULL UNIQUE,
    intake_mode ENUM('NORMAL', 'AYUSH') NOT NULL DEFAULT 'NORMAL',
    language VARCHAR(50) DEFAULT 'English',
    chief_complaint TEXT NULL,
    recommended_department_id BIGINT UNSIGNED NULL,
    status ENUM(
        'DRAFT',
        'IN_PROGRESS',
        'READY_FOR_REVIEW',
        'ASSIGNED',
        'COMPLETED'
    ) DEFAULT 'DRAFT',
    priority ENUM('LOW', 'NORMAL', 'HIGH', 'URGENT') DEFAULT 'NORMAL',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    CONSTRAINT fk_case_visit
        FOREIGN KEY (visit_id)
        REFERENCES visits(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_case_department
        FOREIGN KEY (recommended_department_id)
        REFERENCES departments(id)
        ON DELETE SET NULL,

    INDEX idx_case_status (status),
    INDEX idx_case_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 7. CONVERSATION SESSIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS conversation_sessions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL,
    language VARCHAR(50) NOT NULL DEFAULT 'English',
    mode ENUM('VOICE', 'TOUCH', 'HYBRID') DEFAULT 'HYBRID',
    started_at DATETIME NOT NULL,
    ended_at DATETIME NULL,
    status ENUM('ACTIVE', 'COMPLETED', 'ABANDONED') DEFAULT 'ACTIVE',

    CONSTRAINT fk_conversation_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 8. CONVERSATION MESSAGES
-- =========================================================

CREATE TABLE IF NOT EXISTS conversation_messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id BIGINT UNSIGNED NOT NULL,
    sender ENUM('PATIENT', 'AI', 'SYSTEM') NOT NULL,
    message_text TEXT NOT NULL,
    input_type ENUM('VOICE', 'TEXT', 'TOUCH') DEFAULT 'TEXT',
    sequence_number INT NOT NULL,
    confidence_score DECIMAL(5,4) NULL,
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_message_session
        FOREIGN KEY (session_id)
        REFERENCES conversation_sessions(id)
        ON DELETE CASCADE,

    INDEX idx_message_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 9. CLINICAL HISTORY
-- =========================================================

CREATE TABLE IF NOT EXISTS clinical_history (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL UNIQUE,

    chief_complaint TEXT NULL,
    history_present_illness TEXT NULL,
    past_medical_history TEXT NULL,
    past_surgical_history TEXT NULL,
    medication_history TEXT NULL,
    allergy_history TEXT NULL,
    family_history TEXT NULL,
    personal_history TEXT NULL,
    social_history TEXT NULL,
    review_of_systems TEXT NULL,
    investigation_history TEXT NULL,

    smoking_status VARCHAR(100) NULL,
    alcohol_status VARCHAR(100) NULL,
    occupation VARCHAR(150) NULL,
    diet VARCHAR(150) NULL,
    sleep_pattern VARCHAR(150) NULL,

    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    CONSTRAINT fk_clinical_history_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 10. AYUSH HISTORY
-- =========================================================

CREATE TABLE IF NOT EXISTS ayush_history (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL UNIQUE,

    prakriti TEXT NULL,
    vikriti TEXT NULL,
    sara TEXT NULL,
    samhanana TEXT NULL,
    pramana TEXT NULL,
    satmya TEXT NULL,
    sattva TEXT NULL,
    ahara_shakti TEXT NULL,
    vyayama_shakti TEXT NULL,
    vaya TEXT NULL,

    ahara_vihara TEXT NULL,
    nidana TEXT NULL,
    samprapti TEXT NULL,
    agni TEXT NULL,
    koshtha TEXT NULL,

    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    CONSTRAINT fk_ayush_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 11. DOCUMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS documents (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    file_size BIGINT UNSIGNED NULL,

    document_type ENUM(
        'LAB_REPORT',
        'PRESCRIPTION',
        'DISCHARGE_SUMMARY',
        'IMAGING',
        'MEDICAL_RECORD',
        'OTHER'
    ) DEFAULT 'OTHER',

    uploaded_by BIGINT UNSIGNED NULL,

    upload_status ENUM(
        'UPLOADED',
        'PROCESSING',
        'PROCESSED',
        'FAILED'
    ) DEFAULT 'UPLOADED',

    created_at DATETIME NOT NULL,

    CONSTRAINT fk_document_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_document_user
        FOREIGN KEY (uploaded_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    INDEX idx_document_case (case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 12. MEDICATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS medications (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL,
    medication_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100) NULL,
    frequency VARCHAR(100) NULL,
    duration VARCHAR(100) NULL,
    route VARCHAR(100) NULL,
    source_document_id BIGINT UNSIGNED NULL,
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_medication_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    INDEX idx_medication_case (case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 13. ALLERGIES
-- =========================================================

CREATE TABLE IF NOT EXISTS allergies (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL,
    allergen VARCHAR(255) NOT NULL,
    reaction TEXT NULL,
    severity ENUM('MILD', 'MODERATE', 'SEVERE', 'UNKNOWN')
        DEFAULT 'UNKNOWN',
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_allergy_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    INDEX idx_allergy_case (case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 14. INVESTIGATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS investigations (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    test_date DATE NULL,
    result_value VARCHAR(255) NULL,
    unit VARCHAR(100) NULL,
    reference_range VARCHAR(255) NULL,
    abnormal_flag TINYINT(1) DEFAULT 0,
    source_document_id BIGINT UNSIGNED NULL,
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_investigation_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    INDEX idx_investigation_case (case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 15. DOCUMENT EXTRACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS document_extractions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    document_id BIGINT UNSIGNED NOT NULL,
    extracted_text LONGTEXT NULL,
    extraction_json LONGTEXT NULL,
    ocr_confidence DECIMAL(5,4) NULL,
    verification_required TINYINT(1) DEFAULT 0,

    processing_status ENUM(
        'PENDING',
        'COMPLETED',
        'FAILED'
    ) DEFAULT 'PENDING',

    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    CONSTRAINT fk_extraction_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 16. MEDICAL TIMELINE
-- =========================================================

CREATE TABLE IF NOT EXISTS medical_timeline (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT UNSIGNED NOT NULL,
    case_id BIGINT UNSIGNED NULL,
    event_date DATE NULL,
    event_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    source_document_id BIGINT UNSIGNED NULL,
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_timeline_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_timeline_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_timeline_document
        FOREIGN KEY (source_document_id)
        REFERENCES documents(id)
        ON DELETE SET NULL,

    INDEX idx_timeline_patient (patient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 17. AI SUMMARIES
-- =========================================================

CREATE TABLE IF NOT EXISTS ai_summaries (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL UNIQUE,
    summary_text LONGTEXT NOT NULL,
    summary_json LONGTEXT NULL,
    language VARCHAR(50) DEFAULT 'English',
    ai_confidence DECIMAL(5,4) NULL,

    doctor_status ENUM(
        'PENDING_REVIEW',
        'EDITED',
        'CONFIRMED',
        'REJECTED'
    ) DEFAULT 'PENDING_REVIEW',

    doctor_notes TEXT NULL,
    reviewed_by BIGINT UNSIGNED NULL,
    reviewed_at DATETIME NULL,

    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,

    CONSTRAINT fk_summary_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_summary_doctor
        FOREIGN KEY (reviewed_by)
        REFERENCES users(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 18. RED FLAGS
-- =========================================================

CREATE TABLE IF NOT EXISTS red_flags (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL,
    flag_code VARCHAR(100) NOT NULL,
    flag_title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT') NOT NULL,
    detected_by ENUM('RULE_ENGINE', 'AI', 'STAFF') NOT NULL,
    confidence_score DECIMAL(5,4) NULL,

    status ENUM(
        'ACTIVE',
        'ACKNOWLEDGED',
        'RESOLVED'
    ) DEFAULT 'ACTIVE',

    acknowledged_by BIGINT UNSIGNED NULL,
    acknowledged_at DATETIME NULL,
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_redflag_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_redflag_user
        FOREIGN KEY (acknowledged_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    INDEX idx_redflag_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 19. QUEUES
-- =========================================================

CREATE TABLE IF NOT EXISTS queues (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL,
    department_id BIGINT UNSIGNED NOT NULL,
    queue_number INT NOT NULL,

    priority ENUM(
        'LOW',
        'NORMAL',
        'HIGH',
        'URGENT'
    ) DEFAULT 'NORMAL',

    status ENUM(
        'WAITING',
        'CALLED',
        'IN_PROGRESS',
        'COMPLETED',
        'CANCELLED'
    ) DEFAULT 'WAITING',

    created_at DATETIME NOT NULL,
    called_at DATETIME NULL,
    completed_at DATETIME NULL,

    CONSTRAINT fk_queue_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_queue_department
        FOREIGN KEY (department_id)
        REFERENCES departments(id)
        ON DELETE RESTRICT,

    INDEX idx_queue_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 20. DOCTOR ASSIGNMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS doctor_assignments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    case_id BIGINT UNSIGNED NOT NULL,
    doctor_id BIGINT UNSIGNED NOT NULL,
    assigned_by BIGINT UNSIGNED NULL,

    assignment_status ENUM(
        'ASSIGNED',
        'IN_PROGRESS',
        'COMPLETED',
        'CANCELLED'
    ) DEFAULT 'ASSIGNED',

    assigned_at DATETIME NOT NULL,
    completed_at DATETIME NULL,

    CONSTRAINT fk_assignment_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_assignment_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES doctors(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_assignment_user
        FOREIGN KEY (assigned_by)
        REFERENCES users(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 21. CONSENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS consents (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT UNSIGNED NOT NULL,
    case_id BIGINT UNSIGNED NULL,

    consent_type ENUM(
        'DATA_COLLECTION',
        'AI_PROCESSING',
        'ABHA_SHARING',
        'HIS_SHARING',
        'DOCUMENT_PROCESSING'
    ) NOT NULL,

    consent_given TINYINT(1) NOT NULL DEFAULT 0,
    consent_text TEXT NOT NULL,
    given_at DATETIME NULL,
    revoked_at DATETIME NULL,
    ip_address VARCHAR(45) NULL,
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_consent_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_consent_case
        FOREIGN KEY (case_id)
        REFERENCES cases(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================================
-- 22. AUDIT LOGS
-- =========================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BIGINT UNSIGNED NULL,
    description TEXT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    created_at DATETIME NOT NULL,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



-- =========================================================
-- 23. OTP TOKENS
-- =========================================================
CREATE TABLE IF NOT EXISTS otp_tokens (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(191) NOT NULL,
    purpose ENUM('register','reset') NOT NULL,
    otp_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    attempts INT NOT NULL DEFAULT 0,
    consumed_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    INDEX idx_otp_email_purpose (email,purpose)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- MediKiosk v3 additions: persistent adaptive answers and doctor notifications
CREATE TABLE IF NOT EXISTS case_answers (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  case_id BIGINT UNSIGNED NOT NULL,
  question_key VARCHAR(120) NOT NULL,
  answer_text LONGTEXT NOT NULL,
  language VARCHAR(50) DEFAULT 'English',
  input_type ENUM('VOICE','TEXT','TOUCH') DEFAULT 'TEXT',
  sequence_number INT DEFAULT 1,
  created_at DATETIME NOT NULL,
  CONSTRAINT fk_case_answer_case FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
  INDEX idx_case_answers_case(case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE IF NOT EXISTS case_notifications (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  case_id BIGINT UNSIGNED NOT NULL,
  recipient_user_id BIGINT UNSIGNED NULL,
  channel ENUM('EMAIL','DASHBOARD') DEFAULT 'DASHBOARD',
  subject VARCHAR(255),
  message TEXT,
  status ENUM('QUEUED','SENT','FAILED') DEFAULT 'QUEUED',
  created_at DATETIME NOT NULL,
  CONSTRAINT fk_case_notification_case FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,
  CONSTRAINT fk_case_notification_user FOREIGN KEY(recipient_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;




