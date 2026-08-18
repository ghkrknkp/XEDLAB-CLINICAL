import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship

from app.database.database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=_utc_now)

    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="user", cascade="all, delete-orphan")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=_generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    report_id = Column(String, unique=True, index=True, nullable=False)  # e.g. REP-10291
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    storage_type = Column(String, default="local")  # "local" | "s3"
    report_type = Column(String, default="Unknown")
    report_type_confidence = Column(Float, default=0.0)
    processing_status = Column(String, default="queued")  # queued | processing | analyzed | completed | failed
    page_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utc_now, index=True)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)

    user = relationship("User", back_populates="reports")
    pages = relationship("Page", back_populates="report", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="report", cascade="all, delete-orphan")
    lab_results = relationship("LabResult", back_populates="report", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="report", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="report", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="report", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="report", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="report", cascade="all, delete-orphan")


class Page(Base):
    __tablename__ = "report_pages"

    id = Column(String, primary_key=True, default=_generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    raw_text = Column(Text, default="")
    cleaned_text = Column(Text, default="")
    ocr_used = Column(Boolean, default=False)

    report = relationship("Report", back_populates="pages")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(String, primary_key=True, default=_generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False, index=True)
    page_number = Column(Integer, default=1)
    entity_type = Column(String, nullable=False)  # AGE, SEX, PATIENT_ID, TEST, CONDITION, MEDICATION, etc.
    entity_text = Column(String, nullable=False)
    confidence = Column(Float, default=0.8)

    report = relationship("Report", back_populates="entities")


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(String, primary_key=True, default=_generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False, index=True)
    page_number = Column(Integer, default=1)
    test_name = Column(String, nullable=False)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    reference_low = Column(Float, nullable=True)
    reference_high = Column(Float, nullable=True)
    original_reference_text = Column(String, nullable=True)
    reference_text = Column(String, nullable=True)  # alias for backwards compatibility
    status = Column(String, default="not_classified")  # within_reference_range | below_reference_range | above_reference_range | not_classified
    confidence = Column(Float, default=0.5)
    source_text = Column(String, default="")

    report = relationship("Report", back_populates="lab_results")


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String, primary_key=True, default=_generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    model = Column(String, default="rule-based")
    summary_source = Column(String, default="deterministic_fallback")  # "openai" | "gemini" | "deterministic_fallback"
    created_at = Column(DateTime, default=_utc_now)

    report = relationship("Report", back_populates="summaries")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(String, primary_key=True, default=_generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # JSON-encoded float vector
    page_number = Column(Integer, default=1)
    section_name = Column(String, default="General")

    report = relationship("Report", back_populates="embeddings")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=_generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False, index=True)
    status = Column(String, default="queued")  # queued | processing | completed | failed
    stage = Column(String, default="QUEUED")  # QUEUED, EXTRACTING, OCR_PROCESSING, CLEANING, CLASSIFYING, ENTITY_EXTRACTION, LAB_EXTRACTION, VALIDATION, SUMMARY, INDEXING, COMPLETED, FAILED
    progress = Column(Integer, default=0)  # 0 to 100
    error_code = Column(String, nullable=True)
    safe_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utc_now, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    report = relationship("Report", back_populates="jobs")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=_generate_uuid)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=_utc_now)

    report = relationship("Report", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=_generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources_json = Column(Text, default="[]")  # JSON string of source citations
    created_at = Column(DateTime, default=_utc_now)

    conversation = relationship("Conversation", back_populates="messages")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, default=_generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=True, index=True)
    action = Column(String, nullable=False)  # "UPLOAD", "ANALYZE", "ASK_QA", "DELETE", "LOGIN"
    timestamp = Column(DateTime, default=_utc_now)
    details = Column(String, default="")  # Safe non-medical metadata e.g. "status=completed"

    user = relationship("User", back_populates="audit_events")
    report = relationship("Report", back_populates="audit_events")
