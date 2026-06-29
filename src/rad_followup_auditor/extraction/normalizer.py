from __future__ import annotations

import re

from .patterns import INTERVAL_PATTERNS

_INTERVAL_NAMED_MAP: dict[str, tuple[float, str]] = {
    "annually": (1.0, "years"),
    "yearly": (1.0, "years"),
    "biannually": (6.0, "months"),
    "biennially": (2.0, "years"),
    "monthly": (1.0, "months"),
    "weekly": (1.0, "weeks"),
    "quarterly": (3.0, "months"),
    "semi-annually": (6.0, "months"),
}


def extract_interval(text: str) -> tuple[float | None, str | None]:
    for pat in INTERVAL_PATTERNS:
        if pat["label"] == "numeric_interval":
            match = pat["pattern"].search(text)
            if match:
                try:
                    value = float(match.group(1))
                except (ValueError, IndexError):
                    continue
                raw_unit = match.group(2).lower() if match.lastindex and match.lastindex >= 2 else ""
                unit = _normalize_unit(raw_unit)
                return value, unit
        elif pat["label"] == "named_interval":
            match = pat["pattern"].search(text)
            if match:
                matched = match.group(1).lower()
                if matched in _INTERVAL_NAMED_MAP:
                    return _INTERVAL_NAMED_MAP[matched]
    return None, None


_NORMALIZE_UNIT_MAP: dict[str, str] = {
    "day": "days",
    "days": "days",
    "week": "weeks",
    "weeks": "weeks",
    "wk": "weeks",
    "wks": "weeks",
    "month": "months",
    "months": "months",
    "mo": "months",
    "mos": "months",
    "year": "years",
    "years": "years",
    "yr": "years",
    "yrs": "years",
}


def _normalize_unit(raw: str) -> str | None:
    return _NORMALIZE_UNIT_MAP.get(raw.lower())


_modality_re = re.compile(
    r"(?:CT|MRI|MR|ultrasound|US|sonogram|mammogram|PET|PET/CT|X-ray|CXR|"
    r"radiograph|biopsy|MRCP|MRA|CTA|EEG|EKG|ECG|angiogram|angiography|"
    r"colonography|nuclear medicine|bone scan|DEXA|DXA|fluoroscopy)\b",
    re.IGNORECASE,
)

_anatomic_re = re.compile(
    r"(?:chest|thorax|abdomen|pelvis|head|brain|neck|spine|lumbar|"
    r"cervical|thoracic|breast|cardiac|heart|lung|liver|kidney|renal|"
    r"pancreas|adrenal|thyroid|extremity|shoulder|knee|hip|wrist|ankle|"
    r"elbow|hand|foot|ovarian|prostate|bladder|sinus|orbit|facial|colon|"
    r"rectal|sigmoid|small bowel|appendix|vascular|carotid|coronary|"
    r"pulmonary|aorta|venous)\b",
    re.IGNORECASE,
)


def extract_modality(text: str) -> str | None:
    from ..config import MODALITIES

    match = _modality_re.search(text)
    if match:
        raw = match.group(0).lower()
        return MODALITIES.get(raw, raw)
    return None


def extract_anatomic_region(text: str) -> str | None:
    match = _anatomic_re.search(text)
    if match:
        return match.group(0).lower()
    return None


def normalize_finding(finding_text: str) -> str:
    finding_text = re.sub(r"\s+", " ", finding_text).strip()
    finding_text = re.sub(r"[.,;:]+$", "", finding_text)
    return finding_text.lower()
