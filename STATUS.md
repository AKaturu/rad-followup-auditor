# Status

## Current Release
**v0.1.0** (2026-06-28) — MVP release.

## Implemented Features
- Pattern-based follow-up recommendation extraction from free-text radiology reports
- Negation handling (direct negation, finding negation, clinical correlation)
- Modality extraction with canonical mapping (CT, MRI, US, PET, etc.)
- Time interval extraction and normalization (numeric and named intervals)
- Anatomic region extraction, urgency classification (routine, urgent)
- Confidence scoring (high/medium/low) and review-required flagging
- Synthetic radiology report generator with 10 templates and configurable follow-up rate
- CLI commands: demo, extract, report, serve
- Streamlit dashboard with interactive review, filters, and CSV download
- HTML report with optional PDF export (WeasyPrint + fpdf2 fallback)
- Native desktop release packaging (Windows, macOS, Linux)

## Validation Status
- **Unit tests**: 44 passed (extraction engine, negation handler, normalizer, synthetic data)
- **Synthetic end-to-end test**: Complete (demo generates synthetic reports, runs extraction, produces report)
- **Public-data evaluation**: Not completed
- **Expert review**: Not completed
- **Institutional validation**: Not completed
- **Prospective clinical validation**: Not completed

## Planned Work
- Expand recommendation patterns based on real-world radiology report analysis
- External validation with manually annotated radiology reports
- Configurable synonym dictionaries and custom pattern definitions
- PyPI publishing
