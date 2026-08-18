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
    "mg/dL", "mg/dl", "mmol/L", "mmol/l", "g/dL", "g/dl", "gm/dl", "gm/dL", "gm%", "g%",
    "g/L", "g/l", "mg/L", "mg/l", "µL", "uL", "/µL", "/uL", "/ul", "/mm3", "mm3",
    "/cumm", "cumm", "cells/cumm", "lakhs/cumm", "lakh/cumm",
    "IU/L", "iu/l", "iu/L", "U/L", "u/l", "U/l", "ng/mL", "ng/ml", "pg/mL", "pg/ml",
    "mIU/L", "mIU/ml", "mIU/mL", "µIU/mL", "uIU/mL", "uIU/ml", "uiu/ml",
    "mEq/L", "meq/l", "%", "fL", "fl", "pg", "cells/mcL", "mm/hr", "mm/1st hr",
    "10^3/uL", "10^6/uL", "10*3/uL", "10*6/uL", "k/uL", "M/uL", "sec", "seconds", "ratio",
]
# Regex pattern matching units (longest first)
_UNIT_PATTERN = "|".join(sorted((re.escape(u) for u in KNOWN_UNITS), key=len, reverse=True))

# Comprehensive medical test dictionary with standard default reference ranges
KNOWN_TEST_NAMES = {
    "hemoglobin": {"low": 12.0, "high": 16.0, "unit": "g/dL"},
    "haemoglobin": {"low": 12.0, "high": 16.0, "unit": "g/dL"},
    "hb": {"low": 12.0, "high": 16.0, "unit": "g/dL"},
    "hgb": {"low": 12.0, "high": 16.0, "unit": "g/dL"},
    "hematocrit": {"low": 36.0, "high": 46.0, "unit": "%"},
    "haematocrit": {"low": 36.0, "high": 46.0, "unit": "%"},
    "hct": {"low": 36.0, "high": 46.0, "unit": "%"},
    "pcv": {"low": 36.0, "high": 46.0, "unit": "%"},
    "wbc": {"low": 4000.0, "high": 11000.0, "unit": "/uL"},
    "white blood cell": {"low": 4000.0, "high": 11000.0, "unit": "/uL"},
    "white blood cells": {"low": 4000.0, "high": 11000.0, "unit": "/uL"},
    "total leukocyte count": {"low": 4000.0, "high": 11000.0, "unit": "/uL"},
    "tlc": {"low": 4000.0, "high": 11000.0, "unit": "/uL"},
    "rbc": {"low": 4.5, "high": 5.5, "unit": "million/uL"},
    "red blood cell": {"low": 4.5, "high": 5.5, "unit": "million/uL"},
    "red blood cells": {"low": 4.5, "high": 5.5, "unit": "million/uL"},
    "total rbc": {"low": 4.5, "high": 5.5, "unit": "million/uL"},
    "platelets": {"low": 150000.0, "high": 450000.0, "unit": "/uL"},
    "platelet count": {"low": 150000.0, "high": 450000.0, "unit": "/uL"},
    "plt": {"low": 150000.0, "high": 450000.0, "unit": "/uL"},
    "mcv": {"low": 80.0, "high": 100.0, "unit": "fL"},
    "mch": {"low": 27.0, "high": 33.0, "unit": "pg"},
    "mchc": {"low": 32.0, "high": 36.0, "unit": "g/dL"},
    "rdw": {"low": 11.5, "high": 14.5, "unit": "%"},
    "neutrophils": {"low": 40.0, "high": 75.0, "unit": "%"},
    "lymphocytes": {"low": 20.0, "high": 45.0, "unit": "%"},
    "monocytes": {"low": 2.0, "high": 10.0, "unit": "%"},
    "eosinophils": {"low": 1.0, "high": 6.0, "unit": "%"},
    "basophils": {"low": 0.0, "high": 2.0, "unit": "%"},
    "glucose": {"low": 70.0, "high": 100.0, "unit": "mg/dL"},
    "fasting glucose": {"low": 70.0, "high": 100.0, "unit": "mg/dL"},
    "fasting blood sugar": {"low": 70.0, "high": 100.0, "unit": "mg/dL"},
    "fbs": {"low": 70.0, "high": 100.0, "unit": "mg/dL"},
    "postprandial glucose": {"low": 70.0, "high": 140.0, "unit": "mg/dL"},
    "ppbs": {"low": 70.0, "high": 140.0, "unit": "mg/dL"},
    "random blood sugar": {"low": 70.0, "high": 140.0, "unit": "mg/dL"},
    "rbs": {"low": 70.0, "high": 140.0, "unit": "mg/dL"},
    "blood sugar": {"low": 70.0, "high": 140.0, "unit": "mg/dL"},
    "hba1c": {"low": 4.0, "high": 5.6, "unit": "%"},
    "cholesterol": {"low": 125.0, "high": 200.0, "unit": "mg/dL"},
    "total cholesterol": {"low": 125.0, "high": 200.0, "unit": "mg/dL"},
    "hdl": {"low": 40.0, "high": 60.0, "unit": "mg/dL"},
    "hdl cholesterol": {"low": 40.0, "high": 60.0, "unit": "mg/dL"},
    "ldl": {"low": 0.0, "high": 100.0, "unit": "mg/dL"},
    "ldl cholesterol": {"low": 0.0, "high": 100.0, "unit": "mg/dL"},
    "triglycerides": {"low": 35.0, "high": 150.0, "unit": "mg/dL"},
    "vldl": {"low": 5.0, "high": 30.0, "unit": "mg/dL"},
    "alt": {"low": 7.0, "high": 56.0, "unit": "U/L"},
    "sgpt": {"low": 7.0, "high": 56.0, "unit": "U/L"},
    "ast": {"low": 10.0, "high": 40.0, "unit": "U/L"},
    "sgot": {"low": 10.0, "high": 40.0, "unit": "U/L"},
    "alkaline phosphatase": {"low": 44.0, "high": 147.0, "unit": "U/L"},
    "alp": {"low": 44.0, "high": 147.0, "unit": "U/L"},
    "bilirubin": {"low": 0.2, "high": 1.2, "unit": "mg/dL"},
    "total bilirubin": {"low": 0.2, "high": 1.2, "unit": "mg/dL"},
    "direct bilirubin": {"low": 0.0, "high": 0.3, "unit": "mg/dL"},
    "indirect bilirubin": {"low": 0.2, "high": 0.8, "unit": "mg/dL"},
    "albumin": {"low": 3.5, "high": 5.0, "unit": "g/dL"},
    "globulin": {"low": 2.0, "high": 3.5, "unit": "g/dL"},
    "total protein": {"low": 6.0, "high": 8.3, "unit": "g/dL"},
    "ag ratio": {"low": 1.2, "high": 2.2, "unit": "ratio"},
    "a/g ratio": {"low": 1.2, "high": 2.2, "unit": "ratio"},
    "creatinine": {"low": 0.6, "high": 1.2, "unit": "mg/dL"},
    "serum creatinine": {"low": 0.6, "high": 1.2, "unit": "mg/dL"},
    "urea": {"low": 7.0, "high": 20.0, "unit": "mg/dL"},
    "blood urea": {"low": 15.0, "high": 40.0, "unit": "mg/dL"},
    "bun": {"low": 7.0, "high": 20.0, "unit": "mg/dL"},
    "egfr": {"low": 90.0, "high": 120.0, "unit": "mL/min"},
    "uric acid": {"low": 3.5, "high": 7.2, "unit": "mg/dL"},
    "sodium": {"low": 135.0, "high": 145.0, "unit": "mEq/L"},
    "potassium": {"low": 3.5, "high": 5.0, "unit": "mEq/L"},
    "chloride": {"low": 96.0, "high": 106.0, "unit": "mEq/L"},
    "calcium": {"low": 8.5, "high": 10.5, "unit": "mg/dL"},
    "phosphorus": {"low": 2.5, "high": 4.5, "unit": "mg/dL"},
    "tsh": {"low": 0.4, "high": 4.0, "unit": "mIU/L"},
    "t3": {"low": 80.0, "high": 200.0, "unit": "ng/dL"},
    "total t3": {"low": 80.0, "high": 200.0, "unit": "ng/dL"},
    "t4": {"low": 4.5, "high": 12.0, "unit": "ug/dL"},
    "total t4": {"low": 4.5, "high": 12.0, "unit": "ug/dL"},
    "free t3": {"low": 2.3, "high": 4.2, "unit": "pg/mL"},
    "ft3": {"low": 2.3, "high": 4.2, "unit": "pg/mL"},
    "free t4": {"low": 0.8, "high": 1.8, "unit": "ng/dL"},
    "ft4": {"low": 0.8, "high": 1.8, "unit": "ng/dL"},
    "vitamin d": {"low": 30.0, "high": 100.0, "unit": "ng/mL"},
    "25-hydroxy vitamin d": {"low": 30.0, "high": 100.0, "unit": "ng/mL"},
    "vitamin b12": {"low": 200.0, "high": 900.0, "unit": "pg/mL"},
    "ferritin": {"low": 15.0, "high": 200.0, "unit": "ng/mL"},
    "iron": {"low": 60.0, "high": 170.0, "unit": "ug/dL"},
    "esr": {"low": 0.0, "high": 20.0, "unit": "mm/hr"},
    "crp": {"low": 0.0, "high": 6.0, "unit": "mg/L"},
    "c-reactive protein": {"low": 0.0, "high": 6.0, "unit": "mg/L"},
}


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


def _clean_num(val_str: str) -> Optional[float]:
    """Cleans number string by removing commas, spaces, etc."""
    if not val_str:
        return None
    cleaned = val_str.replace(",", "").replace(" ", "").strip()
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def _calculate_confidence(test_name: str, unit: Optional[str], has_range: bool) -> float:
    """Calculates extraction confidence score reflecting pattern quality."""
    score = 0.55
    clean_name = test_name.strip().lower()

    if clean_name in KNOWN_TEST_NAMES or any(k in clean_name for k in KNOWN_TEST_NAMES):
        score += 0.25
    if unit:
        score += 0.10
    if has_range:
        score += 0.10

    return round(min(score, 0.99), 2)


def parse_lab_values(pages: List[Dict[str, Any]]) -> List[LabFindingRaw]:
    """Extracts lab values, units, and printed reference ranges from report pages.
    
    Robust parser handling:
    1. Standard regex table rows
    2. Pipe/tab/comma-separated OCR tables
    3. Dictionary-assisted extraction for scanned reports with irregular spacing
    """
    findings: List[LabFindingRaw] = []
    seen_keys = set()

    for page in pages:
        text = page.get("text", "")
        page_number = page.get("page", 1)

        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if not line or len(line) < 3:
                continue

            lower_line = line.lower()

            # Skip metadata and header lines
            if any(lower_line.startswith(prefix) for prefix in [
                "patient id", "patient name", "date", "age:", "gender:", "sex:", "doctor:", "hospital:", "page "
            ]):
                continue

            # Normalize line separators (replace pipes, tabs, multiple spaces)
            norm_line = re.sub(r"[|\t]+", " ", line)
            norm_line = re.sub(r"\s{2,}", " ", norm_line).strip()

            # Pattern 1: TestName [:=-] Value [Unit] [ReferenceRange]
            p1 = re.search(
                r"""^(?P<name>[A-Za-z][A-Za-z0-9\s/()\-]{1,40}?)\s*[:=\-]\s*
                    (?P<value>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*
                    (?P<unit>""" + _UNIT_PATTERN + r""")?\s*
                    (?:[\[(]?(?:ref\.?\s*(?:range)?\s*[:\-]?\s*|normal\s*[:\-]?\s*)?
                       (?P<ref_low>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?:-|–|—|to|\.\.)\s*
                       (?P<ref_high>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)[\])]?
                    )?""",
                norm_line,
                re.IGNORECASE | re.VERBOSE,
            )

            # Pattern 2: Tabular whitespace-separated row
            p2 = re.search(
                r"""^(?P<name>[A-Za-z][A-Za-z0-9\s/()\-]{1,40}?)\s+
                    (?P<value>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*
                    (?P<unit>""" + _UNIT_PATTERN + r""")?\s*
                    (?:[\[(]?(?:ref\.?\s*(?:range)?\s*[:\-]?\s*|normal\s*[:\-]?\s*)?
                       (?P<ref_low>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?:-|–|—|to|\.\.)\s*
                       (?P<ref_high>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)[\])]?
                    )?""",
                norm_line,
                re.IGNORECASE | re.VERBOSE,
            )

            match = p1 or p2

            if match:
                name = match.group("name").strip(" :-\t")
                val_raw = match.group("value")
                unit = match.group("unit")
                ref_low_raw = match.group("ref_low")
                ref_high_raw = match.group("ref_high")

                value = _clean_num(val_raw)
                if value is None or len(name) < 2:
                    continue

                # Ignore table headers matching as test names
                if name.lower() in {"page", "reference", "range", "units", "result", "test name", "investigation", "observed value", "parameters"}:
                    continue

                ref_low = _clean_num(ref_low_raw)
                ref_high = _clean_num(ref_high_raw)

                # Fallback to known range if range wasn't printed
                clean_lookup = name.lower().strip()
                if (ref_low is None or ref_high is None) and clean_lookup in KNOWN_TEST_NAMES:
                    ref_low = KNOWN_TEST_NAMES[clean_lookup]["low"]
                    ref_high = KNOWN_TEST_NAMES[clean_lookup]["high"]
                    if not unit:
                        unit = KNOWN_TEST_NAMES[clean_lookup]["unit"]

                orig_ref = f"{ref_low} - {ref_high}" if ref_low is not None and ref_high is not None else None
                status = check_range_or_unknown(value, ref_low, ref_high)
                has_range = ref_low is not None and ref_high is not None
                confidence = _calculate_confidence(name, unit, has_range)

                dedup_key = (name.lower(), value, page_number)
                if dedup_key not in seen_keys:
                    seen_keys.add(dedup_key)
                    findings.append(LabFindingRaw(
                        test_name=name.title(),
                        value=value,
                        unit=unit,
                        reference_low=ref_low,
                        reference_high=ref_high,
                        original_reference_text=orig_ref,
                        reference_text=orig_ref,
                        status=status,
                        confidence=confidence,
                        page_number=page_number,
                        source_text=line,
                    ))
                continue

            # Pattern 3: Dictionary scan on noisy OCR lines
            for test_key, test_info in KNOWN_TEST_NAMES.items():
                if test_key in lower_line:
                    # Find all numbers in the line after or around the test name
                    nums = re.findall(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b", line)
                    if nums:
                        val = _clean_num(nums[0])
                        if val is not None and val > 0:
                            ref_l = test_info["low"]
                            ref_h = test_info["high"]
                            if len(nums) >= 3:
                                r_l = _clean_num(nums[1])
                                r_h = _clean_num(nums[2])
                                if r_l is not None and r_h is not None and r_l < r_h:
                                    ref_l, ref_h = r_l, r_h

                            orig_ref = f"{ref_l} - {ref_h}"
                            status = check_range_or_unknown(val, ref_l, ref_h)
                            dedup_key = (test_key, val, page_number)

                            if dedup_key not in seen_keys:
                                seen_keys.add(dedup_key)
                                findings.append(LabFindingRaw(
                                    test_name=test_key.title(),
                                    value=val,
                                    unit=test_info["unit"],
                                    reference_low=ref_l,
                                    reference_high=ref_h,
                                    original_reference_text=orig_ref,
                                    reference_text=orig_ref,
                                    status=status,
                                    confidence=0.88,
                                    page_number=page_number,
                                    source_text=line,
                                ))
                            break

    return findings
