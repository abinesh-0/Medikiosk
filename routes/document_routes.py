from flask import Blueprint,jsonify,request,current_app
from flask_jwt_extended import jwt_required
from models.case_model import Case
from models.document_model import Document,DocumentExtraction
from models.timeline_model import MedicalTimeline
from services.security.access_control import current_user_id,roles_required
from services.ocr.ocr_engine import extract
from services.ocr.clinical_document_extractor import extract as clinical_extract
from utils.file_utils import save_upload
from utils.validators import allowed_extension
from extensions import db
from pathlib import Path
import json
document_bp=Blueprint("documents",__name__)

def own(case):
    return case.visit.patient.user_id==current_user_id()

@document_bp.post("/<int:case_id>/upload")
@jwt_required()
def upload(case_id):
    case=Case.query.get_or_404(case_id)
    if not own(case) and current_user_id() not in [getattr(case.visit.patient,"user_id",None)]:return jsonify(success=False,error="Access denied"),403
    f=request.files.get("file")
    if not f or not f.filename:return jsonify(success=False,error="File is required"),400
    if not allowed_extension(f.filename,current_app.config["ALLOWED_EXTENSIONS"]):return jsonify(success=False,error="Unsupported file type"),400
    original,stored,path,size=save_upload(f,Path(current_app.config["UPLOAD_FOLDER"])/"documents")
    if size>current_app.config["MAX_UPLOAD_BYTES"]:Path(path).unlink(missing_ok=True);return jsonify(success=False,error="File too large"),413
    doc=Document(case_id=case_id,original_filename=original,stored_filename=stored,file_path=path,file_type=f.mimetype or "application/octet-stream",file_size=size,document_type="OTHER",uploaded_by=current_user_id(),upload_status="PROCESSING")
    db.session.add(doc);db.session.flush()
    text,conf=extract(path); info=clinical_extract(text)
    if not info.get("is_medical_document"):
        Path(path).unlink(missing_ok=True)
        db.session.delete(doc); db.session.commit()
        return jsonify(success=False,error="This document could not be confirmed as a medical document. Please upload a prescription, lab report, scan/report or discharge summary."),400
    ex=DocumentExtraction(document_id=doc.id,extracted_text=text,extraction_json=json.dumps(info,ensure_ascii=False),ocr_confidence=conf,verification_required=conf<.8,processing_status="COMPLETED")
    db.session.add(ex)
    db.session.add(MedicalTimeline(patient_id=case.visit.patient_id,case_id=case_id,event_type="DOCUMENT",title=original,description=text[:1000],source_document_id=doc.id))
    low_name=original.lower(); low_text=(text or "").lower()
    if "discharge" in low_name or "discharge summary" in low_text:
        doc.document_type="DISCHARGE_SUMMARY"
    elif any(x in low_name for x in ["xray","x-ray","mri","ct","scan","ultrasound","imaging"]) or any(x in low_text for x in ["x-ray","mri","ct scan","ultrasound","imaging"]):
        doc.document_type="IMAGING"
    elif info.get("investigations"):
        doc.document_type="LAB_REPORT"
    elif info.get("medications"):
        doc.document_type="PRESCRIPTION"
    else:
        doc.document_type="MEDICAL_RECORD"
    # If a summary already exists, refresh it so every accepted document is included in the doctor handoff.
    if case.ai_summary:
        from models.answer_model import CaseAnswer
        from services.ai.summary_generator import generate
        import json as _json
        answers=[x.to_dict() for x in CaseAnswer.query.filter_by(case_id=case_id).order_by(CaseAnswer.sequence_number).all()]
        documents=[]
        for existing_doc in case.documents:
            item=existing_doc.to_dict()
            if getattr(existing_doc,'extraction',None):
                item['extraction']=existing_doc.extraction.to_dict()
            documents.append(item)
        assignment=None
        if case.doctor_assignments:
            a=[x for x in case.doctor_assignments if x.assignment_status in ["ASSIGNED","IN_PROGRESS"]][-1:]
            if a:
                aa=a[0];assignment={"doctor_name":aa.doctor.user.full_name,"doctor_email":aa.doctor.user.email,"department":aa.doctor.department.name}
    db.session.commit()
    return jsonify(success=True,document=doc.to_dict(),extraction=ex.to_dict(),clinical=info)


@document_bp.post("/<int:case_id>/medical-history")
@jwt_required()
def medical_history_upload(case_id):
    case = Case.query.get_or_404(case_id)
    if not own(case) and current_user_id() not in [getattr(case.visit.patient, "user_id", None)]:
        return jsonify(success=False, error="Access denied"), 403

    from services.ocr.clinical_document_extractor import extract_medical_history_summary
    from models.clinical_history_model import ClinicalHistory

    f = request.files.get("file")
    pasted_text = request.form.get("text", "").strip() or (request.get_json(silent=True) or {}).get("text", "").strip()

    text = ""
    conf = 1.0
    original = "Pasted_Medical_History.txt"
    doc = None
    stored_path = ""

    if f and f.filename:
        if not allowed_extension(f.filename, current_app.config["ALLOWED_EXTENSIONS"]):
            return jsonify(success=False, error="Unsupported file type"), 400
        original, stored, path, size = save_upload(f, Path(current_app.config["UPLOAD_FOLDER"]) / "documents")
        if size > current_app.config["MAX_UPLOAD_BYTES"]:
            Path(path).unlink(missing_ok=True)
            return jsonify(success=False, error="File too large"), 413
        stored_path = path
        doc = Document(
            case_id=case_id,
            original_filename=original,
            stored_filename=stored,
            file_path=path,
            file_type=f.mimetype or "application/octet-stream",
            file_size=size,
            document_type="MEDICAL_RECORD",
            uploaded_by=current_user_id(),
            upload_status="PROCESSING"
        )
        db.session.add(doc)
        db.session.flush()

        # Run OCR extraction
        text, conf = extract(path)
    elif pasted_text:
        text = pasted_text
        conf = 1.0
        doc = Document(
            case_id=case_id,
            original_filename="Pasted_Medical_History.txt",
            stored_filename="pasted_history.txt",
            file_path="",
            file_type="text/plain",
            file_size=len(pasted_text),
            document_type="MEDICAL_RECORD",
            uploaded_by=current_user_id(),
            upload_status="PROCESSED"
        )
        db.session.add(doc)
        db.session.flush()
    else:
        return jsonify(success=False, error="Please select a file or paste medical history text."), 400

    # Extract 9-point Medical History Summary
    history_res = extract_medical_history_summary(text, ocr_confidence=conf, original_filename=original)

    # Save Extraction Record
    ex = DocumentExtraction(
        document_id=doc.id,
        extracted_text=text,
        extraction_json=json.dumps(history_res, ensure_ascii=False),
        ocr_confidence=conf,
        verification_required=not history_res.get("is_reliable", True),
        processing_status="COMPLETED"
    )
    db.session.add(ex)

    # Add to Timeline
    db.session.add(MedicalTimeline(
        patient_id=case.visit.patient_id,
        case_id=case_id,
        event_type="DOCUMENT",
        title=f"Medical History: {original}",
        description=history_res.get("summary_text", "")[:1000],
        source_document_id=doc.id
    ))

    # Update Case Clinical History
    ch = ClinicalHistory.query.filter_by(case_id=case_id).first()
    if not ch:
        ch = ClinicalHistory(case_id=case_id)
        db.session.add(ch)
        db.session.flush()

    s_dict = history_res.get("structured", {})
    if s_dict.get("diagnoses") and s_dict["diagnoses"] != "Not available in uploaded document.":
        ch.past_medical_history = ((ch.past_medical_history or "") + "\n" + s_dict["diagnoses"]).strip()
    if s_dict.get("surgeries") and s_dict["surgeries"] != "Not available in uploaded document.":
        ch.past_surgical_history = ((ch.past_surgical_history or "") + "\n" + s_dict["surgeries"]).strip()
    if s_dict.get("medications") and s_dict["medications"] != "Not available in uploaded document.":
        ch.medication_history = ((ch.medication_history or "") + "\n" + s_dict["medications"]).strip()
    if s_dict.get("allergies") and s_dict["allergies"] != "Not available in uploaded document.":
        ch.allergy_history = ((ch.allergy_history or "") + "\n" + s_dict["allergies"]).strip()
    if s_dict.get("investigations") and s_dict["investigations"] != "Not available in uploaded document.":
        ch.investigation_history = ((ch.investigation_history or "") + "\n" + s_dict["investigations"]).strip()

    doc.upload_status = "PROCESSED"
    db.session.commit()

    return jsonify(
        success=True,
        document=doc.to_dict(),
        extraction=ex.to_dict(),
        history_summary=history_res.get("summary_text"),
        history_data=history_res
    )


@document_bp.get("/<int:case_id>")
@jwt_required()
def list_docs(case_id):
    c=Case.query.get_or_404(case_id)
    if not own(c) and current_user_id()!=c.visit.patient.user_id:return jsonify(success=False,error="Access denied"),403
    return jsonify(success=True,documents=[d.to_dict() for d in c.documents])

