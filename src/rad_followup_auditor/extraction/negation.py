from __future__ import annotations

import re
from dataclasses import dataclass

from .patterns import NEGATION_PATTERNS


@dataclass
class NegationResult:
    is_negated: bool
    matched_pattern: str | None
    matched_text: str | None
    context_window: str | None


def check_negation(
    text: str,
    trigger_pos: int,
    window_chars: int = 30,
) -> NegationResult:
    start = 0 if trigger_pos < 0 else max(0, trigger_pos - window_chars)

    end = min(len(text), trigger_pos + window_chars) if trigger_pos >= 0 else len(text)
    context = text[start:end]

    for neg in NEGATION_PATTERNS:
        match = neg["pattern"].search(context)
        if match:
            return NegationResult(
                is_negated=True,
                matched_pattern=neg["label"],
                matched_text=match.group(),
                context_window=context,
            )

    return NegationResult(
        is_negated=False,
        matched_pattern=None,
        matched_text=None,
        context_window=context,
    )


_negation_lead = re.compile(
    r"(?:no\s+(?:further|additional|specific|dedicated)\s+"
    r"(?:imaging|evaluation|study|work[- ]?up|assessment)|"
    r"no\s+(?:need|indication)\s+(?:for|of)\s+(?:further|additional|any)\s+"
    r"(?:imaging|follow[- ]?up|evaluation)|"
    r"not\s+(?:indicated|recommended|required|necessary|needed|warranted))",
    re.IGNORECASE,
)

_clin_corr = re.compile(
    r"(?:clinical correlation|clinical follow[- ]?up|"
    r"correlate clinically|clinically correlate)",
    re.IGNORECASE,
)


def classify_recommendation_type(rec_text: str) -> str:
    if _negation_lead.search(rec_text):
        return "negative"
    if _clin_corr.search(rec_text):
        return "clinical_correlation"
    return "positive"
