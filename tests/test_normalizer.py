from __future__ import annotations

from rad_followup_auditor.extraction.normalizer import (
    extract_anatomic_region,
    extract_interval,
    extract_modality,
    normalize_finding,
)


class TestExtractInterval:
    def test_numeric_months(self) -> None:
        val, unit = extract_interval("Recommend CT in 6 months")
        assert val == 6.0
        assert unit == "months"

    def test_numeric_years(self) -> None:
        val, unit = extract_interval("Follow-up MRI in 2 years")
        assert val == 2.0
        assert unit == "years"

    def test_numeric_weeks(self) -> None:
        val, unit = extract_interval("US in 8 weeks")
        assert val == 8.0
        assert unit == "weeks"

    def test_annually(self) -> None:
        val, unit = extract_interval("recommend follow-up CT annually")
        assert val == 1.0
        assert unit == "years"

    def test_monthly(self) -> None:
        val, unit = extract_interval("surveillance imaging monthly")
        assert val == 1.0
        assert unit == "months"

    def test_no_interval(self) -> None:
        val, unit = extract_interval("No follow-up needed")
        assert val is None
        assert unit is None

    def test_quarterly(self) -> None:
        val, unit = extract_interval("quarterly follow-up recommended")
        assert val == 3.0
        assert unit == "months"

    def test_range_interval(self) -> None:
        val, unit = extract_interval("CT in 3-6 months")
        assert val == 3.0
        assert unit == "months"


class TestExtractModality:
    def test_ct(self) -> None:
        assert extract_modality("CT") == "CT"
        assert extract_modality("ct") == "CT"

    def test_mri(self) -> None:
        assert extract_modality("MRI") == "MRI"

    def test_ultrasound(self) -> None:
        assert extract_modality("ultrasound") == "Ultrasound"
        assert extract_modality("US") == "Ultrasound"

    def test_no_modality(self) -> None:
        assert extract_modality("no imaging needed") is None


class TestExtractAnatomicRegion:
    def test_chest(self) -> None:
        assert extract_anatomic_region("CT chest") == "chest"

    def test_abdomen(self) -> None:
        assert extract_anatomic_region("ultrasound abdomen") == "abdomen"

    def test_no_region(self) -> None:
        assert extract_anatomic_region("routine follow-up") is None

    def test_liver(self) -> None:
        assert extract_anatomic_region("MRI liver") == "liver"


class TestNormalizeFinding:
    def test_basic(self) -> None:
        assert normalize_finding("  Pulmonary Nodule  ") == "pulmonary nodule"

    def test_trailing_punctuation(self) -> None:
        assert normalize_finding("liver lesion.") == "liver lesion"

    def test_extra_spaces(self) -> None:
        assert normalize_finding("lung   nodule") == "lung nodule"
