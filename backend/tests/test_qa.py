import pytest
from app.services.rag_service import chunk_pages, retrieve
from app.services.llm_service import answer_grounded_qa_safe


def test_isolated_chunking_and_retrieval():
    pages = [
        {
            "page": 1,
            "text": "Complete Blood Count. Patient ID P1001. Hemoglobin is 10.2 g/dL with reference range 12.0 to 16.0 g/dL.",
        },
        {
            "page": 2,
            "text": "Kidney Function. Serum Creatinine is 1.1 mg/dL. Blood Urea Nitrogen is 15 mg/dL.",
        },
    ]

    chunks = chunk_pages(pages)
    assert len(chunks) >= 2

    # Query for hemoglobin
    results = retrieve("What was the hemoglobin level?", chunks, top_k=1)
    assert len(results) == 1
    assert results[0]["page"] == 1
    assert "Hemoglobin" in results[0]["text"]


def test_grounded_qa_answers_abnormal_values():
    validated_findings = [
        {
            "test_name": "Hemoglobin",
            "value": 10.2,
            "unit": "g/dL",
            "reference_low": 12.0,
            "reference_high": 16.0,
            "status": "below_reference_range",
            "reference_text": "12.0-16.0",
        },
        {
            "test_name": "WBC",
            "value": 7200.0,
            "unit": "/uL",
            "reference_low": 4000.0,
            "reference_high": 11000.0,
            "status": "within_reference_range",
            "reference_text": "4000-11000",
        },
    ]

    answer, _ = answer_grounded_qa_safe(
        question="Which values are outside the reference range?",
        retrieved_chunks=[{"page": 1, "text": "Hemoglobin 10.2 g/dL (12-16)"}],
        validated_findings=validated_findings,
        report_type="CBC",
    )

    assert "Hemoglobin" in answer
    assert "below" in answer.lower() or "outside" in answer.lower()
    assert "WBC" not in answer or "normal" in answer.lower() or "within" in answer.lower()
