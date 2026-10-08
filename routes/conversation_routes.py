from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models.case_model import Case
from models.conversation_model import ConversationSession, ConversationMessage
from models.clinical_history_model import ClinicalHistory
from models.ayush_model import AyushHistory
from models.answer_model import CaseAnswer
from models.red_flag_model import RedFlag
from models.department_model import Department
from models.queue_model import Queue, DoctorAssignment
from models.notification_model import CaseNotification
from models.user_model import User
from services.security.access_control import current_user_id
from services.ai.question_engine import next_question
from services.ai.interview_engine import analyze_turn, _candidate_questions
from services.ai.summary_generator import generate
from services.ai.fact_extractor import extract_facts, extract_from_ocr_document
from services.ai.clinical_memory import (
    empty_memory,
    merge_extraction,
    record_turn,
    set_patient_info,
    build_context,
    flatten_answers,
    get_fact,
    has_fact,
    register_symptom,
    set_fact,
    mark_asked,
    mark_answered,
)
from services.ai.department_router import route_with_llm, route_department
from services.ai.doctor_summary import generate_doctor_summary, generate_llm_summary
from services.triage.red_flag_engine import detect, highest
from services.routing.department_router import recommend
from services.routing.doctor_assignment import available_doctor
from extensions import db
import json
import re


def _resolve_department(hint, full_text):
    """Resolve a department from the LLM's full-symptom department_hint.

    The hint is produced by the LLM after analyzing the COMPLETE history
    (not just the first symptom), e.g. "Emergency Medicine / Pulmonology".
    We match it against the active departments. When the hint is absent
    or ambiguous, fall back to the keyword router over the full text.
    """
    names = [d.name for d in Department.query.filter_by(is_active=True).all()]
    name_lower = {n.lower(): n for n in names}

    tokens = re.split(r'[/,;|]', hint or '')
    lowered_depts = {d.lower(): d for d in names}

    # 1) exact token match against an active department name.
    # Prefer SPECIFIC departments (skip the generic "General Medicine"
    # unless it is the only match) so routing follows the full symptom
    # picture rather than a safe catch-all.
    exact = []
    for token in tokens:
        token = token.strip().lower()
        if token in lowered_depts:
            exact.append(lowered_depts[token])
    specific = [n for n in exact if n.lower() != 'general medicine']
    if specific:
        return specific[0]
    if exact:
        return exact[0]

    # 2) containment match for specific (non-generic) departments
    specific = [n for n in names if n.lower() != 'general medicine']
    for token in tokens:
        token = token.strip().lower()
        if not token:
            continue
        for n in specific:
            if n.lower() in token:
                return n

    # 3) keyword router over the complete history
    return recommend(full_text)[0]

conversation_bp = Blueprint('conversation', __name__)


def own(c):
    return c.visit.patient.user_id == current_user_id()


def answers(c):
    return {
        x.question_key: x.answer_text
        for x in CaseAnswer.query.filter_by(case_id=c.id)
        .order_by(CaseAnswer.sequence_number).all()
    }


def answer_rows(c):
    return [
        x.to_dict()
        for x in CaseAnswer.query.filter_by(case_id=c.id)
        .order_by(CaseAnswer.sequence_number).all()
    ]


def full_text(c):
    return ' '.join([c.chief_complaint or ''] + list(answers(c).values()))


def document_payload(c):
    out = []
    for d in c.documents:
        item = d.to_dict()
        if getattr(d, 'extraction', None):
            item['extraction'] = d.extraction.to_dict()
        out.append(item)
    return out


def build_clinical_memory(c):
    memory = empty_memory()

    if c.chief_complaint:
        memory["chief_complaint"] = [c.chief_complaint]

    patient = getattr(c, "patient", None) or (c.visit.patient if getattr(c, "visit", None) else None)
    if patient:
        set_patient_info(
            memory,
            name=getattr(patient, "full_name", ""),
            age=getattr(patient, "age", None),
            gender=getattr(patient, "gender", ""),
        )

    h = c.clinical_history
    if h:
        history_dict = h.to_dict() if hasattr(h, 'to_dict') else {}
        for key, value in history_dict.items():
            if value:
                memory[key] = value

    for ans in answers(c).items():
        key, text = ans
        if text:
            record_turn(memory, str(text))
            mark_asked(memory, key, key.replace("_", " "))
            mark_answered(memory, key, str(text))
            set_fact(memory, key, str(text))

    for doc in c.documents:
        ext = doc.extraction
        if ext and ext.extraction_json:
            try:
                doc_facts = json.loads(ext.extraction_json)
                if isinstance(doc_facts, dict):
                    ocr_result = extract_from_ocr_document(
                        doc_facts.get("clinical_summary", "") or "",
                        doc_facts.get("document_type", doc.document_type or "MEDICAL_RECORD"),
                    )
                    for of in ocr_result.get("ocr_facts", []):
                        memory.setdefault("ocr_facts", []).append(of)
            except Exception:
                pass

    for flag in c.red_flags:
        memory.setdefault("safety_flags", []).append({
            "flag_code": flag.flag_code,
            "flag_title": flag.flag_title,
            "severity": flag.severity,
        })

    return memory


def _merge_ai_facts(c, facts):
    if not isinstance(facts, dict):
        return

    # IMPORTANT: directly query existing history
    h = ClinicalHistory.query.filter_by(case_id=c.id).first()

    if not h:
        h = ClinicalHistory(case_id=c.id)
        db.session.add(h)
        db.session.flush()

    allowed = {
        'chief_complaint',
        'history_present_illness',
        'severity',
        'associated_symptoms',
        'past_medical_history',
        'past_surgical_history',
        'medication_history',
        'allergy_history',
        'family_history',
        'personal_history',
        'social_history',
        'review_of_systems'
    }

    for key, value in facts.items():
        value = str(value or '').strip()

        if key in allowed and value and hasattr(h, key):
            old = str(getattr(h, key) or '').strip()

            if not old:
                setattr(h, key, value)
            elif value.lower() not in old.lower():
                setattr(h, key, old + '\n' + value)

    if facts.get('chief_complaint') and not c.chief_complaint:
        c.chief_complaint = str(facts['chief_complaint']).strip()


def _notify_triage(c, flags):
    urgent = [f for f in flags if f.get('severity') in ('HIGH', 'URGENT')]
    if not urgent:
        return
    staff = User.query.filter_by(role='TRIAGE', is_active=True).all()
    if not staff:
        return
    titles = '; '.join(str(f.get('flag_title') or f.get('flag_code')) for f in urgent)
    message = (
        f'Immediate safety screening alert for case {c.case_number}. '
        f'Priority: {c.priority}. Signals: {titles}. '
        'Clinician/staff verification required.'
    )
    for u in staff:
        exists = CaseNotification.query.filter_by(
            case_id=c.id, recipient_user_id=u.id, subject='MediKiosk safety alert'
        ).first()
        if not exists:
            db.session.add(CaseNotification(
                case_id=c.id,
                recipient_user_id=u.id,
                channel='DASHBOARD',
                subject='MediKiosk safety alert',
                message=message,
                status='QUEUED'
            ))


@conversation_bp.post('/<int:case_id>/session')
@jwt_required()
def session(case_id):
    c = Case.query.get_or_404(case_id)
    if not own(c):
        return jsonify(success=False, error='Access denied'), 403
    s = ConversationSession(
        case_id=case_id,
        language=c.language or 'English',
        mode='HYBRID'
    )
    db.session.add(s)
    db.session.commit()
    initial = next_question(c.intake_mode, answers(c), c.language or 'English')
    return jsonify(success=True, session=s.to_dict(), next_question=initial)


@conversation_bp.post('/<int:case_id>/message')
@jwt_required()
def message(case_id):
    c = Case.query.get_or_404(case_id)
    if not own(c):
        return jsonify(success=False, error='Access denied'), 403

    d = request.get_json() or {}
    text = str(d.get('text', '')).strip()
    key = str(d.get('question_key', '')).strip()
    sid = d.get('session_id')
    if not text or not key:
        return jsonify(success=False, error='Question and answer are required'), 400

    s = ConversationSession.query.get(sid) if sid else None
    if not s or s.case_id != case_id:
        return jsonify(success=False, error='Valid session required'), 400

    existing = CaseAnswer.query.filter_by(case_id=case_id, question_key=key).first()
    if existing:
        # Update instead of creating duplicate answers when the same UI request is retried.
        existing.answer_text = text
        existing.input_type = d.get('input_type') if d.get('input_type') in ['VOICE', 'TEXT', 'TOUCH'] else 'TEXT'
    else:
        seq = CaseAnswer.query.filter_by(case_id=case_id).count() + 1
        input_type = d.get('input_type') if d.get('input_type') in ['VOICE', 'TEXT', 'TOUCH'] else 'TEXT'
        db.session.add(CaseAnswer(
            case_id=case_id,
            question_key=key,
            answer_text=text,
            language=c.language,
            input_type=input_type,
            sequence_number=seq
        ))
        db.session.add(ConversationMessage(
            session_id=s.id,
            sender='PATIENT',
            message_text=text,
            input_type=input_type,
            sequence_number=seq
        ))

    h = ClinicalHistory.query.filter_by(case_id=case_id).first()

    if not h:
        h = ClinicalHistory(case_id=case_id)
        db.session.add(h)
        db.session.flush()
    if hasattr(h, key):
        setattr(h, key, text)
    elif key != 'chief_complaint':
        h.history_present_illness = (
            (h.history_present_illness or '') + '\n' +
            key.replace('_', ' ').title() + ': ' + text
        ).strip()
    if key == 'chief_complaint':
        c.chief_complaint = text

    if c.intake_mode == 'AYUSH':
        ah = AyushHistory.query.filter_by(case_id=case_id).first()

        if not ah:
            ah = AyushHistory(case_id=case_id)
            db.session.add(ah)
            db.session.flush()
        amap = {
            'ayush_agni_change': 'agni',
            'ayush_koshtha_change': 'koshtha',
            'ayush_ahara_trigger': 'nidana',
            'ayush_nidana_trigger': 'nidana',
            'ayush_vikriti_change': 'vikriti'
        }
        if hasattr(ah, key):
            setattr(ah, key, text)
        elif key in amap:
            attr = amap[key]
            setattr(ah, attr, ((getattr(ah, attr) or '') + '\n' + text).strip())

    # ---- ClinicalMemory: build from case state ----
    memory = build_clinical_memory(c)

    # ---- Fact extraction from patient text ----
    extracted = extract_facts(
        patient_text=text,
        previous_context=build_context(memory),
        language=c.language or "English",
    )
    merge_extraction(memory, extracted, source="patient")
    record_turn(memory, text)

    # ---- Safety screen (deterministic + AI) ----
    all_answers = answers(c)
    full = full_text(c)

    rule_flags = detect(full)
    for f in rule_flags:
        if not any(
            x.flag_code == f['flag_code'] and x.status == 'ACTIVE'
            for x in c.red_flags
        ):
            db.session.add(RedFlag(
                case_id=case_id,
                flag_code=f['flag_code'],
                flag_title=f['flag_title'],
                description=f['description'],
                severity=f['severity'],
                detected_by=f['detected_by'],
                confidence_score=f['confidence_score']
            ))

    if rule_flags:
        c.priority = highest(rule_flags)
        c.visit.priority = c.priority
        if c.priority in ['HIGH', 'URGENT']:
            c.visit.status = 'TRIAGE'
            _notify_triage(c, rule_flags)

    # ---- Build candidates and analyze turn with ClinicalMemory ----
    candidates = _candidate_questions(c.intake_mode, all_answers, c.language or 'English')
    ai = analyze_turn(
        c.intake_mode,
        c.language or 'English',
        all_answers,
        candidates,
        len(all_answers),
        clinical_memory=memory,
    )
    _merge_ai_facts(c, ai.get('facts', {}))

    # ---- Merge fact-extracted symptoms into memory ----
    for sym in extracted.get("symptoms", []):
        if isinstance(sym, dict) and sym.get("name"):
            register_symptom(
                memory,
                sym["name"],
                present=sym.get("present", True),
                location=sym.get("location"),
                duration=sym.get("duration"),
                onset=sym.get("onset"),
                severity=sym.get("severity"),
                confidence=0.9,
                source="patient",
            )

    # ---- Department routing: rule engine fast route during intermediate turns ----
    rule_result = route_department(memory, flatten_answers(memory))
    dep = rule_result.get("department") or "General Medicine"

    c.recommended_department = Department.query.filter_by(
        name=dep, is_active=True
    ).first()

    # ---- AI safety output ----
    ai_flags = []
    for f in ai.get('safety_flags', []):
        if not isinstance(f, dict):
            continue
        code = f.get('flag_code')
        if not code:
            continue
        if not any(x.flag_code == code and x.status == 'ACTIVE' for x in c.red_flags):
            evidence = f.get('evidence') or []
            if isinstance(evidence, str):
                evidence = [evidence]
            elif not isinstance(evidence, list):
                evidence = [str(evidence)]
            severity = f.get('severity')
            if severity not in ('HIGH', 'URGENT', 'MEDIUM', 'LOW'):
                severity = 'HIGH'
            item = {
                'flag_code': code,
                'flag_title': f.get('flag_title') or 'Potential safety signal',
                'description': f.get('description') or ('AI screening evidence: ' + ', '.join(evidence)),
                'severity': severity,
                'detected_by': f.get('detected_by') or 'AI',
                'confidence_score': f.get('confidence_score', .80),
            }
            db.session.add(RedFlag(case_id=case_id, **item))
            ai_flags.append(item)

    if ai_flags:
        c.priority = highest(rule_flags + ai_flags)
        c.visit.priority = c.priority
        if c.priority in ['HIGH', 'URGENT']:
            c.visit.status = 'TRIAGE'
            _notify_triage(c, ai_flags)

    db.session.commit()

    persisted_flags = [f.to_dict() for f in c.red_flags if f.status == 'ACTIVE']
    next_q = ai.get('next_question')
    if next_q is None and not ai.get('done'):
        next_q = next_question(
            c.intake_mode, all_answers, c.language or 'English',
        )

    return jsonify(
        success=True,
        next_question=next_q,
        flags=persisted_flags,
        priority=c.priority,
        department=dep,
        known_answers=len(all_answers),
        ai_source=ai.get('ai_source')
    )


@conversation_bp.post('/<int:case_id>/complete')
@jwt_required()
def complete(case_id):
    c = Case.query.get_or_404(case_id)
    if not own(c):
        return jsonify(success=False, error='Access denied'), 403

    a = answer_rows(c)
    docs = document_payload(c)
    flags = [f.to_dict() for f in c.red_flags]
    dep = c.recommended_department or Department.query.filter_by(code='GENMED').first()
    assignment = None

    if c.priority not in ['HIGH', 'URGENT'] and dep:
        existing_assignment = next(
            (x for x in c.doctor_assignments if x.assignment_status in ['ASSIGNED', 'IN_PROGRESS']),
            None
        )
        doc = existing_assignment.doctor if existing_assignment else available_doctor(dep.id)

        if not doc:
            gen = Department.query.filter_by(code='GENMED').first()
            fallback = available_doctor(gen.id) if gen else None
            if fallback:
                dep = gen
                c.recommended_department = gen
                doc = fallback

        if doc:
            if existing_assignment:
                da = existing_assignment
            else:
                da = DoctorAssignment(
                    case_id=case_id,
                    doctor_id=doc.id,
                    assignment_status='ASSIGNED'
                )
                db.session.add(da)
                db.session.flush()
                db.session.add(CaseNotification(
                    case_id=case_id,
                    recipient_user_id=doc.user.id,
                    channel='EMAIL',
                    subject='MediKiosk case assigned',
                    message=f'Case {c.case_number} is ready in your doctor dashboard.',
                    status='QUEUED'
                ))
            c.status = 'ASSIGNED'
            assignment = {
                'doctor_id': doc.id,
                'doctor_name': doc.user.full_name,
                'doctor_email': doc.user.email,
                'department': dep.name,
                'assignment_status': da.assignment_status
            }

        if not Queue.query.filter_by(case_id=case_id).first():
            qnum = (
                db.session.query(db.func.max(Queue.queue_number))
                .filter_by(department_id=dep.id).scalar() or 0
            ) + 1
            db.session.add(Queue(
                case_id=case_id,
                department_id=dep.id,
                queue_number=qnum,
                priority=c.priority,
                status='WAITING'
            ))
        c.visit.status = 'QUEUED'
    else:
        c.status = 'READY_FOR_REVIEW'
        c.visit.status = 'TRIAGE'

    summary_text, structured = generate(
        c,
        c.clinical_history.to_dict() if c.clinical_history else {},
        c.ayush_history.to_dict() if c.ayush_history else {},
        a,
        docs,
        flags,
        assignment,
        c.language
    )

    # ---- Enhanced structured doctor summary ----
    try:
        memory = build_clinical_memory(c)
        doctor_summary = generate_doctor_summary(memory)
        structured["doctor_summary"] = doctor_summary
        structured["department_routing"] = route_department(memory, flatten_answers(memory))
    except Exception:
        pass

    if c.ai_summary:
        s = c.ai_summary
        s.summary_text = summary_text
        s.summary_json = json.dumps(structured, ensure_ascii=False)
        s.language = c.language
        s.ai_confidence = .86
    else:
        db.session.add(__import__('models').AISummary(
            case_id=case_id,
            summary_text=summary_text,
            summary_json=json.dumps(structured, ensure_ascii=False),
            language=c.language,
            ai_confidence=.86
        ))
    db.session.commit()

    qentry = Queue.query.filter_by(case_id=case_id).first()
    return jsonify(
        success=True,
        case=c.to_dict(),
        summary=summary_text,
        structured=structured,
        assignment=assignment,
        department=dep.name if dep else 'General Medicine',
        priority=c.priority,
        queue=qentry.to_dict() if qentry else None,
        queue_number=qentry.queue_number if qentry else None
    )
