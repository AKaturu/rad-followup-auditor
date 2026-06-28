from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import pandas as pd

from ..config import (
    COL_ACCESSION,
    COL_ANATOMIC_REGION,
    COL_CONFIDENCE,
    COL_FINDING,
    COL_HAS_EXPLICIT_RECOMMENDATION,
    COL_INTERVAL_UNIT,
    COL_INTERVAL_VALUE,
    COL_IS_NEGATED,
    COL_MODALITY,
    COL_NEGATION_CONTEXT,
    COL_RECOMMENDATION_TEXT,
    COL_RECOMMENDED_MODALITY,
    COL_REPORT_ID,
    COL_REPORT_TEXT,
    COL_REVIEW_REQUIRED,
    COL_STUDY_DATE,
    COL_URGENCY,
    DEFAULT_CONFIG,
    MODALITIES,
    OUTPUT_COLUMNS,
    ExtractionConfig,
)
from .negation import NegationResult, check_negation, classify_recommendation_type
from .normalizer import (
    extract_anatomic_region,
    extract_interval,
    extract_modality,
    normalize_finding,
)
from .patterns import RECOMMENDATION_PATTERNS, URGENCY_PATTERNS


@dataclass
class ExtractionResult:
    report_id: str
    report_text: str
    finding: str | None = None
    recommended_modality: str | None = None
    interval_value: float | None = None
    interval_unit: str | None = None
    urgency: str | None = None
    anatomic_region: str | None = None
    has_explicit_recommendation: bool = False
    recommendation_text: str | None = None
    confidence: str = "low"
    is_negated: bool = False
    review_required: bool = False
    negation_context: str | None = None
    study_date: Any = None
    modality: str | None = None
    accession: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            COL_REPORT_ID: self.report_id,
            COL_REPORT_TEXT: self.report_text,
            COL_FINDING: self.finding,
            COL_RECOMMENDED_MODALITY: self.recommended_modality,
            COL_INTERVAL_VALUE: self.interval_value,
            COL_INTERVAL_UNIT: self.interval_unit,
            COL_URGENCY: self.urgency,
            COL_ANATOMIC_REGION: self.anatomic_region,
            COL_HAS_EXPLICIT_RECOMMENDATION: self.has_explicit_recommendation,
            COL_RECOMMENDATION_TEXT: self.recommendation_text,
            COL_CONFIDENCE: self.confidence,
            COL_IS_NEGATED: self.is_negated,
            COL_REVIEW_REQUIRED: self.review_required,
            COL_NEGATION_CONTEXT: self.negation_context,
        }


class ExtractionEngine:
    def __init__(self, config: ExtractionConfig | None = None):
        self.config = config or DEFAULT_CONFIG
        self._compiled_modalities = self._build_modality_regex()

    def _build_modality_regex(self) -> re.Pattern:
        terms = sorted(MODALITIES.keys(), key=len, reverse=True)
        return re.compile(
            r"\b(?:" + "|".join(re.escape(t) for t in terms) + r")\b",
            re.IGNORECASE,
        )

    def _extract_modality(self, text: str) -> str | None:
        match = self._compiled_modalities.search(text)
        if match:
            raw = match.group(0).lower()
            return MODALITIES.get(raw, raw)
        return extract_modality(text)

    def _extract_finding_context(self, text: str, match_start: int) -> str:
        before = text[max(0, match_start - 75) : match_start]
        sentences = re.split(r"[.!?\n]+", before)
        finding = sentences[-1].strip() if sentences else ""
        return normalize_finding(finding) if finding else ""

    def extract_report(self, text: str, report_id: str = "") -> ExtractionResult:
        result = ExtractionResult(report_id=report_id, report_text=text)

        if not text or not isinstance(text, str) or not text.strip():
            result.is_negated = False
            result.has_explicit_recommendation = False
            result.review_required = True
            result.confidence = "low"
            result.negation_context = "empty_report"
            return result

        rec_type = classify_recommendation_type(text)

        if rec_type == "negative":
            neg_result = self._find_negation(text)
            result.is_negated = True
            result.negation_context = neg_result.matched_text
            result.has_explicit_recommendation = False
            result.confidence = "high"
            return result

        best_rec_text = None
        best_rec_start = -1
        best_score = 0.0

        for pat_def in RECOMMENDATION_PATTERNS:
            for match in pat_def["pattern"].finditer(text):
                matched = match.group()
                start = match.start()
                score = pat_def["weight"]
                if score > best_score:
                    best_score = score
                    best_rec_text = matched
                    best_rec_start = start

        if best_rec_text is None:
            if rec_type == "clinical_correlation":
                result.has_explicit_recommendation = False
                result.review_required = True
                result.confidence = "medium"
                result.negation_context = "clinical_correlation_only"
            else:
                result.has_explicit_recommendation = False
                result.review_required = True
                result.confidence = "low"
            return result

        result.has_explicit_recommendation = True

        rec_end = best_rec_start + len(best_rec_text)
        window_start = max(0, best_rec_start - 75)
        window_end = min(len(text), rec_end + 100)
        rec_window = text[window_start:window_end]

        result.recommendation_text = best_rec_text

        result.finding = self._extract_finding_context(text, best_rec_start)

        result.recommended_modality = self._extract_modality(rec_window)
        if result.recommended_modality:
            canonical = MODALITIES.get(result.recommended_modality)
            if canonical:
                result.recommended_modality = canonical

        interval_val, interval_unit = extract_interval(rec_window)
        if (
            interval_val is not None
            and self.config.min_interval_value <= interval_val <= self.config.max_interval_value
        ):
            result.interval_value = interval_val
            result.interval_unit = interval_unit

        result.anatomic_region = extract_anatomic_region(rec_window)

        for upat in URGENCY_PATTERNS:
            if upat["pattern"].search(rec_window):
                result.urgency = upat["level"]
                break

        neg_result = check_negation(
            text, best_rec_start, self.config.negation_radius_chars
        )
        result.is_negated = neg_result.is_negated
        result.negation_context = neg_result.matched_text

        if rec_type == "clinical_correlation":
            result.confidence = "medium"
            result.review_required = True
        elif result.is_negated or (result.recommended_modality and result.interval_value is not None):
            result.confidence = "high"
        elif result.recommended_modality:
            result.confidence = "medium"
        else:
            result.confidence = "low"

        if rec_type != "clinical_correlation":
            result.review_required = (
                result.confidence == "low"
                or (result.is_negated and result.interval_value is not None)
            )

        return result

    def _find_negation(self, text: str) -> NegationResult:
        from .negation import check_negation as cn

        return cn(text, -1, self.config.negation_radius_chars)

    def extract_dataframe(
        self, df: pd.DataFrame, text_column: str = COL_REPORT_TEXT
    ) -> pd.DataFrame:
        rows = []
        for _, row in df.iterrows():
            text = str(row.get(text_column, ""))
            report_id = str(row.get(COL_REPORT_ID, ""))
            result = self.extract_report(text, report_id=report_id)
            d = result.to_dict()
            if COL_STUDY_DATE in df.columns:
                d[COL_STUDY_DATE] = row.get(COL_STUDY_DATE)
            if COL_MODALITY in df.columns:
                d[COL_MODALITY] = row.get(COL_MODALITY)
            if COL_ACCESSION in df.columns:
                d[COL_ACCESSION] = row.get(COL_ACCESSION)
            rows.append(d)
        return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def extract_all(
    df: pd.DataFrame,
    text_column: str = COL_REPORT_TEXT,
    config: ExtractionConfig | None = None,
) -> pd.DataFrame:
    engine = ExtractionEngine(config=config)
    return engine.extract_dataframe(df, text_column=text_column)
