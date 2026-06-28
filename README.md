# rad-followup-auditor

[![CI](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Extract and track incidental finding follow-up recommendations from radiology reports.**

`rad-followup-auditor` examines de-identified radiology report text, identifies follow-up recommendations, and converts them into structured fields. The dashboard and CLI enable tracking overdue recommendations, analyzing wording variability, and detecting missing intervals or modality inconsistencies.

## Quick Start

```bash
pip install rad-followup-auditor
rad-followup-auditor demo
rad-followup-auditor serve
```

## What It Does

- Parses free-text radiology reports for follow-up recommendations
- Converts recommendations to structured fields: finding, modality, interval, urgency, anatomic region
- Detects negation ("No follow-up needed"), clinical correlation, and ambiguous language
- Assigns confidence levels (high/medium/low) and flags items needing review
- Generates summary dashboards with recommendation rates, modality breakdowns, and urgency distributions
- Exports structured CSV results and HTML/PDF reports

## Repository Guide

| Path | Purpose |
|---|---|
| `src/rad_followup_auditor/extraction/` | Rule-based extraction engine, negation handling, pattern definitions |
| `src/rad_followup_auditor/cli.py` | CLI commands for demo, extract, report, and dashboard |
| `src/rad_followup_auditor/analysis.py` | Analysis pipeline |
| `src/rad_followup_auditor/app/main.py` | Streamlit dashboard |
| `src/rad_followup_auditor/data/synthetic.py` | Synthetic radiology report generator |
| `src/rad_followup_auditor/report/` | HTML/PDF report generation |
| `tests/` | Extraction, negation, normalizer, and synthetic data tests |

## CLI Commands

| Command | Description |
|---|---|
| `rad-followup-auditor demo` | Generate synthetic reports and run extraction |
| `rad-followup-auditor extract --csv <file>` | Extract recommendations from a CSV |
| `rad-followup-auditor report --csv <file>` | Generate HTML report with optional PDF |
| `rad-followup-auditor serve` | Launch the Streamlit dashboard |

## Input CSV Format

```csv
report_id,report_text
R001,"FINDINGS: 8 mm pulmonary nodule in the right upper lobe. IMPRESSION: Recommend CT chest in 6 months."
R002,"FINDINGS: Normal examination. IMPRESSION: No further imaging recommended."
```

## Output Fields

- `finding` — the finding requiring follow-up (e.g., "pulmonary nodule")
- `recommended_modality` — CT, MRI, Ultrasound, etc.
- `interval_value` / `interval_unit` — e.g., 6 months
- `urgency` — routine or urgent
- `anatomic_region` — body part
- `confidence` — high, medium, or low
- `review_required` — flagged for manual review
- `is_negated` — recommendation was negated

## Publication Angle

"An open-source framework for extracting and tracking incidental finding follow-up recommendations from radiology reports."
