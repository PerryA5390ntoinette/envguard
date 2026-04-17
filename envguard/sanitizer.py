"""Sanitize env values by stripping control characters and null bytes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import re

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass
class SanitizeEntry:
    key: str
    original: str
    sanitized: str
    changed: bool


@dataclass
class SanitizeReport:
    entries: List[SanitizeEntry] = field(default_factory=list)

    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.changed)

    def clean_count(self) -> int:
        return sum(1 for e in self.entries if not e.changed)

    def result_env(self) -> Dict[str, str]:
        return {e.key: e.sanitized for e in self.entries}


def _sanitize_value(value: str) -> str:
    """Remove control characters and null bytes from a value."""
    return _CONTROL_RE.sub("", value)


def sanitize_env(env: Dict[str, str]) -> Tuple[Dict[str, str], SanitizeReport]:
    """Sanitize all values in *env*, returning cleaned env and a report."""
    report = SanitizeReport()
    for key, value in env.items():
        sanitized = _sanitize_value(value)
        changed = sanitized != value
        report.entries.append(
            SanitizeEntry(key=key, original=value, sanitized=sanitized, changed=changed)
        )
    return report.result_env(), report
