from app.services.lab_parser import parse_lab_values

SAMPLE_TEXT = """Hemoglobin 10.2 g/dL 12.0 - 16.0
WBC 7200 /uL 4000-11000
Platelets 250000 /uL 150000-450000
Glucose 128 mg/dL 70-100"""


def test_lab_value_parser_extracts_all_rows():
    pages = [{"page": 1, "text": SAMPLE_TEXT, "ocr_used": False}]
    findings = parse_lab_values(pages)
    names = {f.test_name for f in findings}
    assert "Hemoglobin" in names
    assert "Glucose" in names
    assert len(findings) == 4


def test_reference_range_parser_extracts_bounds():
    pages = [{"page": 1, "text": "Glucose 128 mg/dL 70-100", "ocr_used": False}]
    findings = parse_lab_values(pages)
    glucose = findings[0]
    assert glucose.reference_low == 70
    assert glucose.reference_high == 100
    assert glucose.value == 128


def test_abnormal_value_detection_via_parser():
    pages = [{"page": 1, "text": SAMPLE_TEXT, "ocr_used": False}]
    findings = {f.test_name: f for f in parse_lab_values(pages)}
    assert findings["Hemoglobin"].status == "below_reference_range"
    assert findings["Glucose"].status == "above_reference_range"
    assert findings["Wbc"].status == "within_reference_range"
