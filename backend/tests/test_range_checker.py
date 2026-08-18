import pytest
from app.services.range_checker import check_range, check_range_or_unknown


def test_mandatory_boundary_ranges():
    """Mandatory range boundary tests as specified in Requirement #15, #31."""
    # 10 vs 12-16 => below
    assert check_range(10.0, 12.0, 16.0) == "below_reference_range"

    # 12 vs 12-16 => within
    assert check_range(12.0, 12.0, 16.0) == "within_reference_range"

    # 16 vs 12-16 => within
    assert check_range(16.0, 12.0, 16.0) == "within_reference_range"

    # 17 vs 12-16 => above
    assert check_range(17.0, 12.0, 16.0) == "above_reference_range"


def test_float_precision_ranges():
    assert check_range(10.2, 12.0, 16.0) == "below_reference_range"
    assert check_range(14.5, 12.0, 16.0) == "within_reference_range"
    assert check_range(18.9, 12.0, 16.0) == "above_reference_range"


def test_missing_or_malformed_ranges():
    """Missing or unparseable reference range must yield not_classified."""
    assert check_range_or_unknown(10.0, None, None) == "not_classified"
    assert check_range_or_unknown(None, 12.0, 16.0) == "not_classified"
    assert check_range_or_unknown("abc", 12.0, 16.0) == "not_classified"
    assert check_range_or_unknown(10.0, "low", "high") == "not_classified"


def test_negative_values():
    """Support valid negative clinical ranges (e.g. base excess or delta)."""
    assert check_range(-3.0, -2.0, 2.0) == "below_reference_range"
    assert check_range(0.0, -2.0, 2.0) == "within_reference_range"
    assert check_range(3.0, -2.0, 2.0) == "above_reference_range"
