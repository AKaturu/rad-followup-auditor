from __future__ import annotations

from rad_followup_auditor.extraction.negation import check_negation, classify_recommendation_type


class TestCheckNegation:
    def test_direct_negation(self) -> None:
        text = "No further imaging recommended."
        result = check_negation(text, 0)
        assert result.is_negated
        assert result.matched_pattern == "direct_negation"

    def test_no_negation(self) -> None:
        text = "Recommend CT in 6 months."
        result = check_negation(text, 0)
        assert not result.is_negated

    def test_negation_finding(self) -> None:
        text = "No pulmonary nodule identified."
        result = check_negation(text, 0)
        assert result.is_negated
        assert result.matched_pattern == "negation_finding"

    def test_negation_context_window(self) -> None:
        text = "There is a small nodule. No follow-up CT recommended."
        result = check_negation(text, text.index("No"))
        assert result.is_negated

    def test_no_trigger_in_context(self) -> None:
        text = "This is a normal report with no issues found."
        result = check_negation(text, 30)
        assert not result.is_negated

    def test_context_window_at_boundary(self) -> None:
        text = "Short"
        result = check_negation(text, 2)
        assert not result.is_negated


class TestClassifyRecommendationType:
    def test_positive(self) -> None:
        assert classify_recommendation_type("Recommend follow-up CT") == "positive"

    def test_negative(self) -> None:
        assert classify_recommendation_type("No further imaging recommended") == "negative"

    def test_clinical_correlation(self) -> None:
        assert classify_recommendation_type("Clinical correlation is advised") == "clinical_correlation"

    def test_normal_text(self) -> None:
        assert classify_recommendation_type("Normal examination") == "positive"
