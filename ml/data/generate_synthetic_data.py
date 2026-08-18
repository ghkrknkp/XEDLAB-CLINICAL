"""Generates a small synthetic labeled dataset of report snippets for training
the TF-IDF + Logistic Regression report classifier.

This is clearly synthetic (not real patient data) and exists so the project
is runnable end-to-end without requiring a real, privacy-sensitive corpus.
Swap in real de-identified report text for production use.
"""
import csv
import os
import random

random.seed(42)

TEMPLATES = {
    "CBC": [
        "Complete Blood Count\nHemoglobin {hb} g/dL 12.0-16.0\nWBC {wbc} /uL 4000-11000\nPlatelets {plt} /uL 150000-450000\nRBC {rbc} million/uL 4.2-5.4\nHematocrit {hct} % 36-46",
        "CBC Report\nHb {hb} g/dL Ref 13-17\nWhite Blood Cell Count {wbc} /uL Ref 4500-11000\nPlatelet Count {plt} /uL Ref 150000-410000",
    ],
    "Lipid Profile": [
        "Lipid Profile\nTotal Cholesterol {tc} mg/dL 125-200\nHDL Cholesterol {hdl} mg/dL 40-60\nLDL Cholesterol {ldl} mg/dL 0-100\nTriglycerides {tg} mg/dL 0-150",
        "Cholesterol Panel\nCholesterol {tc} mg/dL Ref <200\nHDL {hdl} mg/dL Ref >40\nLDL {ldl} mg/dL Ref <100\nTriglycerides {tg} mg/dL Ref <150",
    ],
    "Liver Function Test": [
        "Liver Function Test\nSGOT (AST) {ast} U/L 10-40\nSGPT (ALT) {alt} U/L 7-56\nTotal Bilirubin {bili} mg/dL 0.1-1.2\nAlkaline Phosphatase {alp} U/L 44-147",
        "LFT Panel\nALT {alt} IU/L Ref 7-55\nAST {ast} IU/L Ref 8-48\nBilirubin Total {bili} mg/dL Ref 0.3-1.0",
    ],
    "Kidney Function Test": [
        "Kidney Function Test\nCreatinine {creat} mg/dL 0.6-1.3\nBlood Urea Nitrogen {bun} mg/dL 7-20\nUric Acid {ua} mg/dL 3.5-7.2\neGFR {egfr} mL/min 90-120",
        "Renal Panel\nSerum Creatinine {creat} mg/dL Ref 0.7-1.3\nUrea {bun} mg/dL Ref 15-40",
    ],
    "Thyroid Test": [
        "Thyroid Function Test\nTSH {tsh} mIU/L 0.4-4.0\nFree T3 {t3} pg/mL 2.3-4.2\nFree T4 {t4} ng/dL 0.8-1.8",
        "Thyroid Panel\nTSH {tsh} uIU/mL Ref 0.27-4.2\nT4 {t4} ng/dL Ref 0.9-1.7",
    ],
    "Urine Analysis": [
        "Urine Analysis Report\nColor Pale Yellow\nSpecific Gravity 1.02\npH 6.0\nProtein Negative\nGlucose Negative\nUrine Microscopy: RBC 0-2/hpf, WBC 0-3/hpf",
        "Urinalysis\nAppearance Clear\nSpecific Gravity 1.015\nProtein Trace\nKetones Negative\nNitrite Negative",
    ],
    "Radiology": [
        "Radiology Report\nChest X-Ray: No active infiltrate. Cardiac silhouette normal. No pleural effusion.",
        "MRI Report\nMRI Brain: No acute intracranial abnormality. Ventricles normal in size.",
        "Ultrasound Abdomen\nLiver, gallbladder, pancreas, spleen and kidneys appear normal in echotexture.",
    ],
    "Pathology": [
        "Histopathology Report\nSpecimen: Biopsy tissue. Microscopic examination reveals benign findings. No malignancy identified.",
        "Cytology Report\nFine needle aspiration cytology shows benign cellular pattern.",
    ],
    "Discharge Summary": [
        "Discharge Summary\nPatient admitted with fever and cough. Treated with antibiotics. Discharged in stable condition. Follow up in 1 week.",
        "Discharge Summary\nAdmitted for observation following minor procedure. Discharged on day 2, condition stable.",
    ],
    "Clinical Note": [
        "Clinical Note\nChief Complaint: Headache for 3 days.\nHistory of Present Illness: Patient reports throbbing frontal headache.\nPhysical Examination: Vitals stable, no focal neurological deficit.",
        "Progress Note\nChief Complaint: Follow-up visit.\nHistory of Present Illness: Improving symptoms since last visit.\nPhysical Examination: Unremarkable.",
    ],
}


def _rand(a, b, decimals=1):
    return round(random.uniform(a, b), decimals)


def _fill(template: str) -> str:
    return template.format(
        hb=_rand(9, 17), wbc=int(_rand(3000, 13000, 0)), plt=int(_rand(100000, 500000, 0)),
        rbc=_rand(3.5, 6.0), hct=_rand(30, 50),
        tc=int(_rand(140, 260, 0)), hdl=int(_rand(25, 70, 0)), ldl=int(_rand(60, 180, 0)), tg=int(_rand(60, 250, 0)),
        ast=int(_rand(10, 90, 0)), alt=int(_rand(7, 100, 0)), bili=_rand(0.1, 2.5), alp=int(_rand(40, 200, 0)),
        creat=_rand(0.5, 2.0), bun=int(_rand(6, 40, 0)), ua=_rand(3.0, 9.0), egfr=int(_rand(45, 130, 0)),
        tsh=_rand(0.1, 8.0), t3=_rand(1.5, 5.0), t4=_rand(0.5, 2.2),
    )


def generate(n_per_label: int = 40):
    rows = []
    for label, templates in TEMPLATES.items():
        for _ in range(n_per_label):
            template = random.choice(templates)
            rows.append({"text": _fill(template), "label": label})
    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    rows = generate()
    out_path = os.path.join(os.path.dirname(__file__), "synthetic_reports.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")
