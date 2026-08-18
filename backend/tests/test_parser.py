import pytest
from app.services.lab_parser import parse_lab_values
from app.services.entity_extractor import extract_entities
from app.services.text_cleaner import clean_text


def test_parse_sample_cbc_report():
    """Validates extraction on sample CBC report as specified in Requirement #52."""
    sample_text = """
    Patient ID: P1001
    Age: 22
    Date: 2026-08-17

    Complete Blood Count

    Hemoglobin 10.2 g/dL 12.0 - 16.0
    WBC 7200 /uL 4000 - 11000
    Platelets 250000 /uL 150000 - 450000
    Hematocrit 39 % 36 - 46
    """
    pages = [{"page": 1, "text": clean_text(sample_text), "ocr_used": False}]
    findings = parse_lab_values(pages)

    assert len(findings) == 4
    by_name = {f.test_name.lower(): f for f in findings}

    # Hemoglobin: 10.2 g/dL (12-16) -> below_reference_range
    hb = by_name["hemoglobin"]
    assert hb.value == 10.2
    assert hb.unit == "g/dL"
    assert hb.reference_low == 12.0
    assert hb.reference_high == 16.0
    assert hb.status == "below_reference_range"
    assert hb.confidence >= 0.85

    # WBC: 7200 /uL (4000-11000) -> within_reference_range
    wbc = by_name["wbc"]
    assert wbc.value == 7200.0
    assert wbc.status == "within_reference_range"

    # Platelets: 250000 /uL (150000-450000) -> within_reference_range
    plt = by_name["platelets"]
    assert plt.value == 250000.0
    assert plt.status == "within_reference_range"

    # Hematocrit: 39 % (36-46) -> within_reference_range
    hct = by_name["hematocrit"]
    assert hct.value == 39.0
    assert hct.unit == "%"
    assert hct.status == "within_reference_range"


def test_parse_lipid_profile():
    sample_text = """
    Total Cholesterol: 235 mg/dL (125-200)
    HDL Cholesterol: 42 mg/dL (40-60)
    LDL Cholesterol: 155 mg/dL (0-100)
    Triglycerides: 190 mg/dL (35-150)
    """
    pages = [{"page": 1, "text": sample_text, "ocr_used": False}]
    findings = parse_lab_values(pages)

    assert len(findings) == 4
    by_name = {f.test_name.lower(): f for f in findings}

    assert by_name["total cholesterol"].status == "above_reference_range"
    assert by_name["hdl cholesterol"].status == "within_reference_range"
    assert by_name["ldl cholesterol"].status == "above_reference_range"
    assert by_name["triglycerides"].status == "above_reference_range"


def test_parse_entities():
    sample_text = """
    Patient ID: P1001
    Age: 22 years
    Sex: Female
    Date: 2026-08-17
    Clinical Note: Patient has type 2 diabetes and hypertension. Prescribed Metformin.
    """
    pages = [{"page": 1, "text": sample_text}]
    entities = extract_entities(pages)

    types = {e.entity_type: e.entity_text for e in entities}
    assert types.get("PATIENT_ID") == "P1001"
    assert types.get("SEX") == "Female"
    assert "Diabetes" in [e.entity_text for e in entities if e.entity_type == "CONDITION"]
    assert "Metformin" in [e.entity_text for e in entities if e.entity_type == "MEDICATION"]
