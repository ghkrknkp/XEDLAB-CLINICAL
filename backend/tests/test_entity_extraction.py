from app.services.entity_extractor import extract_entities


def test_entity_extraction_finds_age_sex_patient_id():
    pages = [{"page": 1, "text": "Patient ID: MRN-4471\nAge: 45\nSex: Female", "ocr_used": False}]
    entities = extract_entities(pages)
    types = {e.entity_type: e.entity_text for e in entities}
    assert types.get("AGE") == "45"
    assert types.get("SEX") == "F"
    assert types.get("PATIENT_ID") == "MRN-4471"


def test_entity_extraction_finds_conditions():
    pages = [{"page": 1, "text": "History of hypertension and diabetes.", "ocr_used": False}]
    entities = extract_entities(pages)
    condition_texts = {e.entity_text for e in entities if e.entity_type == "CONDITION"}
    assert "Hypertension" in condition_texts
    assert "Diabetes" in condition_texts
