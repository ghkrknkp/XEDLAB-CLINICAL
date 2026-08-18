import os
import uuid
import random
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.config import get_settings
from app.core.security import rate_limiter
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.response import UploadResponse
from app.repositories.report_repository import ReportRepository
from app.services.storage_service import get_storage_service
from app.workers.report_tasks import dispatch_report_processing

router = APIRouter(prefix="/api/reports", tags=["reports"])
settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf", "image/png", "image/jpeg", "image/pjpeg", "text/plain",
    "application/octet-stream",  # some browsers upload txt or pdf as octet-stream
}


def _generate_report_id() -> str:
    return f"REP-{random.randint(10000, 99999)}"


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_report(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Rate limiting on upload
    if not rate_limiter.is_allowed(f"upload_{current_user.id}", max_requests=30, window_seconds=60):
        raise HTTPException(status_code=429, detail="Upload limit exceeded. Please wait a moment.")

    # 2. Filename and Extension validation
    original_filename = file.filename or "uploaded_report"
    ext = os.path.splitext(original_filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. Allowed types: .pdf, .png, .jpg, .jpeg, .txt",
        )

    # 3. Read content & Size validation
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(contents) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.max_file_size_mb} MB.",
        )

    # 4. File integrity / Magic bytes check for PDFs and images
    if ext == ".pdf" and not contents.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Corrupted or invalid PDF file header.")
    if ext in (".png",) and not contents.startswith(b"\x89PNG"):
        raise HTTPException(status_code=400, detail="Corrupted or invalid PNG image.")
    if ext in (".jpg", ".jpeg") and not contents.startswith(b"\xff\xd8"):
        raise HTTPException(status_code=400, detail="Corrupted or invalid JPEG image.")

    # 5. Secure storage
    report_id = _generate_report_id()
    secure_filename = f"{report_id}{ext}"
    storage = get_storage_service()
    stored_path = storage.save_file(contents, secure_filename)

    # 6. Database record creation
    report, job = ReportRepository.create_report(
        db=db,
        user_id=current_user.id,
        report_id=report_id,
        filename=original_filename,
        stored_path=stored_path,
        storage_type=settings.storage_provider,
    )

    # 7. Asynchronous background dispatch
    dispatch_report_processing(report_id, job.id)

    # 8. Return immediately
    return UploadResponse(report_id=report_id, job_id=job.id, status="queued")
