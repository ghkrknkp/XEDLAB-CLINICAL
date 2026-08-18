from typing import Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    report_id: str
    job_id: str
    status: str = "queued"


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"


class ReadyResponse(BaseModel):
    status: str
    database: str
    redis: str
    storage: str


class SafeErrorResponse(BaseModel):
    error: dict
