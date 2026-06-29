from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN_VALIDATION = ROOT / "scripts" / "run_validation.py"


def _load_run_validation_module():
    spec = importlib.util.spec_from_file_location("run_validation", RUN_VALIDATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validation_corpus_has_expected_size_and_categories() -> None:
    corpus = pd.read_csv(ROOT / "tests" / "data" / "validation_reports.csv")

    assert len(corpus) == 300
    assert set(corpus["category"]) == {
        "false_positive_clinical",
        "multiple_recommendations",
        "negated_recommendation",
        "single_recommendation",
        "typo_unconventional",
        "urgent_language",
        "vague_interval",
    }


def test_run_validation_writes_metrics(tmp_path: Path) -> None:
    module = _load_run_validation_module()
    corpus = ROOT / "tests" / "data" / "validation_reports.csv"

    metrics = module.run_validation(corpus, tmp_path)

    assert metrics["n_reports"] == 300
    assert metrics["recommendation_detection"]["recall"] >= 0.95
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "validation_results.csv").exists()
    assert (tmp_path / "metrics_by_category.csv").exists()
    assert (tmp_path / "recommendation_confusion_matrix.csv").exists()
    assert (tmp_path / "validation_report.md").exists()
