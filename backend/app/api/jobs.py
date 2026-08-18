"""Job status and background task tracking API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.report import Report
from app.models import Job
from app.schemas.job import JobStatusResponse

router = APIRouter(prefix="/api/reports", tags=["jobs"])


@router.get("/{report_id}/status", response_model=JobStatusResponse)
def get_report_job_status(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found.")

    job = db.query(Job).filter(Job.report_id == report.id).order_by(Job.created_at.desc()).first()
    if not job:
        # If no job is explicitly found, construct one from report processing status
        return JobStatusResponse(
            report_id=report.report_id,
            job_id="",
            status=report.processing_status,
            stage="COMPLETED" if report.processing_status == "completed" else "PROCESSING",
            progress=100 if report.processing_status == "completed" else 50,
        )

    return JobStatusResponse(
        report_id=report.report_id,
        job_id=job.id,
        status=job.status,
        stage=job.stage,
        progress=job.progress,
        error_code=job.error_code,
        message=job.safe_message,
    )
