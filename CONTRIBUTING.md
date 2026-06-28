# Contributing

Thanks for helping improve rad-followup-auditor.

## Development Setup

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quality Checks

Run before opening a pull request:

```bash
python -m ruff check .
python -m pytest
```

For user-facing changes, also run:

```bash
rad-followup-auditor demo --output outputs/demo --n 50 --seed 42 --no-pdf
```

## Contribution Rules

- Do not commit PHI, credentials, institutional exports, or patient-level data.
- Use synthetic data for examples and automated tests.
- Keep the scope focused on extraction and tracking rather than clinical decision-making.
