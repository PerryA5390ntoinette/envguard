"""Normalizer: standardize .env variable values according to type hints."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class NormalizeEntry:
    key: str
    original: str
    normalized: str
    rule: str  # e.g. 'boolean', 'strip', 'lowercase_bool', 'trim_quotes'

    @property
    def changed(self) -> bool:
        return self.original != self.normalized


@dataclass
class NormalizeReport:
    entries: List[NormalizeEntry] = field(default_factory=list)

    @property
    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.changed)

    @property
    def unchanged_count(self) -> int:
        return sum(1 for e in self.entries if not e.changed)

    @property
    def result_env(self) -> Dict[str, str]:
        return {e.key: e.normalized for e in self.entries}


_BOOLEAN_TRUE = {"1", "yes", "on", "true"}
_BOOLEAN_FALSE = {"0", "no", "off", "false"}


def _normalize_value(value: str) -> tuple[str, str]:
    """Return (normalized_value, rule_applied)."""
    stripped = value.strip()

    # Remove surrounding matching quotes
    if len(stripped) >= 2 and stripped[0] in ('"', "'") and stripped[-1] == stripped[0]:
        inner = stripped[1:-1]
        return inner, "trim_quotes"

    # Normalize boolean-like values to canonical lowercase
    lower = stripped.lower()
    if lower in _BOOLEAN_TRUE:
        canonical = "true"
        if stripped != canonical:
            return canonical, "boolean"
    elif lower in _BOOLEAN_FALSE:
        canonical = "false"
        if stripped != canonical:
            return canonical, "boolean"

    # Strip surrounding whitespace only
    if stripped != value:
        return stripped, "strip"

    return value, "none"


def normalize_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
) -> tuple[Dict[str, str], NormalizeReport]:
    """Normalize values in *env*.

    If *keys* is provided, only those keys are processed; otherwise all keys
    are normalized.
    """
    report = NormalizeReport()
    target_keys = keys if keys is not None else list(env.keys())

    for key in env:
        original = env[key]
        if key in target_keys:
            normalized, rule = _normalize_value(original)
        else:
            normalized, rule = original, "none"
        report.entries.append(NormalizeEntry(key=key, original=original, normalized=normalized, rule=rule))

    return report.result_env, report
