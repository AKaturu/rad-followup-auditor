from __future__ import annotations

import csv
import random
from pathlib import Path

_REPORT_TEMPLATES: list[dict] = [
    {
        "text": (
            "FINDINGS: There is a {size} {finding} in the {region}. "
            "No pleural effusion or pneumothorax. "
            "IMPRESSION: {finding_cap} in the {region}. "
            "Recommend {modality} in {interval} to {purpose}."
        ),
        "has_followup": True,
    },
    {
        "text": (
            "FINDINGS: The heart is normal in size. The lungs are clear. "
            "No focal consolidation, pleural effusion, or pneumothorax. "
            "IMPRESSION: Normal examination."
        ),
        "has_followup": False,
    },
    {
        "text": (
            "FINDINGS: {size} {finding} seen in the {region}. "
            "Stable compared to prior examination. "
            "IMPRESSION: No significant change. "
            "No further imaging recommended."
        ),
        "has_followup": False,
    },
    {
        "text": (
            "FINDINGS: The liver demonstrates a {size} {finding}. "
            "The spleen, pancreas, and kidneys are unremarkable. "
            "IMPRESSION: {finding_cap} in the liver. "
            "Suggest {modality} for further characterization."
        ),
        "has_followup": True,
    },
    {
        "text": (
            "FINDINGS: {finding_cap} in the right {region}, measuring {size}. "
            "No suspicious features. "
            "IMPRESSION: Benign-appearing {finding}. "
            "Follow-up {modality} in {interval} is recommended per ACR guidelines."
        ),
        "has_followup": True,
    },
    {
        "text": (
            "FINDINGS: Unremarkable examination. "
            "The visualized portions of the {region} are normal. "
            "IMPRESSION: Normal study. No follow-up needed."
        ),
        "has_followup": False,
    },
    {
        "text": (
            "FINDINGS: There is a new {size} {finding} in the {region} "
            "that was not present on prior examination. "
            "IMPRESSION: New {finding}. "
            "Recommend {modality} in {interval} to {purpose}. "
            "Clinical correlation is advised."
        ),
        "has_followup": True,
    },
    {
        "text": (
            "FINDINGS: The {region} appears normal. "
            "No masses, nodules, or abnormalities identified. "
            "IMPRESSION: Unremarkable examination."
        ),
        "has_followup": False,
    },
    {
        "text": (
            "FINDINGS: {finding_cap} in the {region} measuring {size}. "
            "The lesion has {feature} margins. "
            "IMPRESSION: Indeterminate {finding}. "
            "Recommend {modality} guided biopsy for tissue diagnosis."
        ),
        "has_followup": True,
    },
    {
        "text": (
            "FINDINGS: Multiple {finding}s are noted in the {region}, "
            "the largest measuring {size}. "
            "IMPRESSION: Multiple {finding}s. "
            "Consider {modality} in {interval} to assess stability."
        ),
        "has_followup": True,
    },
]

_FINDINGS: list[str] = [
    "pulmonary nodule",
    "liver lesion",
    "renal cyst",
    "adrenal mass",
    "thyroid nodule",
    "pancreatic cyst",
    "ovarian cyst",
    "bone lesion",
    "breast mass",
    "lymph node",
    "lung nodule",
    "hepatic hemangioma",
    "splenic lesion",
    "kidney stone",
    "gallbladder polyp",
    "adrenal adenoma",
    "ovarian mass",
    "soft tissue mass",
    "bronchial wall thickening",
    "pleural plaque",
]

_REGIONS: list[str] = [
    "right upper lobe",
    "left lower lobe",
    "right lower quadrant",
    "left upper quadrant",
    "right lobe of the liver",
    "left kidney",
    "right kidney",
    "pancreatic head",
    "pancreatic tail",
    "right breast",
    "left breast",
    "right thyroid lobe",
    "left thyroid lobe",
    "right adrenal gland",
    "left adrenal gland",
    "right ovary",
    "left ovary",
    "right lung base",
    "left lung apex",
    "right chest wall",
]

_MODALITIES: list[str] = [
    "CT chest",
    "CT abdomen",
    "MRI abdomen",
    "MRI liver",
    "contrast-enhanced CT",
    "ultrasound",
    "PET/CT",
    "CT-guided biopsy",
    "MRI breast",
    "CT colonography",
    "CT urogram",
    "MRI pelvis",
    "MRCP",
    "CT angiography",
    "dedicated renal ultrasound",
    "chest X-ray",
    "mammography",
    "CT neck",
    "MRI cervical spine",
    "CT sinuses",
]

_PURPOSES: list[str] = [
    "further characterization",
    "evaluate stability",
    "assess for interval change",
    "confirm benignity",
    "rule out malignancy",
    "assess for progression",
    "further evaluation",
    "surveillance",
    "tissue sampling",
    "document stability",
]

_SIZES: list[str] = [
    "5 mm",
    "8 mm",
    "1.2 cm",
    "1.5 cm",
    "2.0 cm",
    "3 mm",
    "6 mm",
    "10 mm",
    "4 mm",
    "7 mm",
    "1.8 cm",
    "2.5 cm",
]

_FEATURES: list[str] = [
    "smooth",
    "lobulated",
    "irregular",
    "spiculated",
    "well-circumscribed",
    "ill-defined",
    "microlobulated",
    "macrolobulated",
]

_INTERVALS: list[str] = [
    "3 months",
    "6 months",
    "12 months",
    "2 years",
    "1 year",
    "3-6 months",
    "6-12 months",
    "4 months",
    "8 weeks",
    "annually",
]


def _render(template: dict, rng: random.Random) -> str:
    finding = rng.choice(_FINDINGS)
    finding_cap = finding[0].upper() + finding[1:]
    region = rng.choice(_REGIONS)
    purpose = rng.choice(_PURPOSES)
    interval = rng.choice(_INTERVALS)
    size = rng.choice(_SIZES)
    feature = rng.choice(_FEATURES)

    return template["text"].format(
        finding=finding,
        finding_cap=finding_cap,
        region=region,
        purpose=purpose,
        interval=interval,
        modality=rng.choice(_MODALITIES),
        size=size,
        feature=feature,
    )


def generate_reports(
    n: int = 100,
    seed: int = 42,
    followup_rate: float = 0.55,
) -> list[dict]:
    rng = random.Random(seed)
    reports: list[dict] = []

    for i in range(n):
        if rng.random() < followup_rate:
            template = rng.choice([t for t in _REPORT_TEMPLATES if t["has_followup"]])
        else:
            template = rng.choice([t for t in _REPORT_TEMPLATES if not t["has_followup"]])

        text = _render(template, rng) if template else ""

        reports.append(
            {
                "report_id": f"SYNTH-{i+1:04d}",
                "report_text": text,
            }
        )

    return reports


def write_synthetic_csv(
    path: str | Path,
    n: int = 100,
    seed: int = 42,
    followup_rate: float = 0.55,
) -> list[dict]:
    reports = generate_reports(n=n, seed=seed, followup_rate=followup_rate)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["report_id", "report_text"])
        writer.writeheader()
        writer.writerows(reports)

    return reports
