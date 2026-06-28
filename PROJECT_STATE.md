# PROJECT_STATE

## Project Overview

### Project Name
rad-followup-auditor

### Goal
Extract and structure incidental finding follow-up recommendations from free-text radiology reports, enabling adherence tracking, wording-variability analysis, and quality-improvement surveillance.

### Current Status
Phase 1 - MVP complete. Core extraction engine, CLI, synthetic data generator, Streamlit dashboard, HTML/PDF report generation, and test suite implemented.

---

## Completed Features

### Feature: Pattern-Based Extraction Engine
- Recommendation trigger phrase detection (recommend, suggest, follow-up, etc.)
- Negation handling (direct negation, finding negation, clinical correlation)
- Modality extraction (CT, MRI, Ultrasound, PET, etc.) with canonical mapping
- Time interval extraction and normalization (numeric and named intervals)
- Anatomic region extraction
- Urgency classification (routine, urgent)
- Confidence scoring (high/medium/low based on extracted fields)
- Review-required flagging for ambiguous or low-confidence extractions

### Feature: Synthetic Report Generator
- Generates realistic radiology report text with configurable follow-up rate
- 10 report templates with varied findings, regions, modalities, sizes, and features
- Reproducible random seed for deterministic testing

### Feature: CLI Interface
- `demo` — generate synthetic reports and run full extraction pipeline
- `extract` — process a CSV and write structured output with summary
- `report` — generate an HTML report with optional PDF export
- `serve` — launch the Streamlit dashboard

### Feature: Streamlit Dashboard
- Demo data generator tab with configurable parameters
- CSV upload tab for real report data
- Report generation tab with HTML and PDF download buttons
- Metrics display (total, with recommendations, negated, review required)
- Confidence distribution bar chart, urgency pie chart, recommendation status chart
- Extracted recommendations data table
- CSV download of full results

### Feature: Report Generation
- HTML report with stats grid, summary metrics table, and extraction details table
- PDF export via WeasyPrint with fpdf2 fallback

### Feature: Testing
- 44 tests covering extraction engine, negation handler, normalizer, and synthetic data
- Ruff linting configured and passing
- GitHub Actions CI workflow (lint, type check, test, demo smoke test)

### Feature: Project Infrastructure
- pyproject.toml with setuptools build configuration
- Dockerfile for containerized deployment
- MIT License
- README with usage documentation
- .gitignore and .github/workflows/ci.yml

---

## Current Work

### Active Feature
None.

### Progress
All requested MVP surfaces are implemented.

### Remaining Work
- Add more recommendation patterns based on real-world radiology report analysis
- Full external validation with manually annotated radiology reports
- PyPI publishing

---

## Next Actions

1. Push to GitHub and enable CI
2. Cut v0.1.0 tag
3. Publish to PyPI
4. Add packaging for native desktop builds

---

## Resume Instructions

Start with `README.md`. The extraction engine entry point is `src/rad_followup_auditor/extraction/engine.py`; CLI commands live in `src/rad_followup_auditor/cli.py`; the dashboard is `src/rad_followup_auditor/app/main.py`.

Verify with:
```bash
ruff check src/ tests/
python -m pytest
rad-followup-auditor demo --output outputs/demo --n 50 --seed 42 --no-pdf
rad-followup-auditor serve
```
