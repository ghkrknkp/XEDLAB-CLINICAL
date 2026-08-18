"""Report Q&A API endpoint utilizing grounded RAG vector search."""
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.report import Report, Page, LabResult, Embedding, Conversation, Message
from app.schemas.qa import AskRequest, AskResponse
from app.schemas.finding import SourceInfo
from app.core.security import rate_limiter
from app.services.rag_service import chunk_pages, retrieve
from app.services.llm_service import answer_grounded_qa_safe

router = APIRouter(prefix="/api/reports", tags=["qa"])


@router.post("/{report_id}/ask", response_model=AskResponse)
def ask_report_question(
    report_id: str,
    payload: AskRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Rate limiting on QA / LLM calls
    if not rate_limiter.is_allowed(f"qa_{current_user.id}", max_requests=25, window_seconds=60):
        raise HTTPException(status_code=429, detail="Q&A request limit exceeded. Please wait a moment.")

    # 2. Report Ownership Isolation
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report or report.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found.")

    if report.processing_status not in ("completed", "analyzed"):
        raise HTTPException(status_code=400, detail="Report processing is not completed yet.")

    # 3. Retrieve Page chunks for THIS report only
    pages = db.query(Page).filter(Page.report_id == report.id).order_by(Page.page_number).all()
    page_dicts = [{"page": p.page_number, "text": p.raw_text} for p in pages]
    chunks = chunk_pages(page_dicts)

    # 4. Perform vector similarity retrieval
    top_chunks = retrieve(payload.question, chunks, top_k=3)

    # 5. Load validated findings
    findings = db.query(LabResult).filter(LabResult.report_id == report.id).all()
    findings_dicts = [{
        "test_name": f.test_name,
        "value": f.value,
        "unit": f.unit,
        "reference_low": f.reference_low,
        "reference_high": f.reference_high,
        "original_reference_text": f.original_reference_text,
        "reference_text": f.reference_text,
        "status": f.status,
        "page_number": f.page_number,
    } for f in findings]

    # 6. Generate grounded answer
    answer_text, model_used = answer_grounded_qa_safe(
        question=payload.question,
        retrieved_chunks=top_chunks,
        validated_findings=findings_dicts,
        report_type=report.report_type,
    )

    # 7. Format source citations
    sources = [
        SourceInfo(page=c.get("page", 1), text=c.get("text", "")[:250])
        for c in top_chunks
    ]

    # 8. Persist conversation history
    conv = (
        db.query(Conversation)
        .filter(Conversation.report_id == report.id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        conv = Conversation(report_id=report.id, user_id=current_user.id)
        db.add(conv)
        db.flush()

    user_msg = Message(conversation_id=conv.id, role="user", content=payload.question)
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=answer_text,
        sources_json=json.dumps([s.model_dump() for s in sources]),
    )
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()

    return AskResponse(
        report_id=report.report_id,
        question=payload.question,
        answer=answer_text,
        retrieved_sources=sources,
        model_used=model_used,
    )
