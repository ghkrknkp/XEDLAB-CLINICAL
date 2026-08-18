from app.services.text_cleaner import clean_text


def test_text_cleaning_normalizes_whitespace():
    raw = "Hemoglobin    10.2   g/dL\r\n\r\n\r\nWBC   7200"
    cleaned = clean_text(raw)
    assert "\r" not in cleaned
    assert "   " not in cleaned
    assert "\n\n\n" not in cleaned


def test_text_cleaning_preserves_units():
    raw = "Glucose 128 mg/dL"
    cleaned = clean_text(raw)
    assert "mg/dL" in cleaned
