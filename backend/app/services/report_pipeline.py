"""End-to-end Medical Report Processing Pipeline.

Executes all extraction, OCR, cleaning, classification, entity parsing,
deterministic lab validation, grounded summary generation, and vector indexing stages.

Updates Job stage & progress in real-time.
"""
import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import Report, Page, Entity, LabResult, Summary, Embedding, Job
from app.core.logging import log_event
from app.services.storage_service import get_storage_service
from app.services.pdf_extractor import extract_pdf_pages
from app.services.ocr_service import extract_image_pages, extract_txt_pages
from app.services.text_cleaner import clean_pages
from app.services.classifier import classify_report
from app.services.entity_extractor import extract_entities
from app.services.lab_parser import parse_lab_values
from app.services.confidence import adjust_confidence_for_ocr
from app.services.llm_service import generate_grounded_summary_safe
from app.services.rag_service import chunk_pages, embed_texts


def _update_job_stage(db: Session, job: Job, stage: str, progress: int, status: str = "processing"):
    job.stage = stage
    job.progress = progress
    job.status = status
    if stage == "EXTRACTING" and not job.started_at:
        job.started_at = datetime.now(timezone.utc)
    if stage in ("COMPLETED", "FAILED"):
        job.completed_at = datetime.now(timezone.utc)
    db.commit()
    log_event(
        event="job_stage_update",
        report_id=job.report_id,
        job_id=job.id,
        stage=stage,
        status=status,
    )


def process_report_pipeline(report_id: str, job_id: str):
    """Main pipeline execution function run by the background worker."""
    db: Session = SessionLocal()
    start_time = time.time()

    report = db.query(Report).filter(Report.report_id == report_id).first()
    job = db.query(Job).filter(Job.id == job_id).first()

    if not report or not job:
        db.close()
        return

    try:
        report.processing_status = "processing"
        db.commit()

        # ----------------------------------------------------
        # Stage 1: EXTRACTING
        # ----------------------------------------------------
        _update_job_stage(db, job, "EXTRACTING", 15)

        storage = get_storage_service()
        file_bytes = storage.read_file(report.stored_path)
        ext = os.path.splitext(report.filename)[1].lower()

        # ----------------------------------------------------
        # Stage 2: OCR_PROCESSING (if scanned / image)
        # ----------------------------------------------------
        _update_job_stage(db, job, "OCR_PROCESSING", 30)

        if ext == ".pdf":
            raw_pages = extract_pdf_pages(file_bytes)
        elif ext in (".png", ".jpg", ".jpeg"):
            raw_pages = extract_image_pages(file_bytes)
        elif ext == ".txt":
            raw_pages = extract_txt_pages(file_bytes)
        else:
            raise ValueError(f"Unsupported document extension: {ext}")

        # ----------------------------------------------------
        # Stage 3: CLEANING
        # ----------------------------------------------------
        _update_job_stage(db, job, "CLEANING", 45)
        cleaned_pages = clean_pages(raw_pages)
        full_text = "\n\n".join(p["text"] for p in cleaned_pages)

        # Persist Pages
        db.query(Page).filter(Page.report_id == report.id).delete()
        for p in cleaned_pages:
            db.add(Page(
                report_id=report.id,
                page_number=p["page"],
                raw_text=p["text"],
                cleaned_text=p["text"],
                ocr_used=p.get("ocr_used", False),
            ))
        report.page_count = len(cleaned_pages)
        db.commit()

        # ----------------------------------------------------
        # Stage 4: CLASSIFYING
        # ----------------------------------------------------
        _update_job_stage(db, job, "CLASSIFYING", 55)
        report_type, type_confidence = classify_report(full_text)
        report.report_type = report_type
        report.report_type_confidence = type_confidence
        db.commit()

        # ----------------------------------------------------
        # Stage 5: ENTITY_EXTRACTION
        # ----------------------------------------------------
        _update_job_stage(db, job, "ENTITY_EXTRACTION", 65)
        entities = extract_entities(cleaned_pages)
        db.query(Entity).filter(Entity.report_id == report.id).delete()
        for e in entities:
            db.add(Entity(
                report_id=report.id,
                page_number=e.page_number,
                entity_type=e.entity_type,
                entity_text=e.entity_text,
                confidence=e.confidence,
            ))
        db.commit()

        # ----------------------------------------------------
        # Stage 6: LAB_EXTRACTION & VALIDATION
        # ----------------------------------------------------
        _update_job_stage(db, job, "LAB_EXTRACTION", 75)
        parsed_labs = parse_lab_values(cleaned_pages)

        _update_job_stage(db, job, "VALIDATION", 85)
        ocr_by_page = {p["page"]: p.get("ocr_used", False) for p in cleaned_pages}

        db.query(LabResult).filter(LabResult.report_id == report.id).delete()
        for lf in parsed_labs:
            adj_conf = adjust_confidence_for_ocr(lf.confidence, ocr_by_page.get(lf.page_number, False))
            db.add(LabResult(
                report_id=report.id,
                page_number=lf.page_number,
                test_name=lf.test_name,
                value=lf.value,
                unit=lf.unit,
                reference_low=lf.reference_low,
                reference_high=lf.reference_high,
                original_reference_text=lf.original_reference_text,
                reference_text=lf.reference_text,
                status=lf.status,
                confidence=adj_conf,
                source_text=lf.source_text,
            ))
        db.commit()

        # ----------------------------------------------------
        # Stage 7: SUMMARY (Grounded LLM explanation / Fallback)
        # ----------------------------------------------------
        _update_job_stage(db, job, "SUMMARY", 92)
        all_findings = db.query(LabResult).filter(LabResult.report_id == report.id).all()
        findings_payload = [{
            "test_name": f.test_name,
            "value": f.value,
            "unit": f.unit,
            "reference_low": f.reference_low,
            "reference_high": f.reference_high,
            "original_reference_text": f.original_reference_text,
            "reference_text": f.reference_text,
            "status": f.status,
            "page_number": f.page_number,
        } for f in all_findings]

        summary_text, summary_src = generate_grounded_summary_safe(findings_payload, report.report_type)

        db.query(Summary).filter(Summary.report_id == report.id).delete()
        db.add(Summary(
            report_id=report.id,
            summary=summary_text,
            model=summary_src,
            summary_source=summary_src,
        ))
        db.commit()

        # ----------------------------------------------------
        # Stage 8: INDEXING (RAG Vector Index)
        # ----------------------------------------------------
        _update_job_stage(db, job, "INDEXING", 98)
        chunks = chunk_pages(cleaned_pages)
        if chunks:
            chunk_texts = [c["text"] for c in chunks]
            vectors = embed_texts(chunk_texts)
            db.query(Embedding).filter(Embedding.report_id == report.id).delete()
            for c, vec in zip(chunks, vectors):
                db.add(Embedding(
                    report_id=report.id,
                    chunk_text=c["text"],
                    embedding=json.dumps(vec.tolist()),
                    page_number=c["page"],
                    section_name=c.get("section", "General"),
                ))
            db.commit()

        # ----------------------------------------------------
        # Stage 9: COMPLETED
        # ----------------------------------------------------
        report.processing_status = "completed"
        db.commit()
        _update_job_stage(db, job, "COMPLETED", 100, status="completed")

        elapsed = (time.time() - start_time) * 1000
        log_event("pipeline_completed", report_id=report_id, job_id=job_id, duration_ms=elapsed, status="completed")

    except Exception as exc:
        report.processing_status = "failed"
        job.error_code = "PROCESSING_ERROR"
        job.safe_message = "The document could not be processed completely. Please verify file format and quality."
        _update_job_stage(db, job, "FAILED", job.progress, status="failed")
        db.commit()
        log_event(
            "pipeline_failed",
            report_id=report_id,
            job_id=job_id,
            error_code="PROCESSING_ERROR",
            status="failed",
            level=30,
        )

    finally:
        db.close()
