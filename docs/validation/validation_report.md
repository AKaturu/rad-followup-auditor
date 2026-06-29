# Validation Benchmark Report

## Scope

This report summarizes a deterministic 300-report synthetic benchmark corpus checked in at
`tests/data/validation_reports.csv`. It is useful for regression testing, method transparency,
and reviewer signoff on expected extraction behavior. It does not replace a human-adjudicated
clinical validation study.

The corpus includes single recommendations, multiple recommendations, negated recommendations,
vague intervals, urgent language, unconventional phrasing, and clinical-only false-positive
patterns. Annotation columns include two synthetic review labels and a consensus status so the
file has the same shape expected for a future two-reviewer clinical corpus.

## Reproduce

```bash
python scripts/build_validation_corpus.py
python scripts/run_validation.py tests/data/validation_reports.csv outputs/validation
```

## Overall Metrics

- Reports: 300
- Exact all-field match: 0.223
- Recommendation sensitivity: 1.000
- Recommendation precision: 0.934
- Recommendation F1: 0.966
- Macro field accuracy: 0.788

## Field Metrics

| Field | Accuracy | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|---:|
| finding | 0.753 | 0.711 | 0.762 | 0.735 | 239 |
| recommended_modality | 1.000 | 1.000 | 1.000 | 1.000 | 239 |
| interval_value | 1.000 | 1.000 | 1.000 | 1.000 | 199 |
| interval_unit | 1.000 | 1.000 | 1.000 | 1.000 | 199 |
| urgency | 0.617 | 0.887 | 0.576 | 0.698 | 231 |
| anatomic_region | 0.683 | 0.617 | 0.640 | 0.628 | 239 |
| has_explicit_recommendation | 0.943 | 0.943 | 0.943 | 0.943 | 300 |
| is_negated | 0.973 | 0.973 | 0.973 | 0.973 | 300 |
| review_required | 0.690 | 0.690 | 0.690 | 0.690 | 300 |

## Category Breakdown

| Category | Reports | Exact Match | Recommendation F1 |
|---|---:|---:|---:|
| false_positive_clinical | 16 | 0.000 | 0.000 |
| multiple_recommendations | 45 | 0.000 | 1.000 |
| negated_recommendation | 45 | 0.800 | 0.000 |
| single_recommendation | 90 | 0.000 | 1.000 |
| typo_unconventional | 24 | 0.292 | 1.000 |
| urgent_language | 40 | 0.600 | 1.000 |
| vague_interval | 40 | 0.000 | 1.000 |

## Recommendation Confusion Matrix

| Gold | Predicted | Count |
|---|---|---:|
| false | false | 44 |
| false | true | 17 |
| true | false | 0 |
| true | true | 239 |

## Interpretation

The engine performs well at detecting whether a report contains an explicit imaging follow-up
recommendation in this synthetic benchmark. Modality and interval extraction are strong when the
recommendation is explicit. The lower exact all-field match is driven by stricter fields:
finding-context extraction, anatomic region selection when multiple body-region terms occur, and
review-required classification for deliberately ambiguous reports.

## Limitations

- The checked-in corpus is synthetic and cannot support clinical performance claims.
- The current engine extracts one primary recommendation per report.
- Finding matching uses strict string matching against a normalized context phrase.
- External validation should use de-identified reports with independent human review and adjudication.
- The Zenodo DOI should be added after a stable release is archived and externally reviewed.
