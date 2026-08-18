from app.services.confidence import adjust_confidence_for_ocr, needs_verification_warning


def test_confidence_score_ocr_penalty():
    assert adjust_confidence_for_ocr(0.9, ocr_used=False) == 0.9
    assert adjust_confidence_for_ocr(0.9, ocr_used=True) == 0.75


def test_confidence_score_floor():
    assert adjust_confidence_for_ocr(0.1, ocr_used=True) == 0.05


def test_needs_verification_warning_threshold():
    assert needs_verification_warning(0.4) is True
    assert needs_verification_warning(0.8) is False
