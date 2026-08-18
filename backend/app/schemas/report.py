from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas.finding import LabFinding, EntityOut, SourceInfo


class ReportOut(BaseModel):
    report_id: str
    filename: str
    report_type: str
    report_type_confidence: float = 0.0
    processing_status: str
    page_count: int
    created_at: str
    job_id: Optional[str] = None

    class Config:
        from_attributes = True


class ReportSummaryOut(BaseModel):
    report_id: str
    filename: str
    report_type: str
    report_type_confidence: float
    processing_status: str
    page_count: int
    total_findings: int
    within_range: int
    below_range: int
    above_range: int
    unknown: int
    summary: Optional[str] = None
    summary_source: Optional[str] = None
    created_at: str
    disclaimer: str = (
        "AI Medical Report Analyzer is an informational document-analysis tool. "
        "It does not provide medical diagnosis or treatment advice. Laboratory "
        "reference ranges may vary by laboratory, method, age, sex, and other "
        "factors. Always consult a qualified healthcare professional for "
        "interpretation of medical results."
    )


class ReportPageOut(BaseModel):
    page: int
    text: str
    cleaned_text: Optional[str] = None
    ocr_used: bool


class TrendItem(BaseModel):
    report_id: str
    date: str
    value: Optional[float]
    unit: Optional[str]
    status: str


class ComparisonOut(BaseModel):
    report_id: str
    trends: Dict[str, List[TrendItem]]
