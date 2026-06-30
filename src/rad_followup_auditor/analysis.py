from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import (
    COL_CONFIDENCE,
    COL_HAS_EXPLICIT_RECOMMENDATION,
    COL_INTERVAL_VALUE,
    COL_IS_NEGATED,
    COL_REVIEW_REQUIRED,
    COL_URGENCY,
    ExtractionConfig,
)
from .extraction import extract_all
from .schemas import validate_input, validate_output


@dataclass
class AnalysisOutput:
    raw: pd.DataFrame
    extracted: pd.DataFrame
    summary: pd.DataFrame
    stats: dict


def load_and_extract(
    csv_path: str | Path,
    text_column: str = "report_text",
    config: ExtractionConfig | None = None,
) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError as err:
        raise FileNotFoundError(f"CSV file not found: {csv_path}") from err
    df = validate_input(df)
    result = extract_all(df, text_column=text_column, config=config)
    return validate_output(result)


def compute_summary(extracted: pd.DataFrame) -> pd.DataFrame:
    total = len(extracted)
    if total == 0:
        return pd.DataFrame()

    with_recs = extracted[extracted[COL_HAS_EXPLICIT_RECOMMENDATION]]
    negated = extracted[extracted[COL_IS_NEGATED]]
    review = extracted[extracted[COL_REVIEW_REQUIRED]]

    rows = [
        {"metric": "Total reports", "value": total},
        {
            "metric": "Reports with recommendations",
            "value": len(with_recs),
            "pct": round(len(with_recs) / total * 100, 1) if total else 0,
        },
        {
            "metric": "Negated recommendations",
            "value": len(negated),
            "pct": round(len(negated) / total * 100, 1) if total else 0,
        },
        {
            "metric": "Review required",
            "value": len(review),
            "pct": round(len(review) / total * 100, 1) if total else 0,
        },
    ]

    if not with_recs.empty:
        high_conf = with_recs[with_recs[COL_CONFIDENCE] == "high"]
        rows.append(
            {
                "metric": "High-confidence extractions",
                "value": len(high_conf),
                "pct": (
                    round(len(high_conf) / len(with_recs) * 100, 1)
                    if len(with_recs)
                    else 0
                ),
            }
        )

        conf_counts = with_recs[COL_CONFIDENCE].value_counts()
        for level in ["high", "medium", "low"]:
            rows.append(
                {
                    "metric": f"  - {level}",
                    "value": int(conf_counts.get(level, 0)),
                }
            )

        urgency_counts = with_recs[COL_URGENCY].value_counts()
        for level in ["routine", "urgent"]:
            n_urg = int(urgency_counts.get(level, 0))
            if n_urg:
                rows.append(
                    {
                        "metric": f"Urgency: {level}",
                        "value": n_urg,
                        "pct": (
                            round(n_urg / len(with_recs) * 100, 1)
                            if len(with_recs)
                            else 0
                        ),
                    }
                )

        with_interval = with_recs[with_recs[COL_INTERVAL_VALUE].notna()]
        rows.append(
            {
                "metric": "With time interval specified",
                "value": len(with_interval),
                "pct": (
                    round(len(with_interval) / len(with_recs) * 100, 1)
                    if len(with_recs)
                    else 0
                ),
            }
        )

        no_interval = with_recs[with_recs[COL_INTERVAL_VALUE].isna()]
        rows.append(
            {
                "metric": "Missing time interval",
                "value": len(no_interval),
                "pct": (
                    round(len(no_interval) / len(with_recs) * 100, 1)
                    if len(with_recs)
                    else 0
                ),
            }
        )

        modalities = with_recs["recommended_modality"].dropna()
        top_mods = modalities.value_counts().head(5)
        for mod, cnt in top_mods.items():
            rows.append(
                {
                    "metric": f"  - Modality: {mod}",
                    "value": cnt,
                }
            )

    return pd.DataFrame(rows)


def run_analysis(
    csv_path: str | Path,
    config: ExtractionConfig | None = None,
) -> AnalysisOutput:
    extracted = load_and_extract(csv_path, config=config)
    summary = compute_summary(extracted)

    total = len(extracted)
    with_rec = int(extracted[COL_HAS_EXPLICIT_RECOMMENDATION].sum())
    negated = int(extracted[COL_IS_NEGATED].sum())
    review = int(extracted[COL_REVIEW_REQUIRED].sum())

    stats = {
        "total": total,
        "with_recommendations": with_rec,
        "negated": negated,
        "review_required": review,
        "recommendation_rate": round(with_rec / total * 100, 1) if total else 0.0,
        "negation_rate": round(negated / total * 100, 1) if total else 0.0,
    }

    filled = extracted.copy()

    return AnalysisOutput(
        raw=pd.DataFrame(),
        extracted=filled,
        summary=summary,
        stats=stats,
    )


def write_json_outputs(
    extracted: pd.DataFrame,
    summary: pd.DataFrame,
    output_dir: str | Path,
    *,
    stats: dict | None = None,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths = {
        "extracted_json": output / "extracted_results.json",
        "summary_json": output / "extraction_summary.json",
    }
    extracted.to_json(
        paths["extracted_json"],
        orient="records",
        indent=2,
        date_format="iso",
    )
    summary.to_json(
        paths["summary_json"],
        orient="records",
        indent=2,
        date_format="iso",
    )
    if stats is not None:
        paths["stats_json"] = output / "extraction_stats.json"
        paths["stats_json"].write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    return paths
