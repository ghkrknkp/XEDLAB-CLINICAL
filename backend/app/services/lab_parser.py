"""Laboratory measurement, unit, and reference-range parser.

CRITICAL MANDATE:
Extract test values, units, and printed reference ranges deterministically.
Never use an LLM for numerical extraction or comparison.
"""
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from app.services.range_checker import check_range_or_unknown

# Comprehensive medical laboratory units
KNOWN_UNITS = [
    "mg/dL", "mmol/L", "g/dL", "g/L", "µL", "uL", "/µL", "/uL", "/ul", "/mm3",
    "IU/L", "U/L", "u/l", "ng/mL", "pg/mL", "mIU/L", "µIU/mL", "uIU/mL",
    "mEq/L", "%", "fL", "fl", "pg", "cells/mcL", "mm/hr", "10^3/uL", "10^6/uL",
    "10*3/uL", "10*6/uL", "k/uL", "M/uL", "sec", "seconds", "ratio",
]
# Regex pattern matching units (longest first)
_UNIT_PATTERN = "|".join(sorted((re.escape(u) for u in KNOWN_UNITS), key=len, reverse=True))

# Common laboratory test names for confidence boosting
KNOWN_TEST_NAMES = {
    "hemoglobin", "hb", "hematocrit", "hct", "wbc", "white blood cell", "white blood cells",
    "rbc", "red blood cell", "red blood cells", "platelets", "platelet count", "plt",
    "mcv", "mch", "mchc", "rdw", "neutrophils", "lymphocytes", "monocytes", "eosinophils", "basophils",
    "glucose", "fasting glucose", "postprandial glucose", "random glucose", "hba1c",
    "cholesterol", "total cholesterol", "hdl", "hdl cholesterol", "ldl", "ldl cholesterol",
    "triglycerides", "vldl", "alt", "sgpt", "ast", "sgot", "alkaline phosphatase", "alp",
    "bilirubin", "total bilirubin", "direct bilirubin", "indirect bilirubin",
    "albumin", "globulin", "total protein", "ag ratio", "a/g ratio",
    "creatinine", "serum creatinine", "urea", "blood urea", "bun", "egfr", "uric acid",
    "sodium", "potassium", "chloride", "bicarbonate", "calcium", "phosphorus", "magnesium",
    "tsh", "t3", "total t3", "t4", "total t4", "free t3", "ft3", "free t4", "ft4",
    "vitamin d", "25-hydroxy vitamin d", "vitamin b12", "ferritin", "iron", "tibc",
    "esr", "crp", "c-reactive protein", "psa", "troponin", "d-dimer",
    "inr", "pt", "aptt",
}

# Regex pattern for lab result lines:
# Examples:
# - Hemoglobin 10.2 g/dL 12.0 - 16.0
# - Glucose: 128 mg/dL (70-100)
# - Creatinine 1.1 mg/dL 0.6-1.2
# - WBC 7200 /uL 4000 - 11000
# - Platelets 250000 /uL 150000 - 450000
# - Hematocrit 39 % 36 - 46
# - TSH 2.1 mIU/L Ref: 0.4 - 4.0
# - Potassium 4.5 mEq/L [3.5 to 5.0]
ROW_PATTERN = re.compile(
    r"""^(?P<name>[A-Za-z0-9\s/()\-]{2,45}?)\s*[:=\t]\s*
        (?P<value>-?\d+(?:\.\d+)?)\s*
        (?P<unit>""" + _UNIT_PATTERN + r""")?\s*
        (?:[\[(]?(?:reference\s*range\s*[:\-]?\s*|ref\.?\s*[:\-]?\s*|normal\s*[:\-]?\s*)?
           (?P<ref_low>\d+(?:\.\d+)?)\s*(?:-|–|—|to|\.\.)\s*(?P<ref_high>\d+(?:\.\d+)?)[\])]?
        )?
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Alternative regex for whitespace-separated tabular rows (no colon/equals)
TABULAR_ROW_PATTERN = re.compile(
    r"""(?P<name>[A-Za-z][A-Za-z0-9\s/()\-]{1,40}?)\s+
        (?P<value>-?\d+(?:\.\d+)?)\s*
        (?P<unit>""" + _UNIT_PATTERN + r""")?\s*
        (?:[\[(]?(?:reference\s*range\s*[:\-]?\s*|ref\.?\s*[:\-]?\s*|normal\s*[:\-]?\s*)?
           (?P<ref_low>\d+(?:\.\d+)?)\s*(?:-|–|—|to|\.\.)\s*(?P<ref_high>\d+(?:\.\d+)?)[\])]?
        )?
    """,
    re.IGNORECASE | re.VERBOSE,
)


@dataclass
class LabFindingRaw:
    test_name: str
    value: Optional[float]
    unit: Optional[str]
    reference_low: Optional[float]
    reference_high: Optional[float]
    original_reference_text: Optional[str]
    reference_text: Optional[str]
    status: str
    confidence: float
    page_number: int
    source_text: str


def _calculate_confidence(test_name: str, unit: Optional[str], has_range: bool) -> float:
    """Calculates extraction confidence score reflecting pattern quality."""
    score = 0.50
    clean_name = test_name.strip().lower()

    if clean_name in KNOWN_TEST_NAMES or any(k in clean_name for k in KNOWN_TEST_NAMES):
        score += 0.25
    if unit:
        score += 0.15
    if has_range:
        score += 0.10

    return round(min(score, 0.99), 2)


def parse_lab_values(pages: List[Dict[str, Any]]) -> List[LabFindingRaw]:
    """Extracts lab values, units, and printed reference ranges from cleaned report pages."""
    findings: List[LabFindingRaw] = []
    seen_keys = set()

    for page in pages:
        text = page.get("text", "")
        page_number = page.get("page", 1)

        for line in text.split("\n"):
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Skip metadata and header lines
            lower_line = line.lower()
            if any(lower_line.startswith(prefix) for prefix in [
                "patient id", "patient name", "date", "age:", "gender:", "sex:", "doctor:", "hospital:", "page "
            ]):
                continue

            match = ROW_PATTERN.search(line) or TABULAR_ROW_PATTERN.search(line)
            if not match:
                continue

            name = match.group("name").strip(" :-\t")
            if not name or len(name) < 2:
                continue

            # Ignore generic keywords matching as test names
            if name.lower() in {"page", "reference", "range", "units", "result", "test name", "investigation", "observed value"}:
                continue

            try:
                value = float(match.group("value"))
            except (TypeError, ValueError):
                continue

            unit = match.group("unit")
            ref_low_raw = match.group("ref_low")
            ref_high_raw = match.group("ref_high")

            ref_low = float(ref_low_raw) if ref_low_raw is not None else None
            ref_high = float(ref_high_raw) if ref_high_raw is not None else None

            if ref_low is not None and ref_high is not None:
                original_reference_text = f"{ref_low_raw}-{ref_high_raw}"
            else:
                original_reference_text = None

            # Deduplication key for multiple regex matches on same line
            dedup_key = (name.lower(), value, page_number)
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            # Deterministic range classification
            status = check_range_or_unknown(value, ref_low, ref_high)
            has_range = ref_low is not None and ref_high is not None
            confidence = _calculate_confidence(name, unit, has_range)

            findings.append(LabFindingRaw(
                test_name=name.title(),
                value=value,
                unit=unit,
                reference_low=ref_low,
                reference_high=ref_high,
                original_reference_text=original_reference_text,
                reference_text=original_reference_text,
                status=status,
                confidence=confidence,
                page_number=page_number,
                source_text=line,
            ))

    return findings
