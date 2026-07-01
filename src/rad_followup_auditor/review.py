"""Human-review templates and inter-rater agreement metrics."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from .config import COL_HAS_EXPLICIT_RECOMMENDATION, COL_REPORT_ID, COL_REPORT_TEXT, COL_URGENCY

REVIEW_COLUMNS: tuple[str, ...] = (
    COL_REPORT_ID,
    COL_REPORT_TEXT,
    "predicted_has_followup",
    "predicted_urgency",
    "reviewer_id",
    "has_followup",
    "urgency",
    "interval_present",
    "notes",
)
DEFAULT_LABEL_COLUMNS: tuple[str, ...] = ("has_followup", "urgency", "interval_present")


def write_review_template(
    extracted_csv: str | Path,
    output_csv: str | Path,
    *,
    reviewer_id: str = "",
) -> Path:
    """Write a reviewer-label template from extraction output."""
    source = Path(extracted_csv)
    destination = Path(output_csv)
    frame = pd.read_csv(source).fillna("")
    required = {COL_REPORT_ID, COL_REPORT_TEXT}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"extracted CSV missing required columns: {', '.join(sorted(missing))}")

    template = pd.DataFrame()
    template[COL_REPORT_ID] = frame[COL_REPORT_ID].astype(str)
    template[COL_REPORT_TEXT] = frame[COL_REPORT_TEXT].astype(str)
    template["predicted_has_followup"] = (
        frame[COL_HAS_EXPLICIT_RECOMMENDATION].astype(str)
        if COL_HAS_EXPLICIT_RECOMMENDATION in frame.columns
        else ""
    )
    template["predicted_urgency"] = frame[COL_URGENCY].astype(str) if COL_URGENCY in frame.columns else ""
    template["reviewer_id"] = reviewer_id
    template["has_followup"] = ""
    template["urgency"] = ""
    template["interval_present"] = ""
    template["notes"] = ""

    destination.parent.mkdir(parents=True, exist_ok=True)
    template.to_csv(destination, index=False, columns=REVIEW_COLUMNS)
    return destination


def cohen_kappa(labels_a: list[str], labels_b: list[str]) -> dict[str, Any]:
    """Compute Cohen's kappa for two equal-length label lists."""
    if len(labels_a) != len(labels_b):
        raise ValueError("label lists must have equal length")
    if not labels_a:
        return {
            "n": 0,
            "observed_agreement": None,
            "expected_agreement": None,
            "kappa": None,
        }

    n = len(labels_a)
    observed = sum(a == b for a, b in zip(labels_a, labels_b, strict=True)) / n
    count_a = Counter(labels_a)
    count_b = Counter(labels_b)
    labels = set(count_a) | set(count_b)
    expected = sum((count_a[label] / n) * (count_b[label] / n) for label in labels)
    kappa = 1.0 if expected == 1.0 and observed == 1.0 else (observed - expected) / (1 - expected)
    return {
        "n": n,
        "observed_agreement": observed,
        "expected_agreement": expected,
        "kappa": kappa,
    }


def reviewer_agreement(
    reviewer_a_csv: str | Path,
    reviewer_b_csv: str | Path,
    output_json: str | Path,
    *,
    label_columns: tuple[str, ...] = DEFAULT_LABEL_COLUMNS,
) -> dict[str, Any]:
    """Compare two reviewer-label CSVs by report_id and write agreement metrics."""
    left = _load_review_labels(Path(reviewer_a_csv), label_columns)
    right = _load_review_labels(Path(reviewer_b_csv), label_columns)
    left_ids, right_ids = set(left), set(right)
    if left_ids != right_ids:
        missing_left = sorted(right_ids - left_ids)
        missing_right = sorted(left_ids - right_ids)
        raise ValueError(
            "reviewer files must contain the same report_id set; "
            f"missing_from_a={missing_left[:5]}, missing_from_b={missing_right[:5]}"
        )

    ordered_ids = sorted(left_ids)
    fields: dict[str, Any] = {}
    for column in label_columns:
        labels_a = [left[report_id][column] for report_id in ordered_ids]
        labels_b = [right[report_id][column] for report_id in ordered_ids]
        agreement = cohen_kappa(labels_a, labels_b)
        agreement["confusion"] = _confusion(labels_a, labels_b)
        fields[column] = agreement

    payload = {
        "schema_version": 1,
        "reviewer_a": Path(reviewer_a_csv).name,
        "reviewer_b": Path(reviewer_b_csv).name,
        "report_count": len(ordered_ids),
        "label_columns": list(label_columns),
        "fields": fields,
    }
    destination = Path(output_json)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def _load_review_labels(path: Path, label_columns: tuple[str, ...]) -> dict[str, dict[str, str]]:
    frame = pd.read_csv(path).fillna("")
    required = {COL_REPORT_ID, *label_columns}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"review CSV missing required columns: {', '.join(sorted(missing))}")
    if frame[COL_REPORT_ID].astype(str).duplicated().any():
        raise ValueError("review CSV contains duplicate report_id values")
    rows: dict[str, dict[str, str]] = {}
    for row in frame.to_dict(orient="records"):
        report_id = str(row[COL_REPORT_ID]).strip()
        if not report_id:
            raise ValueError("review CSV contains a blank report_id")
        rows[report_id] = {column: _normalize_label(row[column]) for column in label_columns}
    return rows


def _normalize_label(value: Any) -> str:
    text = str(value).strip().lower()
    return text if text else "<blank>"


def _confusion(labels_a: list[str], labels_b: list[str]) -> list[dict[str, Any]]:
    counts = Counter(zip(labels_a, labels_b, strict=True))
    return [
        {"reviewer_a": a, "reviewer_b": b, "count": count}
        for (a, b), count in sorted(counts.items())
    ]
