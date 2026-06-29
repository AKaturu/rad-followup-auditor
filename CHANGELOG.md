# Changelog

## Unreleased

### Added

- Synthetic 300-report validation benchmark corpus.
- Validation runner with accuracy, precision, recall, F1, category summaries, and confusion matrix outputs.
- Validation benchmark documentation under `docs/validation/`.

### Improved

- Finding-context extraction now strips section labels and trailing recommendation phrases.

## 0.1.0 - 2026-06-28

### Added

- Pattern-based follow-up recommendation extraction from free-text radiology reports
- Negation handling (direct negation, finding negation, clinical correlation)
- Modality extraction with canonical mapping (CT, MRI, US, PET, etc.)
- Time interval extraction and normalization (numeric and named intervals)
- Anatomic region extraction and urgency classification (routine, urgent)
- Confidence scoring (high/medium/low) and review-required flagging
- Synthetic radiology report generator with 10 templates
- CLI commands (demo, extract, report, serve)
- Streamlit dashboard with interactive review and CSV download
- HTML report with optional PDF export (WeasyPrint + fpdf2 fallback)
- Native desktop release packaging (Windows, macOS, Linux)
- GitHub Actions CI (lint, type check, test, demo smoke)
- Full test suite (extraction, negation, normalizer, synthetic data)
- Reproducible README demo media generation
