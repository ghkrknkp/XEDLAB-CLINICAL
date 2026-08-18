"""Aggregate confidence scoring utilities.

Combines signals from OCR usage, parser certainty, unit detection, and
reference-range detection into a single explainable score per finding.
Never used to hide low-confidence extractions - callers should surface the
warning banner for anything below LOW_CONFIDENCE_THRESHOLD.
"""

LOW_CONFIDENCE_THRESHOLD = 0.6
LOW_CONFIDENCE_WARNING = "Please verify this extracted value against the original report."


def adjust_confidence_for_ocr(base_confidence: float, ocr_used: bool) -> float:
    """OCR introduces additional error risk (misread digits/decimals), so we
    apply a modest deterministic penalty when a value came from an OCR'd page."""
    if not ocr_used:
        return base_confidence
    penalized = base_confidence - 0.15
    return round(max(penalized, 0.05), 2)


def needs_verification_warning(confidence: float) -> bool:
    return confidence < LOW_CONFIDENCE_THRESHOLD
