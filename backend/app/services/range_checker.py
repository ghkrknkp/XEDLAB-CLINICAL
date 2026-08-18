"""Deterministic numeric range checking.

CRITICAL SAFETY MANDATE (Requirements #6, #12, #13, #15, #21):
The LLM is NEVER used for mathematical comparison or deciding whether a value
is within or outside a reference range. All numerical checks are 100% deterministic.

Status values:
- within_reference_range
- below_reference_range
- above_reference_range
- not_classified
"""
from typing import Optional, Union


def check_range(value: float, low: float, high: float) -> str:
    """Pure deterministic comparison.

    Boundary behavior:
    - value < low: below_reference_range
    - value > high: above_reference_range
    - low <= value <= high: within_reference_range
    """
    if value < low:
        return "below_reference_range"
    elif value > high:
        return "above_reference_range"
    else:
        return "within_reference_range"


def check_range_or_unknown(
    value: Optional[Union[float, int, str]],
    low: Optional[Union[float, int, str]],
    high: Optional[Union[float, int, str]],
) -> str:
    """Safe wrapper: returns 'not_classified' if values/ranges cannot be parsed."""
    if value is None or low is None or high is None:
        return "not_classified"

    try:
        val_f = float(value)
        low_f = float(low)
        high_f = float(high)
        return check_range(val_f, low_f, high_f)
    except (TypeError, ValueError):
        return "not_classified"
