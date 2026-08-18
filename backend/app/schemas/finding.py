from typing import List, Optional
from pydantic import BaseModel


class SourceInfo(BaseModel):
    page: int
    text: str


class LabFinding(BaseModel):
    test_name: str
    value: Optional[float]
    unit: Optional[str]
    reference_low: Optional[float]
    reference_high: Optional[float]
    original_reference_text: Optional[str] = None
    reference_text: Optional[str] = None
    status: str  # "within_reference_range" | "below_reference_range" | "above_reference_range" | "not_classified"
    confidence: float
    source: SourceInfo

    class Config:
        from_attributes = True


class EntityOut(BaseModel):
    entity_type: str
    entity_text: str
    page_number: int
    confidence: float

    class Config:
        from_attributes = True


class FindingsOut(BaseModel):
    report_id: str
    findings: List[LabFinding]
    entities: List[EntityOut] = []
    total_findings: int = 0
    within_range_count: int = 0
    outside_range_count: int = 0
    unclassified_count: int = 0
