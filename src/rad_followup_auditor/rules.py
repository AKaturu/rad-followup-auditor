from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import DEFAULT_CONFIG, ExtractionConfig


def load_extraction_config(
    custom_patterns: str | Path | None = None,
    exclude_patterns: str | Path | None = None,
    *,
    base: ExtractionConfig = DEFAULT_CONFIG,
) -> ExtractionConfig:
    recommendation_rules: list[str] = []
    exclude_rules: list[str] = []

    if custom_patterns:
        custom_payload = _load_rule_file(custom_patterns)
        recommendation_rules.extend(custom_payload["recommendation_patterns"])
        exclude_rules.extend(custom_payload["exclude_patterns"])

    if exclude_patterns:
        exclude_payload = _load_rule_file(exclude_patterns, default_kind="exclude")
        recommendation_rules.extend(exclude_payload["recommendation_patterns"])
        exclude_rules.extend(exclude_payload["exclude_patterns"])

    return ExtractionConfig(
        window_chars_before=base.window_chars_before,
        window_chars_after=base.window_chars_after,
        min_interval_value=base.min_interval_value,
        max_interval_value=base.max_interval_value,
        default_interval_unit=base.default_interval_unit,
        negation_radius_chars=base.negation_radius_chars,
        high_confidence_threshold=base.high_confidence_threshold,
        medium_confidence_threshold=base.medium_confidence_threshold,
        custom_recommendation_patterns=(*base.custom_recommendation_patterns, *recommendation_rules),
        exclude_patterns=(*base.exclude_patterns, *exclude_rules),
    )


def _load_rule_file(
    path: str | Path,
    *,
    default_kind: str = "recommendation",
) -> dict[str, list[str]]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() == ".json":
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError("Custom rule JSON must be an object")
        return _patterns_from_json(payload)

    rules = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if default_kind == "exclude":
        return {"recommendation_patterns": [], "exclude_patterns": rules}
    return {"recommendation_patterns": rules, "exclude_patterns": []}


def _patterns_from_json(payload: dict[str, Any]) -> dict[str, list[str]]:
    recommendation_keys = ("recommendation_patterns", "custom_patterns", "include_patterns")
    exclude_keys = ("exclude_patterns", "false_positive_patterns", "suppression_patterns")
    return {
        "recommendation_patterns": _collect_patterns(payload, recommendation_keys),
        "exclude_patterns": _collect_patterns(payload, exclude_keys),
    }


def _collect_patterns(payload: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
    patterns: list[str] = []
    for key in keys:
        values = payload.get(key, [])
        if isinstance(values, str):
            values = [values]
        for item in values:
            if isinstance(item, str):
                patterns.append(item)
            elif isinstance(item, dict) and "pattern" in item:
                patterns.append(str(item["pattern"]))
            else:
                raise ValueError(f"Invalid custom rule entry under {key}: {item!r}")
    return patterns
