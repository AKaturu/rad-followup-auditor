from __future__ import annotations

import re

RECOMMENDATION_PATTERNS: list[dict] = [
    {
        "label": "recommend_followup",
        "pattern": re.compile(
            r"(?:recommend|recommended|recommending|advise|advised|advises|"
            r"suggest|suggested|suggests|should undergo|should have|"
            r"should be performed|should be obtained|should get|"
            r"indicated|may benefit from|warrants|warrant|"
            r"referral|referred|refer)",
            re.IGNORECASE,
        ),
        "weight": 1.0,
    },
    {
        "label": "followup_imaging",
        "pattern": re.compile(
            r"(?:follow[- ]?up|f/u|f\.u\.|surveillance|monitoring|"
            r"re[- ]?imaging|repeat imaging|additional imaging|"
            r"further evaluation|further imaging|"
            r"subsequent imaging|subsequent evaluation)",
            re.IGNORECASE,
        ),
        "weight": 0.9,
    },
    {
        "label": "interval_trigger",
        "pattern": re.compile(
            r"(?:in\s+\d+|at\s+\d+|within\s+\d+|every\s+\d+|"
            r"annually|yearly|biannually|biennially|"
            r"monthly|weekly|q\s*\d+|q\d+)",
            re.IGNORECASE,
        ),
        "weight": 0.8,
    },
    {
        "label": "modality_hint",
        "pattern": re.compile(
            r"(?:CT|MRI|MR|ultrasound|US|sonogram|mammogram|"
            r"PET|PET/CT|X-ray|CXR|radiograph|"
            r"biopsy|MRCP|MRA|CTA|EEG|EKG|ECG|"
            r"angiogram|angiography|colonography|"
            r"nuclear medicine|bone scan|DEXA|DXA|"
            r"fluoroscopy|(?:CT|MR|ultrasound|sonographic)[-\s]?guided)",
            re.IGNORECASE,
        ),
        "weight": 0.7,
    },
    {
        "label": "recommendation_verbs",
        "pattern": re.compile(
            r"(?:to exclude|to evaluate|to assess|to characterize|to rule out|"
            r"to confirm|to follow|to monitor|to check|to reassess|"
            r"correlate with|correlation with|compared to|comparison with)",
            re.IGNORECASE,
        ),
        "weight": 0.6,
    },
]

NEGATION_PATTERNS: list[dict] = [
    {
        "label": "direct_negation",
        "pattern": re.compile(
            r"(?:no\s+(?:follow[- ]?up|further|additional|specific|dedicated)\s+"
            r"(?:imaging|evaluation|study|CT|MRI|ultrasound|US|X-ray|radiograph|"
            r"needed|required|necessary|recommended)|"
            r"no\s+(?:further|additional)\s+(?:imaging|studies|evaluation|"
            r"workup|work[- ]?up|assessment)|"
            r"not\s+(?:indicated|recommended|required|necessary|needed|warranted|"
            r"suggested|advised)|"
            r"no\s+(?:need|requirement|indication)\s+(?:for|of)\s+(?:further|"
            r"additional|any)\s+(?:imaging|follow[- ]?up|evaluation))",
            re.IGNORECASE,
        ),
        "weight": 1.0,
    },
    {
        "label": "negation_finding",
        "pattern": re.compile(
            r"(?:no\s+(?:\w+\s+)?(?:evidence|sign|finding|abnormality|mass|nodule|lesion|"
            r"adenopathy|effusion|consolidation|pneumothorax|fracture|"
            r"hemorrhage|infarct|obstruction|dilatation|stricture|"
            r"stenosis|aneurysm|dissection|thrombus|embolus)|"
            r"(?:^|[.!?]\s*)negative(?:$|[.!?\s])|"
            r"(?:^|[.!?]\s*)unremarkable(?:$|[.!?\s])|"
            r"no acute|no significant|no appreciable)",
            re.IGNORECASE,
        ),
        "weight": 0.8,
    },
    {
        "label": "deferring_negation",
        "pattern": re.compile(
            r"(?:defer|deferred|deferring)\s+(?:to|for)\s+(?:clinical|"
            r"clinician|referring|primary|PCP|specialty|surgical|medical).*?"
            r"(?:correlation|decision|management|discretion|evaluation|follow[- ]?up)",
            re.IGNORECASE,
        ),
        "weight": 0.7,
    },
    {
        "label": "clinical_correlation_negation",
        "pattern": re.compile(
            r"(?:clinical correlation|clinical follow[- ]?up|"
            r"correlate clinically|clinically correlate|"
            r"clinical decision|clinical context)",
            re.IGNORECASE,
        ),
        "weight": 0.3,
    },
]

URGENCY_PATTERNS: list[dict] = [
    {
        "label": "urgent",
        "pattern": re.compile(
            r"\b(?:urgent|urgently|prompt|promptly|emergent|emergently|"
            r"immediate|immediately|ASAP|as soon as possible|"
            r"expedited|expedite|stat\b)",
            re.IGNORECASE,
        ),
        "level": "urgent",
        "weight": 1.0,
    },
    {
        "label": "routine",
        "pattern": re.compile(
            r"\b(?:routine|screening|surveillance|"
            r"follow[- ]?up|interval|baseline|"
            r"annually|yearly|biannually|biennially)\b",
            re.IGNORECASE,
        ),
        "level": "routine",
        "weight": 0.6,
    },
]

INTERVAL_PATTERNS: list[dict] = [
    {
        "label": "numeric_interval",
        "pattern": re.compile(
            r"(?:in|at|within|every|after|for)\s+"
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:to|-)?\s*(?:\d+(?:\.\d+)?\s*)?"
            r"(day|days|week|weeks|wk|wks|month|months|mo|mos|"
            r"year|years|yr|yrs)\b",
            re.IGNORECASE,
        ),
    },
    {
        "label": "named_interval",
        "pattern": re.compile(
            r"\b(annually|yearly|biannually|biennially|"
            r"monthly|weekly|quarterly|semi-annually)\b",
            re.IGNORECASE,
        ),
    },
]
