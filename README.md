# rad-followup-auditor

[![CI](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/ci.yml)
[![Desktop/native release](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/release.yml/badge.svg)](https://github.com/AKaturu/rad-followup-auditor/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Extract, structure, and audit incidental finding follow-up recommendations from radiology reports.**

![rad-followup-auditor demo](docs/assets/demo.gif)

Incidental findings often include free-text recommendations such as "CT chest in 6 months" or "MRI abdomen recommended." Those recommendations can be hard to monitor across a large report corpus. This project turns report text into reviewable CSV outputs so teams can audit follow-up language, find ambiguous recommendations, and prioritize manual review.

**Validation status:** Software functionality has been tested using synthetic or public data as described below. This project has not undergone prospective clinical validation and is not intended for independent clinical decision-making.

| Evidence | Status |
|---|---|
| Unit tests | Complete (44 tests) |
| Synthetic end-to-end test | Complete |
| Public-data evaluation | Not completed |
| Expert review | Not completed |
| Institutional validation | Not completed |
| Prospective clinical validation | Not completed |

## Capabilities

- Parses free-text radiology reports for follow-up recommendations
- Converts recommendations to structured fields: finding, modality, interval, urgency, anatomic region
- Detects negated recommendations ("No follow-up needed")
- Assigns confidence levels and flags cases needing manual review
- Generates CSV summaries and HTML reports with optional PDF export
- Streamlit dashboard for interactive review

## Quick Start

```bash
pip install -e ".[app]"
rad-followup-auditor demo --output outputs/demo --n 50 --seed 42 --no-pdf
rad-followup-auditor serve
```

## Limitations

- This tool is for research, quality improvement, and workflow prototyping
- It is not a medical device and should not be used as the sole source for clinical decisions
- Use synthetic or properly de-identified report text unless your institution has approved a compliant local workflow

## Documentation

| Topic | File |
|---|---|
| Release steps | [docs/release.md](docs/release.md) |
| Demo media generation | [docs/demo-media.md](docs/demo-media.md) |
| Input CSV format and output fields | [README.md](README.md) (Input CSV Format section) |
| Contribution guide | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security reporting | [SECURITY.md](SECURITY.md) |

## License

MIT. See [LICENSE](LICENSE).
