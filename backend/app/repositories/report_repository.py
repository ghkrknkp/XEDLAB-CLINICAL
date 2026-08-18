"""Repository for Report database operations."""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.database.models import Report, Job, AuditEvent


class ReportRepository:

    @staticmethod
    def create_report(
        db: Session,
        user_id: str,
        report_id: str,
        filename: str,
        stored_path: str,
        storage_type: str = "local",
    ) -> Tuple[Report, Job]:
        report = Report(
            user_id=user_id,
            report_id=report_id,
            filename=filename,
            stored_path=stored_path,
            storage_type=storage_type,
            processing_status="queued",
        )
        db.add(report)
        db.flush()

        job = Job(
            report_id=report.id,
            status="queued",
            stage="QUEUED",
            progress=0,
        )
        db.add(job)

        audit = AuditEvent(
            user_id=user_id,
            report_id=report.id,
            action="UPLOAD",
            details="status=queued",
        )
        db.add(audit)

        db.commit()
        db.refresh(report)
        db.refresh(job)
        return report, job

    @staticmethod
    def get_by_report_id(db: Session, report_id: str, user_id: Optional[str] = None) -> Optional[Report]:
        query = db.query(Report).filter(Report.report_id == report_id)
        if user_id:
            query = query.filter(Report.user_id == user_id)
        return query.first()

    @staticmethod
    def list_user_reports(db: Session, user_id: str) -> List[Report]:
        return (
            db.query(Report)
            .filter(Report.user_id == user_id)
            .order_by(Report.created_at.desc())
            .all()
        )

    @staticmethod
    def delete_report(db: Session, report: Report):
        audit = AuditEvent(
            user_id=report.user_id,
            report_id=report.id,
            action="DELETE",
            details="status=deleted",
        )
        db.add(audit)
        db.delete(report)
        db.commit()
