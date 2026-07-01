# Human Review and Agreement Workflow

Use this workflow when moving beyond synthetic benchmarks into public or institutionally governed report corpora. The goal is to separate software regression tests from reviewer-adjudicated validation evidence.

## Create Reviewer Templates

Run extraction first:

```bash
rad-followup-auditor extract --csv reports.csv --output outputs/extract
```

Create one label file per reviewer:

```bash
rad-followup-auditor review-template \
  outputs/extract/extracted_results.csv reviewer_a.csv --reviewer-id A

rad-followup-auditor review-template \
  outputs/extract/extracted_results.csv reviewer_b.csv --reviewer-id B
```

Reviewers should independently label:

- `has_followup`
- `urgency`
- `interval_present`
- free-text `notes` for uncertain cases

Do not commit report text, reviewer labels, or local review exports unless the corpus is public, de-identified, and approved for redistribution.

## Compute Agreement

```bash
rad-followup-auditor reviewer-agreement \
  reviewer_a.csv reviewer_b.csv reviewer_agreement.json
```

The output reports per-field observed agreement, expected agreement, Cohen's kappa, and compact confusion counts. Use this before final adjudication so the manuscript can distinguish tool performance from reviewer disagreement.

## Publication Guardrails

- Synthetic benchmark scores are regression evidence, not clinical validation.
- Public-data labels should be sampled and adjudicated before strong performance claims.
- Report inter-rater reliability before reporting final adjudicated tool metrics.
- Keep raw reports and reviewer notes in the governed validation workspace, not in Git.
