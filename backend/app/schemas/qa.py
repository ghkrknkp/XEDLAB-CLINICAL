from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.finding import SourceInfo


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500, description="Question regarding the uploaded medical report")


class AskResponse(BaseModel):
    report_id: str
    question: str
    answer: str
    retrieved_sources: List[SourceInfo]
    model_used: str = "grounded-rag"
    disclaimer: str = (
        "AI Medical Report Analyzer provides informational, non-diagnostic explanations. "
        "It does not replace professional medical advice, diagnosis, or treatment."
    )


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: List[SourceInfo] = []
    created_at: str


class ConversationOut(BaseModel):
    id: str
    report_id: str
    messages: List[MessageOut] = []
    created_at: str
