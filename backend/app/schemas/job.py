from typing import Optional
from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    report_id: str
    job_id: str
    status: str  # "queued" | "processing" | "completed" | "failed"
    stage: str  # "QUEUED" | "EXTRACTING" | "OCR_PROCESSING" | "CLEANING" | "CLASSIFYING" | "ENTITY_EXTRACTION" | "LAB_EXTRACTION" | "VALIDATION" | "SUMMARY" | "INDEXING" | "COMPLETED" | "FAILED"
    progress: int  # 0 to 100
    error_code: Optional[str] = None
    message: Optional[str] = None


class JobDetail(BaseModel):
    id: str
    report_id: str
    status: str
    stage: str
    progress: int
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True
