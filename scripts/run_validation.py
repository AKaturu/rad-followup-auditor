"""Run extraction against an annotated corpus and compute validation metrics."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rad_followup_auditor.config import (
    COL_ANATOMIC_REGION,
    COL_FINDING,
    COL_HAS_EXPLICIT_RECOMMENDATION,
    COL_INTERVAL_UNIT,
    COL_INTERVAL_VALUE,
    COL_IS_NEGATED,
    COL_RECOMMENDED_MODALITY,
    COL_REPORT_ID,
    COL_REPORT_TEXT,
    COL_REVIEW_REQUIRED,
    COL_URGENCY,
)
from rad_followup_auditor.extraction import extract_all

FIELD_MAP: dict[str, str] = {
    "finding": COL_FINDING,
    "recommended_modality": COL_RECOMMENDED_MODALITY,
    "interval_value": COL_INTERVAL_VALUE,
    "interval_unit": COL_INTERVAL_UNIT,
    "urgency": COL_URGENCY,
    "anatomic_region": COL_ANATOMIC_REGION,
    "has_explicit_recommendation": COL_HAS_EXPLICIT_RECOMMENDATION,
    "is_negated": COL_IS_NEGATED,
    "review_required": COL_REVIEW_REQUIRED,
}


def run_validation(corpus_path: Path, output_dir: Path) -> dict[str, Any]:
    annotations = pd.read_csv(corpus_path, dtype=str, keep_default_na=False)
    extracted = extract_all(annotations[[COL_REPORT_ID, COL_REPORT_TEXT]])
    joined = annotations.merge(
        extracted,
        on=[COL_REPORT_ID, COL_REPORT_TEXT],
        how="left",
        validate="one_to_one",
    )
    results = _build_result_rows(joined)
    metrics = _build_metrics(results)
    by_category = _build_category_metrics(results)
    confusion = _confusion_matrix(
        results["gold_has_explicit_recommendation_bool"],
        results["pred_has_explicit_recommendation_bool"],
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_dir / "validation_results.csv", index=False)
    by_category.to_csv(output_dir / "metrics_by_category.csv", index=False)
    confusion.to_csv(output_dir / "recommendation_confusion_matrix.csv", index=False)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "validation_report.md").write_text(
        render_markdown_report(metrics, by_category, confusion),
        encoding="utf-8",
    )
    return metrics


def render_markdown_report(
    metrics: dict[str, Any],
    by_category: pd.DataFrame,
    confusion: pd.DataFrame,
) -> str:
    lines = [
        "# Validation Benchmark Report",
        "",
        "## Scope",
        "",
        (
            "This report summarizes a deterministic synthetic benchmark corpus. "
            "It is useful for regression testing and method transparency, but it "
            "does not replace a human-adjudicated clinical validation study."
        ),
        "",
        "## Overall Metrics",
        "",
        f"- Reports: {metrics['n_reports']}",
        f"- Exact all-field match: {metrics['exact_all_fields_rate']:.3f}",
        f"- Recommendation sensitivity: {metrics['recommendation_detection']['recall']:.3f}",
        f"- Recommendation precision: {metrics['recommendation_detection']['precision']:.3f}",
        f"- Recommendation F1: {metrics['recommendation_detection']['f1']:.3f}",
        "",
        "## Field Metrics",
        "",
        "| Field | Accuracy | Precision | Recall | F1 | Support |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for field, payload in metrics["fields"].items():
        lines.append(
            "| "
            f"{field} | {payload['accuracy']:.3f} | {payload['precision']:.3f} | "
            f"{payload['recall']:.3f} | {payload['f1']:.3f} | {payload['support']} |"
        )
    lines.extend(["", "## Category Breakdown", ""])
    lines.append("| Category | Reports | Exact Match | Recommendation F1 |")
    lines.append("|---|---:|---:|---:|")
    for row in by_category.itertuples(index=False):
        lines.append(
            f"| {row.category} | {row.n_reports} | {row.exact_all_fields_rate:.3f} | "
            f"{row.recommendation_f1:.3f} |"
        )
    lines.extend(["", "## Recommendation Confusion Matrix", ""])
    lines.append("| Gold | Predicted | Count |")
    lines.append("|---|---|---:|")
    for row in confusion.itertuples(index=False):
        lines.append(f"| {row.gold} | {row.predicted} | {row.count} |")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- The checked-in corpus is synthetic and cannot support clinical performance claims.",
            "- The current engine extracts one primary recommendation per report.",
            "- Finding matching is strict string matching against a normalized context phrase.",
            "- External validation should use de-identified reports with independent human review.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_result_rows(frame: pd.DataFrame) -> pd.DataFrame:
    results = frame[[COL_REPORT_ID, "category", COL_REPORT_TEXT]].copy()
    match_columns: list[str] = []
    for gold_field, prediction_field in FIELD_MAP.items():
        gold_column = f"gold_{gold_field}"
        pred_column = f"pred_{gold_field}"
        match_column = f"{gold_field}_match"
        results[gold_column] = frame[gold_column].map(
            lambda value, field=gold_field: _normalize_value(value, field)
        )
        results[pred_column] = frame[prediction_field].map(
            lambda value, field=gold_field: _normalize_value(value, field)
        )
        results[match_column] = results[gold_column] == results[pred_column]
        match_columns.append(match_column)

    for field in ["has_explicit_recommendation", "is_negated", "review_required"]:
        results[f"gold_{field}_bool"] = results[f"gold_{field}"].map(_to_bool)
        results[f"pred_{field}_bool"] = results[f"pred_{field}"].map(_to_bool)

    results["exact_all_fields_match"] = results[match_columns].all(axis=1)
    return results


def _build_metrics(results: pd.DataFrame) -> dict[str, Any]:
    match_columns = [column for column in results.columns if column.endswith("_match")]
    metrics: dict[str, Any] = {
        "n_reports": len(results),
        "exact_all_fields": int(results["exact_all_fields_match"].sum()),
        "exact_all_fields_rate": float(results["exact_all_fields_match"].mean()),
        "recommendation_detection": _binary_metrics(
            results["gold_has_explicit_recommendation_bool"],
            results["pred_has_explicit_recommendation_bool"],
        ),
        "fields": {},
    }
    for field in FIELD_MAP:
        gold = results[f"gold_{field}"]
        pred = results[f"pred_{field}"]
        match = results[f"{field}_match"]
        metrics["fields"][field] = {
            "accuracy": float(match.mean()),
            "support": int(gold.astype(str).str.len().gt(0).sum()),
            **_exact_value_metrics(gold, pred),
        }
    metrics["macro_field_accuracy"] = float(results[match_columns].mean().mean())
    return metrics


def _build_category_metrics(results: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for category, group in results.groupby("category", dropna=False):
        rec_metrics = _binary_metrics(
            group["gold_has_explicit_recommendation_bool"],
            group["pred_has_explicit_recommendation_bool"],
        )
        rows.append(
            {
                "category": category,
                "n_reports": len(group),
                "exact_all_fields_rate": float(group["exact_all_fields_match"].mean()),
                "recommendation_precision": rec_metrics["precision"],
                "recommendation_recall": rec_metrics["recall"],
                "recommendation_f1": rec_metrics["f1"],
            }
        )
    return pd.DataFrame(rows).sort_values("category").reset_index(drop=True)


def _binary_metrics(gold: Iterable[bool], pred: Iterable[bool]) -> dict[str, Any]:
    gold_list = list(gold)
    pred_list = list(pred)
    tp = sum(1 for g, p in zip(gold_list, pred_list, strict=True) if g and p)
    fp = sum(1 for g, p in zip(gold_list, pred_list, strict=True) if not g and p)
    fn = sum(1 for g, p in zip(gold_list, pred_list, strict=True) if g and not p)
    tn = sum(1 for g, p in zip(gold_list, pred_list, strict=True) if not g and not p)
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    return {
        "true_positive": int(tp),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_negative": int(tn),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def _exact_value_metrics(gold: pd.Series, pred: pd.Series) -> dict[str, float]:
    gold_positive = gold.astype(str).str.len().gt(0)
    pred_positive = pred.astype(str).str.len().gt(0)
    exact_positive = gold_positive & pred_positive & gold.eq(pred)
    precision = _safe_div(int(exact_positive.sum()), int(pred_positive.sum()))
    recall = _safe_div(int(exact_positive.sum()), int(gold_positive.sum()))
    f1 = _safe_div(2 * precision * recall, precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def _confusion_matrix(gold: pd.Series, pred: pd.Series) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for gold_value in [False, True]:
        for pred_value in [False, True]:
            rows.append(
                {
                    "gold": str(gold_value).lower(),
                    "predicted": str(pred_value).lower(),
                    "count": int(((gold == gold_value) & (pred == pred_value)).sum()),
                }
            )
    return pd.DataFrame(rows)


def _normalize_value(value: Any, field: str) -> str:
    if pd.isna(value):
        return ""
    raw = str(value).strip()
    if raw.lower() in {"nan", "none", "nat"}:
        return ""
    if field == "interval_value" and raw:
        try:
            number = float(raw)
        except ValueError:
            return raw
        return str(int(number)) if number.is_integer() else str(number)
    if field in {"has_explicit_recommendation", "is_negated", "review_required"}:
        return str(_to_bool(raw)).lower()
    return " ".join(raw.lower().split())


def _to_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _safe_div(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2:
        print("Usage: python scripts/run_validation.py <corpus.csv> <output_dir>", file=sys.stderr)
        return 2
    metrics = run_validation(Path(args[0]), Path(args[1]))
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
