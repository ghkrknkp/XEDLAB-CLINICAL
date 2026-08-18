"""Medical entity extraction: Hybrid Regex + Medical Dictionaries + NER.

Extracts:
- Patient ID / MRN
- Age
- Sex / Gender
- Report Date
- Medical Conditions
- Symptoms
- Medications
- Medical Procedures
- Body Parts & Anatomy

Assigns extraction confidence to each detected entity.
"""
import re
from dataclasses import dataclass
from typing import List, Dict, Any

AGE_PATTERN = re.compile(r"\bAge\s*[:\-]?\s*(\d{1,3}(?:\s*(?:years|yrs|y/o|yo))?)\b", re.IGNORECASE)
SEX_PATTERN = re.compile(r"\b(?:Sex|Gender)\s*[:\-]?\s*(Male|Female|M|F)\b", re.IGNORECASE)
PATIENT_ID_PATTERN = re.compile(r"\b(?:Patient\s*(?:ID|No\.?)|MRN|UHID|Reg\s*No\.?)\s*[:\-]?\s*([A-Za-z0-9\-]{3,20})\b", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b(?:Date|Report\s*Date|Collected\s*Date)\s*[:\-]?\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b", re.IGNORECASE)

CONDITION_KEYWORDS = [
    "diabetes", "type 2 diabetes", "hypertension", "anemia", "hypothyroidism", "hyperthyroidism",
    "jaundice", "infection", "fever", "asthma", "arthritis", "fatty liver", "hyperlipidemia",
    "chronic kidney disease", "gastritis", "pneumonia", "bronchitis", "tachycardia",
]

SYMPTOM_KEYWORDS = [
    "fatigue", "headache", "nausea", "dizziness", "pain", "chest pain", "abdominal pain",
    "swelling", "shortness of breath", "cough", "weakness", "vomiting", "weight loss",
]

MEDICATION_KEYWORDS = [
    "metformin", "insulin", "atorvastatin", "amlodipine", "levothyroxine",
    "paracetamol", "aspirin", "ibuprofen", "losartan", "omeprazole", "pantoprazole",
    "metoprolol", "glipizide", "amoxicillin", "azithromycin",
]

PROCEDURE_KEYWORDS = [
    "biopsy", "x-ray", "ultrasound", "mri", "ct scan", "endoscopy", "ecg", "ekg",
    "echocardiogram", "fnac", "colonoscopy", "dialysis", "phlebotomy",
]

BODY_PART_KEYWORDS = [
    "liver", "kidney", "heart", "lung", "thyroid", "spine", "chest", "abdomen",
    "brain", "stomach", "gallbladder", "pancreas", "spleen", "bladder", "prostate",
]


@dataclass
class EntityFinding:
    entity_type: str
    entity_text: str
    page_number: int
    confidence: float


def _keyword_scan(text: str, keywords: List[str], entity_type: str, page: int, base_conf: float = 0.75) -> List[EntityFinding]:
    found = []
    lower = text.lower()
    for kw in keywords:
        # Match whole word/phrase
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, lower):
            found.append(EntityFinding(
                entity_type=entity_type,
                entity_text=kw.title(),
                page_number=page,
                confidence=base_conf,
            ))
    return found


def extract_entities(pages: List[Dict[str, Any]]) -> List[EntityFinding]:
    """Extracts demographic, clinical, and anatomical entities across all pages."""
    entities: List[EntityFinding] = []
    seen = set()

    for page in pages:
        text = page.get("text", "")
        page_number = page.get("page", 1)

        # 1. Patient Demographics & Identifiers
        age_match = AGE_PATTERN.search(text)
        if age_match:
            entities.append(EntityFinding("AGE", age_match.group(1).strip(), page_number, 0.90))

        sex_match = SEX_PATTERN.search(text)
        if sex_match:
            raw_sex = sex_match.group(1).upper()[0]
            val = "Male" if raw_sex == "M" else "Female"
            entities.append(EntityFinding("SEX", val, page_number, 0.90))

        pid_match = PATIENT_ID_PATTERN.search(text)
        if pid_match:
            entities.append(EntityFinding("PATIENT_ID", pid_match.group(1).strip(), page_number, 0.85))

        date_match = DATE_PATTERN.search(text)
        if date_match:
            entities.append(EntityFinding("DATE", date_match.group(1).strip(), page_number, 0.85))

        # 2. Medical Concept Dictionaries
        all_kw_entities = (
            _keyword_scan(text, CONDITION_KEYWORDS, "CONDITION", page_number, 0.80) +
            _keyword_scan(text, SYMPTOM_KEYWORDS, "SYMPTOM", page_number, 0.75) +
            _keyword_scan(text, MEDICATION_KEYWORDS, "MEDICATION", page_number, 0.80) +
            _keyword_scan(text, PROCEDURE_KEYWORDS, "PROCEDURE", page_number, 0.80) +
            _keyword_scan(text, BODY_PART_KEYWORDS, "BODY_PART", page_number, 0.80)
        )

        for ent in all_kw_entities:
            key = (ent.entity_type, ent.entity_text.lower(), page_number)
            if key not in seen:
                seen.add(key)
                entities.append(ent)

    return entities
