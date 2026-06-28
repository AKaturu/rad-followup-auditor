from __future__ import annotations

from pathlib import Path

from rad_followup_auditor.data.synthetic import generate_reports, write_synthetic_csv


class TestGenerateReports:
    def test_default_count(self) -> None:
        reports = generate_reports(seed=42)
        assert len(reports) == 100

    def test_custom_count(self) -> None:
        reports = generate_reports(n=50, seed=1)
        assert len(reports) == 50

    def test_reproducible_seed(self) -> None:
        r1 = generate_reports(n=10, seed=42)
        r2 = generate_reports(n=10, seed=42)
        assert r1 == r2

    def test_different_seeds(self) -> None:
        r1 = generate_reports(n=10, seed=42)
        r2 = generate_reports(n=10, seed=99)
        assert r1 != r2

    def test_has_report_id(self) -> None:
        reports = generate_reports(n=5, seed=42)
        for r in reports:
            assert "report_id" in r
            assert r["report_id"].startswith("SYNTH-")

    def test_has_report_text(self) -> None:
        reports = generate_reports(n=5, seed=42)
        for r in reports:
            assert "report_text" in r
            assert len(r["report_text"]) > 0

    def test_followup_rate_zero(self) -> None:
        reports = generate_reports(n=50, seed=42, followup_rate=0.0)
        texts = [r["report_text"] for r in reports]
        assert not any("Recommend" in t for t in texts)

    def test_followup_rate_one(self) -> None:
        reports = generate_reports(n=50, seed=42, followup_rate=1.0)
        texts = [r["report_text"] for r in reports]
        assert any("Recommend" in t or "Follow-up" in t or "Suggest" in t for t in texts)


class TestWriteSyntheticCSV:
    def test_writes_csv(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "test_reports.csv"
        reports = write_synthetic_csv(csv_path, n=10, seed=42)
        assert csv_path.exists()
        assert len(reports) == 10

    def test_csv_content(self, tmp_path: Path) -> None:
        import csv

        csv_path = tmp_path / "test_reports.csv"
        write_synthetic_csv(csv_path, n=5, seed=42)
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 5
        assert "report_id" in rows[0]
        assert "report_text" in rows[0]
