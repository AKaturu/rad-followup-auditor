"""Build the synthetic validation corpus used by the benchmark tests.

The resulting CSV is intentionally synthetic. It exercises realistic report
wording patterns, but it is not a substitute for an institutionally reviewed
clinical corpus.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "tests" / "data" / "validation_reports.csv"


@dataclass(frozen=True)
class CaseTemplate:
    category: str
    finding: str
    report_text: str
    recommended_modality: str
    interval_value: str
    interval_unit: str
    urgency: str
    anatomic_region: str
    has_explicit_recommendation: str
    is_negated: str
    review_required: str
    notes: str


def _positive_cases() -> list[CaseTemplate]:
    findings = [
        ("pulmonary nodule is present", "CT", "6", "months", "routine", "chest"),
        ("indeterminate liver lesion is present", "MRI", "3", "months", "routine", "abdomen"),
        ("complex renal cyst is present", "Ultrasound", "6", "months", "routine", "renal"),
        ("thyroid nodule is present", "Ultrasound", "1", "years", "routine", "thyroid"),
        ("pancreatic cystic lesion is present", "MRI", "1", "years", "routine", "pancreas"),
        ("adrenal nodule is present", "CT", "12", "months", "routine", "adrenal"),
        ("breast asymmetry is present", "Mammography", "6", "months", "routine", "breast"),
        ("sclerotic bone lesion is present", "Nuclear Medicine", "3", "months", "routine", "spine"),
        ("ovarian cyst is present", "Ultrasound", "8", "weeks", "routine", "ovarian"),
        ("small bowel thickening is present", "CT", "6", "weeks", "routine", "small bowel"),
    ]
    cases: list[CaseTemplate] = []
    for finding, modality, value, unit, urgency, region in findings:
        cases.append(
            CaseTemplate(
                category="single_recommendation",
                finding=finding,
                report_text=(
                    f"FINDINGS: {finding.capitalize()}. IMPRESSION: "
                    f"{finding.capitalize()}; recommend {modality} {region} in {value} {unit}."
                ),
                recommended_modality=modality,
                interval_value=value,
                interval_unit=unit,
                urgency=urgency,
                anatomic_region=region,
                has_explicit_recommendation="true",
                is_negated="false",
                review_required="false",
                notes="direct single recommendation with explicit interval",
            )
        )
    return cases


def _multiple_cases() -> list[CaseTemplate]:
    cases: list[CaseTemplate] = []
    base = [
        ("pulmonary nodules are present", "CT", "chest", "6", "months"),
        ("renal lesion and liver lesion are present", "MRI", "abdomen", "3", "months"),
        ("thyroid nodule and cervical node are present", "Ultrasound", "neck", "12", "weeks"),
        ("breast calcifications and asymmetry are present", "Mammography", "breast", "6", "months"),
        ("pancreatic cyst and adrenal nodule are present", "MRI", "abdomen", "1", "years"),
    ]
    for finding, modality, region, value, unit in base:
        cases.append(
            CaseTemplate(
                category="multiple_recommendations",
                finding=finding,
                report_text=(
                    f"FINDINGS: {finding.capitalize()}. IMPRESSION: {finding.capitalize()}; "
                    f"recommend {modality} {region} in {value} {unit}. "
                    "Also suggest clinical follow-up with the referring clinician."
                ),
                recommended_modality=modality,
                interval_value=value,
                interval_unit=unit,
                urgency="routine",
                anatomic_region=region,
                has_explicit_recommendation="true",
                is_negated="false",
                review_required="false",
                notes="primary imaging recommendation plus secondary clinical language",
            )
        )
    return cases


def _negated_cases() -> list[CaseTemplate]:
    phrases = [
        "No follow-up imaging recommended.",
        "No further imaging is needed.",
        "No additional evaluation required.",
        "Follow-up CT is not indicated.",
        "No need for further imaging.",
    ]
    return [
        CaseTemplate(
            category="negated_recommendation",
            finding="",
            report_text=(
                "FINDINGS: Stable benign appearing renal cyst. IMPRESSION: "
                f"{phrase}"
            ),
            recommended_modality="",
            interval_value="",
            interval_unit="",
            urgency="",
            anatomic_region="",
            has_explicit_recommendation="false",
            is_negated="true",
            review_required="false",
            notes="explicitly negated follow-up recommendation",
        )
        for phrase in phrases
    ]


def _vague_interval_cases() -> list[CaseTemplate]:
    base = [
        ("indeterminate liver lesion is present", "MRI", "abdomen"),
        ("pulmonary nodule is present", "CT", "chest"),
        ("complex renal lesion is present", "Ultrasound", "renal"),
        ("thyroid nodule is present", "Ultrasound", "thyroid"),
        ("adrenal nodule is present", "CT", "adrenal"),
    ]
    return [
        CaseTemplate(
            category="vague_interval",
            finding=finding,
            report_text=(
                f"FINDINGS: {finding.capitalize()}. IMPRESSION: {finding.capitalize()}; "
                f"consider {modality} {region} follow-up as clinically indicated."
            ),
            recommended_modality=modality,
            interval_value="",
            interval_unit="",
            urgency="routine",
            anatomic_region=region,
            has_explicit_recommendation="true",
            is_negated="false",
            review_required="true",
            notes="explicit modality with vague timing",
        )
        for finding, modality, region in base
    ]


def _urgent_cases() -> list[CaseTemplate]:
    base = [
        ("possible intracranial lesion is present", "MRI", "brain", "2", "weeks"),
        ("suspected pulmonary embolic sequela is present", "CTA", "pulmonary", "7", "days"),
        ("enlarging neck mass is present", "CT", "neck", "10", "days"),
        ("possible infection-related collection is present", "CT", "abdomen", "1", "weeks"),
        ("new spinal lesion is present", "MRI", "spine", "2", "weeks"),
    ]
    return [
        CaseTemplate(
            category="urgent_language",
            finding=finding,
            report_text=(
                f"FINDINGS: {finding.capitalize()}. IMPRESSION: {finding.capitalize()}; "
                f"urgent {modality} {region} is recommended within {value} {unit}."
            ),
            recommended_modality=modality,
            interval_value=value,
            interval_unit=unit,
            urgency="urgent",
            anatomic_region=region,
            has_explicit_recommendation="true",
            is_negated="false",
            review_required="false",
            notes="urgent or expedited recommendation wording",
        )
        for finding, modality, region, value, unit in base
    ]


def _edge_cases() -> list[CaseTemplate]:
    return [
        CaseTemplate(
            category="typo_unconventional",
            finding="pulmonary nodule is present",
            report_text=(
                "FINDINGS: Pulmonary nodule is present. IMPRESSION: "
                "Pulmonary nodule is present; f/u CT chest in 6 mos."
            ),
            recommended_modality="CT",
            interval_value="6",
            interval_unit="months",
            urgency="routine",
            anatomic_region="chest",
            has_explicit_recommendation="true",
            is_negated="false",
            review_required="false",
            notes="abbreviated follow-up and month wording",
        ),
        CaseTemplate(
            category="typo_unconventional",
            finding="liver lesion is present",
            report_text=(
                "FINDINGS: Liver lesion is present. IMPRESSION: "
                "Liver lesion is present; MRI abdomen yearly for surveillance."
            ),
            recommended_modality="MRI",
            interval_value="1",
            interval_unit="years",
            urgency="routine",
            anatomic_region="abdomen",
            has_explicit_recommendation="true",
            is_negated="false",
            review_required="false",
            notes="named yearly interval",
        ),
        CaseTemplate(
            category="typo_unconventional",
            finding="renal cyst is present",
            report_text=(
                "FINDINGS: Renal cyst is present. IMPRESSION: "
                "Renal cyst is present; sonogram renal after 3 mos."
            ),
            recommended_modality="Ultrasound",
            interval_value="3",
            interval_unit="months",
            urgency="",
            anatomic_region="renal",
            has_explicit_recommendation="true",
            is_negated="false",
            review_required="false",
            notes="modality synonym and abbreviated interval",
        ),
        CaseTemplate(
            category="false_positive_clinical",
            finding="",
            report_text=(
                "FINDINGS: Mild chronic change. IMPRESSION: Clinical correlation is suggested; "
                "no specific imaging follow-up is recommended."
            ),
            recommended_modality="",
            interval_value="",
            interval_unit="",
            urgency="",
            anatomic_region="",
            has_explicit_recommendation="false",
            is_negated="true",
            review_required="true",
            notes="clinical correlation and negated imaging",
        ),
        CaseTemplate(
            category="false_positive_clinical",
            finding="",
            report_text=(
                "FINDINGS: Stable postoperative appearance. IMPRESSION: "
                "Clinical follow-up at the discretion of the treating team."
            ),
            recommended_modality="",
            interval_value="",
            interval_unit="",
            urgency="",
            anatomic_region="",
            has_explicit_recommendation="false",
            is_negated="false",
            review_required="true",
            notes="clinical-only follow-up, not imaging follow-up",
        ),
    ]


def build_rows() -> list[dict[str, str]]:
    seed_cases = (
        _positive_cases()
        + _multiple_cases()
        + _negated_cases()
        + _vague_interval_cases()
        + _urgent_cases()
        + _edge_cases()
    )
    rows: list[dict[str, str]] = []
    for index in range(300):
        case = seed_cases[index % len(seed_cases)]
        report_id = f"VAL-{index + 1:03d}"
        variant_text = case.report_text
        if index >= 250:
            variant_text = variant_text.replace("IMPRESSION:", "CONCLUSION:")
        elif index >= 200:
            variant_text = variant_text.replace("recommend", "advise")
        elif index >= 150:
            variant_text = variant_text.replace("FINDINGS:", "EXAM FINDINGS:")
        row = {
            "report_id": report_id,
            "category": case.category,
            "report_text": variant_text,
            "gold_finding": case.finding,
            "gold_recommended_modality": case.recommended_modality,
            "gold_interval_value": case.interval_value,
            "gold_interval_unit": case.interval_unit,
            "gold_urgency": case.urgency,
            "gold_anatomic_region": case.anatomic_region,
            "gold_has_explicit_recommendation": case.has_explicit_recommendation,
            "gold_is_negated": case.is_negated,
            "gold_review_required": case.review_required,
            "reviewer_1": "synthetic_template",
            "reviewer_2": "synthetic_adjudication",
            "adjudication_status": "synthetic_consensus",
            "notes": case.notes,
        }
        rows.append(row)
    return rows


def write_corpus(path: Path) -> None:
    rows = build_rows()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    write_corpus(DEFAULT_OUTPUT)
    print(f"Wrote {DEFAULT_OUTPUT}")


if __name__ == "__main__":
    main()
