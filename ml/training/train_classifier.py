"""ML Training Script for Medical Report Classifier.

Trains a TF-IDF + Logistic Regression classifier on 11 medical report categories:
1. CBC
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

Saves trained model artifact to ml/models/classifier.joblib.
"""
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

DATASET = [
    # CBC
    ("Complete Blood Count Hemoglobin 14.2 g/dL Hematocrit 42% WBC 6500 /uL Platelets 250000 /uL RBC 4.8 MCV 88", "CBC"),
    ("CBC with Differential: Hb 11.5 g/dL, Total Leukocyte Count 8200, Neutrophils 65%, Lymphocytes 28%, Platelet Count 180000", "CBC"),
    ("Hemogram blood report: Hemoglobin 10.2 g/dL (12-16), WBC 7200 /uL, Platelets 220000", "CBC"),
    ("Automated Hematology Analyzer CBC report: Red Blood Cells 4.5 M/uL, Hgb 13.0 g/dL, Hct 40%, RDW 12.5%", "CBC"),

    # Lipid Profile
    ("Lipid Panel Fasting: Total Cholesterol 220 mg/dL, HDL 45 mg/dL, LDL 140 mg/dL, Triglycerides 180 mg/dL, VLDL 35", "Lipid Profile"),
    ("Lipid Profile Serum: Cholesterol 190 mg/dL, Triglycerides 150 mg/dL, Direct LDL 110 mg/dL, Direct HDL 50 mg/dL", "Lipid Profile"),
    ("Cardiovascular Lipid Risk Panel: Total Chol 240, HDL Chol 38, LDL Chol 160, Non-HDL Chol 202, Triglycerides 210 mg/dL", "Lipid Profile"),

    # Liver Function Test
    ("Liver Function Test (LFT): Total Bilirubin 1.2 mg/dL, Direct Bilirubin 0.3 mg/dL, SGOT (AST) 32 U/L, SGPT (ALT) 45 U/L, ALP 95 U/L", "Liver Function Test"),
    ("Hepatic Panel: ALT 55 IU/L, AST 48 IU/L, Total Protein 7.2 g/dL, Serum Albumin 4.1 g/dL, Alkaline Phosphatase 110 IU/L", "Liver Function Test"),
    ("Liver Profile: Bilirubin Total 0.9 mg/dL, SGPT 38 U/L, SGOT 29 U/L, Gamma GT 35 U/L, Total Protein 6.8 g/dL", "Liver Function Test"),

    # Kidney Function Test
    ("Kidney Function Test (KFT / RFT): Serum Creatinine 1.1 mg/dL, Blood Urea Nitrogen (BUN) 18 mg/dL, Urea 32 mg/dL, Uric Acid 5.5 mg/dL", "Kidney Function Test"),
    ("Renal Profile: eGFR 88 mL/min/1.73m2, Creatinine 0.9 mg/dL, Serum Sodium 140 mEq/L, Potassium 4.2 mEq/L, Chloride 101 mEq/L", "Kidney Function Test"),
    ("Renal Function Panel: Blood Urea 28 mg/dL, Serum Creatinine 1.4 mg/dL, Serum Electrolytes Sodium 138, Potassium 4.8", "Kidney Function Test"),

    # Thyroid Test
    ("Thyroid Profile: Thyroid Stimulating Hormone (TSH) 2.4 mIU/L, Total T3 1.2 ng/mL, Total T4 8.5 ug/dL", "Thyroid Test"),
    ("Thyroid Function Test: Free T3 3.1 pg/mL, Free T4 1.2 ng/dL, Ultrasensitive TSH 4.8 uIU/mL", "Thyroid Test"),
    ("Serum TSH 6.5 mIU/L (0.4-4.0), Anti-TPO Antibodies positive, Free Thyroxine FT4 0.9 ng/dL", "Thyroid Test"),

    # Urine Analysis
    ("Complete Urinalysis: Color Pale Yellow, Specific Gravity 1.015, pH 6.0, Protein Negative, Glucose Nil, Pus Cells 1-2 /HPF, RBCs Nil", "Urine Analysis"),
    ("Routine Urine Examination: Appearance Clear, Leukocyte Esterase Negative, Nitrite Negative, Ketones Negative, Epithelial Cells 2-3", "Urine Analysis"),
    ("Microscopic Urine Analysis: Specific Gravity 1.020, Casts None, Crystals Calcium Oxalate Few, Bacteria Absent", "Urine Analysis"),

    # Radiology
    ("Chest X-Ray PA View: Both lung fields are clear. Costophrenic angles are sharp. Cardiothoracic ratio is normal. No acute focal consolidation.", "Radiology"),
    ("MRI Brain with Contrast: No acute intracranial hemorrhage, territorial infarction, or mass effect. Ventricles and sulci are age-appropriate.", "Radiology"),
    ("Ultrasound Abdomen & Pelvis: Liver is normal in size with normal echotexture. Gallbladder is clear of calculi. Kidneys show normal parenchymal thickness.", "Radiology"),
    ("CT Scan Thorax Non-Contrast: No evidence of pleural effusion or pneumothorax. Mediastinal structures unremarkable.", "Radiology"),

    # Pathology
    ("Histopathology Report: Biopsy of gastric mucosa demonstrates chronic mild superficial gastritis without Helicobacter pylori or intestinal metaplasia.", "Pathology"),
    ("Surgical Pathology Report: Excisional skin biopsy demonstrates benign intradermal melanocytic nevus with clear surgical margins.", "Pathology"),
    ("Cytology Examination: Fine needle aspiration cytology (FNAC) of thyroid nodule reveals benign follicular nodule (Bethesda Category II).", "Pathology"),

    # Discharge Summary
    ("Discharge Summary: Patient admitted on 2026-05-10 with acute gastroenteritis. Hospital course uneventful. Discharged in stable condition on oral hydration.", "Discharge Summary"),
    ("Hospital Discharge Note: Chief Admission Diagnosis: Community acquired pneumonia. Resolved with IV Ceftriaxone. Follow-up in outpatient clinic in 1 week.", "Discharge Summary"),

    # Clinical Note
    ("Outpatient Clinical Consultation Note: 54-year-old female presents for routine hypertension follow-up. Blood pressure 128/82 mmHg. Systemic exam unremarkable.", "Clinical Note"),
    ("Progress Note: Patient reports mild tension headache for 2 days. Physical examination: Cranial nerves intact, neck supple. Plan: Rest, hydration.", "Clinical Note"),

    # Other
    ("Invoice and billing receipt for hospital diagnostic services. Total charges: $150.00. Payment method: Insurance.", "Other"),
    ("Patient appointment confirmation and hospital visit schedule instructions.", "Other"),
]


def train():
    texts, labels = zip(*DATASET)

    # Use TF-IDF + Logistic Regression
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=1000)
    X = vectorizer.fit_transform(texts)
    y = labels

    model = LogisticRegression(C=1.0, max_iter=300, random_state=42)
    model.fit(X, y)

    # Save model artifact
    models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    os.makedirs(models_dir, exist_ok=True)
    out_path = os.path.join(models_dir, "classifier.joblib")

    artifact = {
        "model": model,
        "vectorizer": vectorizer,
        "classes": list(model.classes_),
    }
    joblib.dump(artifact, out_path)
    print(f"Model saved successfully to: {out_path}")
    print(f"Trained on {len(texts)} samples across {len(set(labels))} classes.")
    return out_path


if __name__ == "__main__":
    train()
