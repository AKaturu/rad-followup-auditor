from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from rad_followup_auditor.analysis import compute_summary, load_and_extract, write_json_outputs
from rad_followup_auditor.cli import app
from rad_followup_auditor.rules import load_extraction_config


def test_write_json_outputs(tmp_path: Path) -> None:
    extracted = pd.DataFrame(
        [
            {
                "report_id": "R1",
                "report_text": "Recommend CT in 6 months.",
                "has_explicit_recommendation": True,
            }
        ]
    )
    summary = pd.DataFrame([{"metric": "Total reports", "value": 1}])

    paths = write_json_outputs(extracted, summary, tmp_path, stats={"total": 1})

    assert json.loads(paths["extracted_json"].read_text(encoding="utf-8"))[0]["report_id"] == "R1"
    assert json.loads(paths["summary_json"].read_text(encoding="utf-8"))[0]["metric"] == "Total reports"
    assert json.loads(paths["stats_json"].read_text(encoding="utf-8"))["total"] == 1


def test_load_custom_rules_from_json(tmp_path: Path) -> None:
    rules = tmp_path / "rules.json"
    rules.write_text(
        json.dumps(
            {
                "recommendation_patterns": [{"label": "local", "pattern": "next CT due"}],
                "exclude_patterns": ["follow-up at oncology discretion"],
            }
        ),
        encoding="utf-8",
    )

    config = load_extraction_config(rules)

    assert config.custom_recommendation_patterns == ("next CT due",)
    assert config.exclude_patterns == ("follow-up at oncology discretion",)


def test_plain_text_exclude_rules(tmp_path: Path) -> None:
    excludes = tmp_path / "excludes.txt"
    excludes.write_text("# local suppressions\noncology discretion\n", encoding="utf-8")

    config = load_extraction_config(exclude_patterns=excludes)

    assert config.exclude_patterns == ("oncology discretion",)


def test_cli_extract_writes_json_and_uses_rules(tmp_path: Path) -> None:
    reports = tmp_path / "reports.csv"
    reports.write_text(
        "report_id,report_text\n"
        'R1,"FINDINGS: Nodule. IMPRESSION: Next CT due for surveillance."\n'
        'R2,"FINDINGS: Postoperative change. IMPRESSION: Follow-up at oncology discretion."\n',
        encoding="utf-8",
    )
    rules = tmp_path / "rules.json"
    rules.write_text(
        json.dumps(
            {
                "recommendation_patterns": ["next CT due"],
                "exclude_patterns": ["follow-up at oncology discretion"],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "out"

    result = CliRunner().invoke(
        app,
        [
            "extract",
            "--csv",
            str(reports),
            "--output",
            str(output),
            "--custom-patterns",
            str(rules),
        ],
    )

    assert result.exit_code == 0, result.output
    extracted_json = output / "extracted_results.json"
    assert extracted_json.exists()
    rows = json.loads(extracted_json.read_text(encoding="utf-8"))
    assert rows[0]["has_explicit_recommendation"]
    assert not rows[1]["has_explicit_recommendation"]


def test_load_and_extract_with_text_exclude(tmp_path: Path) -> None:
    reports = tmp_path / "reports.csv"
    reports.write_text(
        "report_id,report_text\n"
        'R1,"IMPRESSION: Follow-up at oncology discretion."\n',
        encoding="utf-8",
    )
    excludes = tmp_path / "excludes.txt"
    excludes.write_text("oncology discretion\n", encoding="utf-8")

    config = load_extraction_config(exclude_patterns=excludes)
    extracted = load_and_extract(reports, config=config)
    summary = compute_summary(extracted)

    assert not extracted.iloc[0]["has_explicit_recommendation"]
    assert summary.loc[summary["metric"] == "Reports with recommendations", "value"].iloc[0] == 0
