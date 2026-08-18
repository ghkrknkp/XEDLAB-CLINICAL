"""Report type classification service.

Classification Categories:
1. CBC (Complete Blood Count)
2. Lipid Profile
3. Liver Function Test
4. Kidney Function Test
5. Thyroid Test
6. Urine Analysis
7. Radiology
8. Pathology
9. Discharge Summary
10. Clinical Note
11. Other

Supports:
- Trained TF-IDF + LogisticRegression model artifact (ml/models/classifier.joblib)
- Transparent keyword fallback with calibrated confidence if model artifact is absent
"""
import os
from typing import Tuple

LABELS = [
    "CBC", "Lipid Profile", "Liver Function Test", "Kidney Function Test",
    "Thyroid Test", "Urine Analysis", "Radiology", "Pathology",
    "Discharge Summary", "Clinical Note", "Other",
]

_KEYWORD_RULES = {
    "CBC": ["hemoglobin", "wbc", "rbc", "platelet", "hematocrit", "complete blood count", "mcv", "mch", "leukocyte", "neutrophils"],
    "Lipid Profile": ["cholesterol", "hdl", "ldl", "triglycerides", "lipid profile", "vldl"],
    "Liver Function Test": ["sgot", "sgpt", "alt", "ast", "bilirubin", "liver function", "alkaline phosphatase", "alp", "hepatic"],
    "Kidney Function Test": ["creatinine", "urea", "bun", "egfr", "kidney function", "renal profile", "uric acid"],
    "Thyroid Test": ["tsh", "t3", "t4", "thyroid", "free t3", "free t4", "thyrotropin"],
    "Urine Analysis": ["urine", "urinalysis", "specific gravity", "epithelial cells", "pus cells"],
    "Radiology": ["x-ray", "mri", "ct scan", "ultrasound", "radiograph", "chest pa", "echocardiogram", "sonography"],
    "Pathology": ["biopsy", "histopathology", "cytology", "fnac", "carcinoma", "malignancy", "benign"],
    "Discharge Summary": ["discharge summary", "admitted on", "discharged on", "hospital course", "admission diagnosis"],
    "Clinical Note": ["chief complaint", "history of present illness", "physical examination", "consultation note", "progress note"],
}

_model = None
_vectorizer = None


def _load_model():
    global _model, _vectorizer
    if _model is not None:
        return

    # Check probable locations for the model artifact
    candidate_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "classifier.joblib")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models", "classifier.joblib")),
        os.path.abspath("./ml/models/classifier.joblib"),
    ]

    for path in candidate_paths:
        if os.path.exists(path):
            try:
                import joblib
                artifact = joblib.load(path)
                _model = artifact.get("model")
                _vectorizer = artifact.get("vectorizer")
                return
            except Exception:
                pass

    _model = False  # Mark checked but not found


def _rule_based_classify(text: str) -> Tuple[str, float]:
    lower = text.lower()
    best_label, best_hits = "Other", 0

    for label, keywords in _KEYWORD_RULES.items():
        hits = sum(1 for kw in keywords if kw in lower)
        if hits > best_hits:
            best_label, best_hits = label, hits

    if best_hits == 0:
        return "Other", 0.30

    confidence = min(0.40 + best_hits * 0.08, 0.60)
    return best_label, round(confidence, 2)


def classify_report(full_text: str) -> Tuple[str, float]:
    """Returns (report_type, confidence)."""
    _load_model()
    if _model and _vectorizer:
        try:
            vec = _vectorizer.transform([full_text])
            proba = _model.predict_proba(vec)[0]
            idx = proba.argmax()
            label = _model.classes_[idx]
            return label, round(float(proba[idx]), 2)
        except Exception:
            pass

    return _rule_based_classify(full_text)
