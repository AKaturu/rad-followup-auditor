from __future__ import annotations

import pandas as pd
import pandera.pandas as pa

from .config import (
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
    CONFIDENCE_LEVELS,
    INTERVAL_UNITS,
    URGENCY_LEVELS,
)


def _build_input_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        {
            COL_REPORT_ID: pa.Column(str, nullable=False, required=True, coerce=True),
            COL_REPORT_TEXT: pa.Column(str, nullable=False, required=True, coerce=True),
            COL_STUDY_DATE: pa.Column(
                "datetime64[ns]", nullable=True, required=False, coerce=True
            ),
            COL_MODALITY: pa.Column(str, nullable=True, required=False, coerce=True),
            COL_ACCESSION: pa.Column(str, nullable=True, required=False, coerce=True),
        },
        coerce=True,
        strict=False,
        add_missing_columns=False,
    )


def _build_output_schema() -> pa.DataFrameSchema:
    return pa.DataFrameSchema(
        {
            COL_REPORT_ID: pa.Column(str, nullable=False, required=True),
            COL_REPORT_TEXT: pa.Column(str, nullable=False, required=True),
            COL_FINDING: pa.Column(str, nullable=True, required=False),
            COL_RECOMMENDED_MODALITY: pa.Column(str, nullable=True, required=False),
            COL_INTERVAL_VALUE: pa.Column(float, nullable=True, required=False),
            COL_INTERVAL_UNIT: pa.Column(
                str,
                nullable=True,
                required=False,
                checks=pa.Check.isin([*list(INTERVAL_UNITS), None]) if INTERVAL_UNITS else None,
            ),
            COL_URGENCY: pa.Column(
                str,
                nullable=True,
                required=False,
                checks=pa.Check.isin([*list(URGENCY_LEVELS), None]) if URGENCY_LEVELS else None,
            ),
            COL_ANATOMIC_REGION: pa.Column(str, nullable=True, required=False),
            COL_HAS_EXPLICIT_RECOMMENDATION: pa.Column(bool, nullable=False, required=True),
            COL_RECOMMENDATION_TEXT: pa.Column(str, nullable=True, required=False),
            COL_CONFIDENCE: pa.Column(
                str,
                nullable=False,
                required=True,
                checks=pa.Check.isin(CONFIDENCE_LEVELS),
            ),
            COL_IS_NEGATED: pa.Column(bool, nullable=False, required=True),
            COL_REVIEW_REQUIRED: pa.Column(bool, nullable=False, required=True),
            COL_NEGATION_CONTEXT: pa.Column(str, nullable=True, required=False),
        },
        coerce=True,
        strict=False,
        add_missing_columns=False,
    )


INPUT_SCHEMA: pa.DataFrameSchema = _build_input_schema()
OUTPUT_SCHEMA: pa.DataFrameSchema = _build_output_schema()


def validate_input(df: pd.DataFrame) -> pd.DataFrame:
    return INPUT_SCHEMA.validate(df, lazy=True)


def validate_output(df: pd.DataFrame) -> pd.DataFrame:
    return OUTPUT_SCHEMA.validate(df, lazy=True)
