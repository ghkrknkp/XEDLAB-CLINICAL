import pytest
from app.services.classifier import classify_report


def test_classify_cbc():
    text = "Complete Blood Count. Hemoglobin 13.5 g/dL, Platelet count 250000, WBC 7000, Hematocrit 41%"
    label, confidence = classify_report(text)
    assert label == "CBC"
    assert confidence > 0.40


def test_classify_lipid():
    text = "Lipid Profile. Serum Cholesterol 220 mg/dL, HDL 45 mg/dL, LDL 130 mg/dL, Triglycerides 170 mg/dL"
    label, confidence = classify_report(text)
    assert label == "Lipid Profile"
    assert confidence > 0.40


def test_classify_liver():
    text = "Liver Function Test (LFT). Total Bilirubin 1.1 mg/dL, SGOT (AST) 35 U/L, SGPT (ALT) 42 U/L, ALP 90"
    label, confidence = classify_report(text)
    assert label == "Liver Function Test"
    assert confidence > 0.40


def test_classify_kidney():
    text = "Kidney Function Test (KFT). Serum Creatinine 1.2 mg/dL, Blood Urea 30 mg/dL, BUN 15, eGFR 85"
    label, confidence = classify_report(text)
    assert label == "Kidney Function Test"
    assert confidence > 0.40


def test_classify_thyroid():
    text = "Thyroid Function Test. Thyroid Stimulating Hormone (TSH) 3.2 mIU/L, Free T3 3.0, Free T4 1.1"
    label, confidence = classify_report(text)
    assert label == "Thyroid Test"
    assert confidence > 0.40
