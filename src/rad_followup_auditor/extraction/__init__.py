from .engine import ExtractionEngine, ExtractionResult, extract_all
from .patterns import NEGATION_PATTERNS, RECOMMENDATION_PATTERNS

__all__ = [
    "NEGATION_PATTERNS",
    "RECOMMENDATION_PATTERNS",
    "ExtractionEngine",
    "ExtractionResult",
    "extract_all",
]
