import os
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.report import Report, Page, Entity, LabResult, Summary
from app.schemas.report import (
    ReportOut, ReportSummaryOut, ReportPageOut, ComparisonOut,
)
from app.schemas.finding import FindingsOut, LabFinding, EntityOut, SourceInfo
from app.schemas.response import MessageResponse
from app.repositories.report_repository import ReportRepository
from app.repositories.finding_repository import FindingRepository
from app.services.storage_service import get_storage_service

logger = logging.getLogger("medreports")
router = APIRouter(prefix="/api/reports", tags=["reports"])


def _get_owned_report(report_id: str, db: Session, current_user: User) -> Report:
    """Strict authorization checkpoint ensuring report ownership."""
    report = ReportRepository.get_by_report_id(db, report_id, user_id=current_user.id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@router.get("", response_model=List[ReportOut])
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = ReportRepository.list_user_reports(db, current_user.id)
    return [
        ReportOut(
            report_id=r.report_id,
            filename=r.filename,
            report_type=r.report_type,
            report_type_confidence=r.report_type_confidence,
            processing_status=r.processing_status,
            page_count=r.page_count,
            created_at=r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
        for r in reports
    ]


@router.get("/history", response_model=List[ReportOut])
def list_reports_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Alias for report history."""
    return list_reports(db, current_user)


@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = _get_owned_report(report_id, db, current_user)
    return ReportOut(
        report_id=report.report_id,
        filename=report.filename,
        report_type=report.report_type,
        report_type_confidence=report.report_type_confidence,
        processing_status=report.processing_status,
        page_count=report.page_count,
        created_at=report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    )


@router.get("/{report_id}/findings", response_model=FindingsOut)
def get_findings(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = _get_owned_report(report_id, db, current_user)
    results = FindingRepository.get_lab_results(db, report.id)
    entities = FindingRepository.get_entities(db, report.id)

    findings_out = []
    within_count = 0
    outside_count = 0
    unclass_count = 0

    for f in results:
        if f.status == "within_reference_range":
            within_count += 1
        elif f.status in ("below_reference_range", "above_reference_range"):
            outside_count += 1
        else:
            unclass_count += 1

        ref_text = f.original_reference_text or f.reference_text
        if not ref_text and f.reference_low is not None and f.reference_high is not None:
            ref_text = f"{f.reference_low} - {f.reference_high}"

        findings_out.append(LabFinding(
            test_name=f.test_name,
            value=f.value,
            unit=f.unit,
            reference_low=f.reference_low,
            reference_high=f.reference_high,
            original_reference_text=ref_text,
            reference_text=ref_text,
            status=f.status,
            confidence=f.confidence,
            source=SourceInfo(page=f.page_number, text=f.source_text),
        ))

    entities_out = [
        EntityOut(
            entity_type=e.entity_type,
            entity_text=e.entity_text,
            page_number=e.page_number,
            confidence=e.confidence,
        )
        for e in entities
    ]

    return FindingsOut(
        report_id=report.report_id,
        findings=findings_out,
        entities=entities_out,
        total_findings=len(findings_out),
        within_range_count=within_count,
        outside_range_count=outside_count,
        unclassified_count=unclass_count,
    )


@router.get("/{report_id}/summary", response_model=ReportSummaryOut)
def get_summary(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = _get_owned_report(report_id, db, current_user)
    summary_obj = (
        db.query(Summary)
        .filter(Summary.report_id == report.id)
        .order_by(Summary.created_at.desc())
        .first()
    )

    findings = FindingRepository.get_lab_results(db, report.id)
    counts = {
        "within_reference_range": 0,
        "below_reference_range": 0,
        "above_reference_range": 0,
        "not_classified": 0,
    }
    for f in findings:
        counts[f.status] = counts.get(f.status, 0) + 1

    return ReportSummaryOut(
        report_id=report.report_id,
        filename=report.filename,
        report_type=report.report_type,
        report_type_confidence=report.report_type_confidence,
        processing_status=report.processing_status,
        page_count=report.page_count,
        total_findings=len(findings),
        within_range=counts["within_reference_range"],
        below_range=counts["below_reference_range"],
        above_range=counts["above_reference_range"],
        unknown=counts.get("not_classified", 0) + counts.get("unknown", 0),
        summary=summary_obj.summary if summary_obj else "Summary generation pending.",
        summary_source=summary_obj.summary_source if summary_obj else "pending",
        created_at=report.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    )


@router.get("/{report_id}/pages", response_model=List[ReportPageOut])
def get_report_pages(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = _get_owned_report(report_id, db, current_user)
    pages = db.query(Page).filter(Page.report_id == report.id).order_by(Page.page_number).all()
    return [
        ReportPageOut(
            page=p.page_number,
            text=p.raw_text,
            cleaned_text=p.cleaned_text,
            ocr_used=p.ocr_used,
        )
        for p in pages
    ]


@router.get("/{report_id}/comparison", response_model=ComparisonOut)
def get_report_comparison(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = _get_owned_report(report_id, db, current_user)
    trends = FindingRepository.get_longitudinal_trends(db, current_user.id, report.report_id)
    return ComparisonOut(report_id=report.report_id, trends=trends)


@router.delete("/{report_id}", response_model=MessageResponse)
def delete_report(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Permanent report deletion (Requirement #48).

    Deletes:
    - Uploaded file from storage (Local / S3)
    - All DB records (Report, Pages, Entities, LabResults, Summaries, Embeddings, Jobs, Conversations)
    - Safe audit event logged
    """
    report = _get_owned_report(report_id, db, current_user)

    # 1. Delete file from storage
    storage = get_storage_service()
    storage.delete_file(report.stored_path)

    # 2. Delete database entity and cascades
    ReportRepository.delete_report(db, report)

    return MessageResponse(message="Report and all associated data permanently deleted.")
