# rad-followup-auditor

[![CI](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/ci.yml)
[![Desktop/native release](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/release.yml/badge.svg)](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Extract, structure, and audit incidental finding follow-up recommendations from radiology reports.**

![rad-followup-auditor demo](docs/assets/demo.gif)

`rad-followup-auditor` examines de-identified radiology report text, identifies follow-up recommendations, and converts them into structured fields. The CLI and Streamlit dashboard support quality improvement workflows such as overdue recommendation review, wording variability analysis, and detection of missing intervals or modality mismatches.

## Quick Start

Install from source:

```bash
git clone https://github.com/AKaturu/rad-followup-auditor.git
cd rad-followup-auditor
python -m pip install -e ".[app]"
rad-followup-auditor demo --output outputs/demo --n 50 --seed 42 --no-pdf
rad-followup-auditor serve
```

Prefer a no-Python install? Download a Windows, macOS, or Linux archive from the [Releases](https://github.com/AKaturu/rad-followup-auditor/releases) page after a release build is published.

## Why It Exists

Incidental findings often include free-text recommendations such as "CT chest in 6 months" or "MRI abdomen recommended." Those recommendations can be hard to monitor across a large report corpus. This project turns report text into reviewable CSV outputs so teams can audit follow-up language, find ambiguous recommendations, and prioritize manual review.

## What It Does

- Parses free-text radiology reports for follow-up recommendations.
- Converts recommendations to structured fields: finding, modality, interval, urgency, and anatomic region.
- Detects negated recommendations such as "No follow-up needed."
- Assigns confidence levels and flags cases that need manual review.
- Generates CSV summaries and an HTML report from synthetic or de-identified report inputs.
- Provides a Streamlit dashboard for interactive review.

## CLI Commands

| Command | Description |
|---|---|
| `rad-followup-auditor demo` | Generate synthetic reports and run extraction. |
| `rad-followup-auditor extract --csv <file>` | Extract recommendations from a CSV. |
| `rad-followup-auditor report --csv <file>` | Generate an HTML report with optional PDF export. |
| `rad-followup-auditor serve` | Launch the Streamlit dashboard. |

## Input CSV Format

```csv
report_id,report_text
R001,"FINDINGS: 8 mm pulmonary nodule in the right upper lobe. IMPRESSION: Recommend CT chest in 6 months."
R002,"FINDINGS: Normal examination. IMPRESSION: No further imaging recommended."
```

## Output Fields

| Field | Meaning |
|---|---|
| `finding` | Finding requiring follow-up, such as `pulmonary nodule`. |
| `recommended_modality` | CT, MRI, ultrasound, or other recommended modality. |
| `interval_value` / `interval_unit` | Follow-up timing, such as `6 months`. |
| `urgency` | Routine, urgent, or other urgency label. |
| `anatomic_region` | Body region inferred from the recommendation. |
| `confidence` | High, medium, or low extraction confidence. |
| `review_required` | Boolean flag for manual review. |
| `is_negated` | Recommendation was negated or explicitly unnecessary. |

## Repository Guide

| Path | Purpose |
|---|---|
| `src/rad_followup_auditor/extraction/` | Rule-based extraction engine, negation handling, and patterns. |
| `src/rad_followup_auditor/cli.py` | CLI commands for demo, extract, report, and dashboard launch. |
| `src/rad_followup_auditor/app/main.py` | Streamlit dashboard. |
| `src/rad_followup_auditor/data/synthetic.py` | Synthetic radiology report generator. |
| `src/rad_followup_auditor/report/` | HTML/PDF report generation. |
| `scripts/build_native.py` | Native executable packaging helper for GitHub Actions. |
| `scripts/generate_demo_media.py` | Reproducible README media generator. |
| `tests/` | Extraction, negation, normalizer, and synthetic data tests. |

## Validation

The repository includes a deterministic 300-report synthetic benchmark corpus at
`tests/data/validation_reports.csv` and a validation runner:

```bash
python scripts/build_validation_corpus.py
python scripts/run_validation.py tests/data/validation_reports.csv outputs/validation
```

Current synthetic benchmark results:

| Metric | Value |
|---|---:|
| Reports | 300 |
| Recommendation sensitivity | 1.000 |
| Recommendation precision | 0.934 |
| Recommendation F1 | 0.966 |
| Macro field accuracy | 0.788 |
| Exact all-field match | 0.223 |

See [docs/validation/validation_report.md](docs/validation/validation_report.md) for field-level
metrics, category summaries, limitations, and next validation steps. These results are useful for
regression testing and method transparency, but they are not clinical performance claims.

## Demo Media

The README animation is generated from a real synthetic CLI demo run:

```bash
python -m pip install -e ".[media]"
python scripts/generate_demo_media.py
```

See [docs/demo-media.md](docs/demo-media.md) for details.

## Releases

The [Desktop/native release](.github/workflows/release.yml) workflow builds downloadable CLI archives for Windows, macOS, and Linux. It can be run manually from GitHub Actions, or by pushing a tag such as `v0.1.0`.

See [docs/release.md](docs/release.md) for release steps.

## Safety And Scope

This tool is intended for research, quality improvement, and workflow prototyping. It is not a medical device and should not be used as the sole source for clinical decisions. Use synthetic or properly de-identified report text unless your institution has approved a compliant local workflow.

## Publication Angle

"An open-source framework for extracting and tracking incidental finding follow-up recommendations from radiology reports."
