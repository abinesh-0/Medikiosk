from datetime import datetime

from extensions import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    case_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "cases.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False
    )

    file_path = db.Column(
        db.Text,
        nullable=False
    )

    file_type = db.Column(
        db.String(100),
        nullable=False
    )

    file_size = db.Column(
        db.Integer,
        nullable=True
    )

    document_type = db.Column(
        db.Enum(
            "LAB_REPORT",
            "PRESCRIPTION",
            "DISCHARGE_SUMMARY",
            "IMAGING",
            "MEDICAL_RECORD",
            "OTHER"
        ),
        default="OTHER"
    )

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    upload_status = db.Column(
        db.Enum(
            "UPLOADED",
            "PROCESSING",
            "PROCESSED",
            "FAILED"
        ),
        default="UPLOADED"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    # Case <-> Documents
    case = db.relationship(
        "Case",
        back_populates="documents"
    )

    # User <-> Uploaded Documents
    uploader = db.relationship(
        "User",
        back_populates="uploaded_documents",
        foreign_keys=[uploaded_by]
    )

    # Document <-> Extraction
    extraction = db.relationship(
        "DocumentExtraction",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Document <-> Medical Timeline
    timeline_events = db.relationship(
        "MedicalTimeline",
        back_populates="source_document"
    )

    # Document <-> Investigations
    investigations = db.relationship("Investigation", back_populates="source_document")
    medications = db.relationship("Medication", foreign_keys="Medication.source_document_id", back_populates="source_document")

    # =========================================================
    # TO DICT
    # =========================================================

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "document_type": self.document_type,
            "uploaded_by": self.uploaded_by,
            "upload_status": self.upload_status,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            )
        }

    def __repr__(self):
        return f"<Document {self.original_filename}>"


class DocumentExtraction(db.Model):
    __tablename__ = "document_extractions"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "documents.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    extracted_text = db.Column(
        db.Text,
        nullable=True
    )

    extraction_json = db.Column(
        db.Text,
        nullable=True
    )

    ocr_confidence = db.Column(
        db.Numeric(5, 4),
        nullable=True
    )

    verification_required = db.Column(
        db.Boolean,
        default=False
    )

    processing_status = db.Column(
        db.Enum(
            "PENDING",
            "COMPLETED",
            "FAILED"
        ),
        default="PENDING"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================================================
    # RELATIONSHIPS
    # =========================================================

    document = db.relationship(
        "Document",
        back_populates="extraction"
    )

    # =========================================================
    # TO DICT
    # =========================================================

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "extracted_text": self.extracted_text,
            "extraction_json": self.extraction_json,
            "ocr_confidence": (
                float(self.ocr_confidence)
                if self.ocr_confidence is not None
                else None
            ),
            "verification_required": bool(
                self.verification_required
            ),
            "processing_status": self.processing_status,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            )
        }

    def __repr__(self):
        return f"<DocumentExtraction {self.id}>"