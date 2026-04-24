"""Classify .env variables by sensitivity and data type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_KEYWORDS = {"password", "secret", "token", "api_key", "private", "auth", "credential"}
_TYPE_PATTERNS = {
    "boolean": lambda v: v.lower() in {"true", "false", "yes", "no", "1", "0"},
    "integer": lambda v: v.lstrip("-").isdigit(),
    "float": lambda v: _is_float(v),
    "url": lambda v: v.startswith(("http://", "https://", "ftp://")),
    "path": lambda v: v.startswith("/") or v.startswith("./") or v.startswith("../"),
}


def _is_float(value: str) -> bool:
    try:
        float(value)
        return "." in value or "e" in value.lower()
    except ValueError:
        return False


def _detect_sensitivity(name: str) -> bool:
    lower = name.lower()
    return any(kw in lower for kw in _SENSITIVE_KEYWORDS)


def _detect_type(value: str) -> str:
    for type_name, check in _TYPE_PATTERNS.items():
        if check(value):
            return type_name
    return "string"


@dataclass
class ClassificationEntry:
    key: str
    value: str
    sensitive: bool
    inferred_type: str


@dataclass
class ClassificationReport:
    entries: List[ClassificationEntry] = field(default_factory=list)

    def sensitive_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.sensitive]

    def by_type(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        for entry in self.entries:
            result.setdefault(entry.inferred_type, []).append(entry.key)
        return result

    def summary(self) -> str:
        """Return a human-readable summary of the classification report.

        Example output::

            10 variables (3 sensitive). Types: boolean=2, integer=1, string=7
        """
        type_counts = {
            t: len(keys) for t, keys in self.by_type().items()
        }
        type_summary = ", ".join(
            f"{t}={count}" for t, count in sorted(type_counts.items())
        )
        return (
            f"{self.total} variables ({self.sensitive_count} sensitive). "
            f"Types: {type_summary}"
        )

    @property
    def sensitive_count(self) -> int:
        return sum(1 for e in self.entries if e.sensitive)

    @property
    def total(self) -> int:
        return len(self.entries)


def classify_env(env: Dict[str, str]) -> ClassificationReport:
    """Classify each variable in *env* by sensitivity and inferred type."""
    report = ClassificationReport()
    for key, value in env.items():
        entry = ClassificationEntry(
            key=key,
            value=value,
            sensitive=_detect_sensitivity(key),
            inferred_type=_detect_type(value),
        )
        report.entries.append(entry)
    return report
