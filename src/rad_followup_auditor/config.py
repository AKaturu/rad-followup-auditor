from __future__ import annotations

from dataclasses import dataclass

COL_REPORT_ID = "report_id"
COL_REPORT_TEXT = "report_text"
COL_STUDY_DATE = "study_date"
COL_MODALITY = "modality"
COL_ACCESSION = "accession"

REQUIRED_INPUT_COLUMNS: tuple[str, ...] = (
    COL_REPORT_ID,
    COL_REPORT_TEXT,
)

OPTIONAL_INPUT_COLUMNS: tuple[str, ...] = (
    COL_STUDY_DATE,
    COL_MODALITY,
    COL_ACCESSION,
)

COL_FINDING = "finding"
COL_RECOMMENDED_MODALITY = "recommended_modality"
COL_INTERVAL_VALUE = "interval_value"
COL_INTERVAL_UNIT = "interval_unit"
COL_URGENCY = "urgency"
COL_ANATOMIC_REGION = "anatomic_region"
COL_HAS_EXPLICIT_RECOMMENDATION = "has_explicit_recommendation"
COL_RECOMMENDATION_TEXT = "recommendation_text"
COL_CONFIDENCE = "confidence"
COL_IS_NEGATED = "is_negated"
COL_REVIEW_REQUIRED = "review_required"
COL_NEGATION_CONTEXT = "negation_context"

OUTPUT_COLUMNS: tuple[str, ...] = (
    COL_REPORT_ID,
    COL_REPORT_TEXT,
    COL_FINDING,
    COL_RECOMMENDED_MODALITY,
    COL_INTERVAL_VALUE,
    COL_INTERVAL_UNIT,
    COL_URGENCY,
    COL_ANATOMIC_REGION,
    COL_HAS_EXPLICIT_RECOMMENDATION,
    COL_RECOMMENDATION_TEXT,
    COL_CONFIDENCE,
    COL_IS_NEGATED,
    COL_REVIEW_REQUIRED,
    COL_NEGATION_CONTEXT,
)


MODALITIES: dict[str, str] = {
    "ct": "CT",
    "cat scan": "CT",
    "computed tomography": "CT",
    "mri": "MRI",
    "mr": "MRI",
    "magnetic resonance": "MRI",
    "ultrasound": "Ultrasound",
    "us": "Ultrasound",
    "sonogram": "Ultrasound",
    "ultrasonography": "Ultrasound",
    "x-ray": "X-ray",
    "radiograph": "X-ray",
    "cxr": "X-ray",
    "chest x-ray": "X-ray",
    "pet": "PET",
    "pet/ct": "PET/CT",
    "pet-ct": "PET/CT",
    "mammography": "Mammography",
    "mammogram": "Mammography",
    "fluoroscopy": "Fluoroscopy",
    "nuclear medicine": "Nuclear Medicine",
    "bone scan": "Nuclear Medicine",
    "dexa": "DEXA",
    "dxa": "DEXA",
    "colonography": "CT Colonography",
    "ct colonography": "CT Colonography",
    "virtual colonoscopy": "CT Colonography",
    "biopsy": "Biopsy",
    "percutaneous biopsy": "Biopsy",
    "mrcp": "MRCP",
    "mra": "MRA",
    "mr angiography": "MRA",
    "cta": "CTA",
    "ct angiography": "CTA",
    "eeg": "EEG",
    "ekg": "EKG",
    "ecg": "EKG",
    "angiogram": "Angiography",
    "angiography": "Angiography",
}

ANATOMIC_REGIONS: list[str] = [
    "chest",
    "thorax",
    "abdomen",
    "pelvis",
    "head",
    "brain",
    "neck",
    "spine",
    "lumbar spine",
    "cervical spine",
    "thoracic spine",
    "breast",
    "cardiac",
    "heart",
    "lung",
    "liver",
    "kidney",
    "renal",
    "pancreas",
    "adrenal",
    "thyroid",
    "extremity",
    "upper extremity",
    "lower extremity",
    "shoulder",
    "knee",
    "hip",
    "wrist",
    "ankle",
    "elbow",
    "hand",
    "foot",
    "ovarian",
    "prostate",
    "bladder",
    "sinus",
    "orbit",
    "facial",
    "paranasal sinus",
    "temporal bone",
    "mandible",
    "colon",
    "rectal",
    "sigmoid",
    "small bowel",
    "appendix",
    "vascular",
    "carotid",
    "coronary",
    "pulmonary",
    "aorta",
    "venous",
]

URGENCY_LEVELS: list[str] = ["routine", "urgent", "STAT"]

CONFIDENCE_LEVELS: list[str] = ["high", "medium", "low"]

INTERVAL_UNITS: list[str] = ["days", "weeks", "months", "years"]


@dataclass(frozen=True)
class ExtractionConfig:
    window_chars_before: int = 75
    window_chars_after: int = 50
    min_interval_value: float = 0.0
    max_interval_value: float = 120.0
    default_interval_unit: str = "months"
    negation_radius_chars: int = 30
    high_confidence_threshold: float = 0.8
    medium_confidence_threshold: float = 0.5
    custom_recommendation_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()


DEFAULT_CONFIG: ExtractionConfig = ExtractionConfig()
