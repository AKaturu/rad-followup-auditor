from __future__ import annotations

import pandas as pd
import pytest

from rad_followup_auditor.config import (
    COL_HAS_EXPLICIT_RECOMMENDATION,
    COL_IS_NEGATED,
    COL_RECOMMENDATION_TEXT,
)
from rad_followup_auditor.extraction import ExtractionEngine, extract_all


@pytest.fixture
def engine() -> ExtractionEngine:
    return ExtractionEngine()


class TestExtractionEngine:
    def test_empty_text(self, engine: ExtractionEngine) -> None:
        result = engine.extract_report("", report_id="empty")
        assert not result.has_explicit_recommendation
        assert result.review_required
        assert result.confidence == "low"

    def test_whitespace_text(self, engine: ExtractionEngine) -> None:
        result = engine.extract_report("   ", report_id="ws")
        assert not result.has_explicit_recommendation
        assert result.review_required

    def test_explicit_recommendation_ct(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: 8 mm pulmonary nodule in the right upper lobe. "
            "IMPRESSION: Recommend CT chest in 6 months."
        )
        result = engine.extract_report(text, report_id="R001")
        assert result.has_explicit_recommendation
        assert result.recommended_modality == "CT"
        assert result.interval_value == 6.0
        assert result.interval_unit == "months"
        assert result.confidence == "high"
        assert not result.is_negated

    def test_finding_context_strips_section_label(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: Pulmonary nodule is present. "
            "IMPRESSION: Pulmonary nodule is present; recommend CT chest in 6 months."
        )
        result = engine.extract_report(text, report_id="R001A")
        assert result.finding == "pulmonary nodule is present"

    def test_finding_context_handles_conclusion_label(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: Liver lesion is present. "
            "CONCLUSION: Liver lesion is present; advise MRI abdomen in 3 months."
        )
        result = engine.extract_report(text, report_id="R001B")
        assert result.finding == "liver lesion is present"

    def test_negation_no_followup(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: Normal examination. No acute findings. "
            "IMPRESSION: No further imaging recommended."
        )
        result = engine.extract_report(text, report_id="R002")
        assert result.is_negated
        assert not result.has_explicit_recommendation
        assert result.confidence == "high"

    def test_followup_with_interval(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: 1.5 cm liver lesion. "
            "IMPRESSION: Suggest MRI in 12 months to evaluate stability."
        )
        result = engine.extract_report(text, report_id="R003")
        assert result.has_explicit_recommendation
        assert result.recommended_modality == "MRI"
        assert result.interval_value == 12.0
        assert result.interval_unit == "months"
        assert result.confidence == "high"

    def test_ultrasound_followup(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: 2 cm ovarian cyst. "
            "IMPRESSION: Follow-up ultrasound in 8 weeks is recommended."
        )
        result = engine.extract_report(text, report_id="R004")
        assert result.has_explicit_recommendation
        assert result.recommended_modality == "Ultrasound"
        assert result.interval_value == 8.0
        assert result.interval_unit == "weeks"

    def test_annual_interval(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: 5 mm lung nodule. "
            "IMPRESSION: Recommend follow-up CT annually."
        )
        result = engine.extract_report(text, report_id="R005")
        assert result.has_explicit_recommendation
        assert result.interval_value == 1.0
        assert result.interval_unit == "years"

    def test_no_followup_normal(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: The heart is normal in size. The lungs are clear. "
            "IMPRESSION: Normal examination."
        )
        result = engine.extract_report(text, report_id="R006")
        assert not result.has_explicit_recommendation

    def test_clinical_correlation(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: 1 cm adrenal nodule. "
            "IMPRESSION: Clinical correlation recommended."
        )
        result = engine.extract_report(text, report_id="R007")
        assert result.confidence in ("medium", "low")
        assert result.review_required

    def test_biopsy_recommendation(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: 2 cm spiculated breast mass. "
            "IMPRESSION: Recommend ultrasound-guided biopsy."
        )
        result = engine.extract_report(text, report_id="R008")
        assert result.has_explicit_recommendation
        assert result.recommended_modality == "Ultrasound" or "biopsy" in (
            result.recommended_modality or ""
        ).lower()

    def test_urgent_recommendation(self, engine: ExtractionEngine) -> None:
        text = (
            "FINDINGS: Large right pleural effusion. "
            "IMPRESSION: Urgent CT chest recommended."
        )
        result = engine.extract_report(text, report_id="R009")
        assert result.urgency == "urgent"

    def test_dataframe_batch(self, engine: ExtractionEngine) -> None:
        df = pd.DataFrame(
            {
                "report_id": ["R1", "R2", "R3"],
                "report_text": [
                    "Normal exam. No follow-up needed.",
                    "8 mm nodule. Recommend CT in 6 months.",
                    "Clear lungs. Impression: Normal.",
                ],
            }
        )
        result = engine.extract_dataframe(df)
        assert len(result) == 3
        assert result.iloc[0][COL_IS_NEGATED]
        assert result.iloc[1][COL_HAS_EXPLICIT_RECOMMENDATION]
        assert not result.iloc[2][COL_HAS_EXPLICIT_RECOMMENDATION]


class TestExtractAll:
    def test_extract_all_function(self) -> None:
        df = pd.DataFrame(
            {
                "report_id": ["R1"],
                "report_text": [
                    "6 mm lung nodule. Recommend CT chest in 12 months."
                ],
            }
        )
        result = extract_all(df)
        assert len(result) == 1
        assert result.iloc[0][COL_HAS_EXPLICIT_RECOMMENDATION]
        assert result.iloc[0][COL_RECOMMENDATION_TEXT] is not None

    def test_empty_dataframe(self) -> None:
        df = pd.DataFrame({"report_id": [], "report_text": []})
        result = extract_all(df)
        assert len(result) == 0

    def test_with_input_columns(self) -> None:
        df = pd.DataFrame(
            {
                "report_id": ["R1"],
                "report_text": ["Recommend MRI in 3 months."],
                "modality": ["CT"],
            }
        )
        result = extract_all(df)
        assert len(result) == 1
