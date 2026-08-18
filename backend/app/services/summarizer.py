"""Compatibility bridge forwarding to llm_service.py."""
from typing import List, Dict, Any
from app.services.llm_service import generate_grounded_summary_safe, LocalFallbackProvider


def generate_grounded_explanation(findings: List[Dict[str, Any]], report_type: str) -> str:
    summary_text, _ = generate_grounded_summary_safe(findings, report_type)
    return summary_text
