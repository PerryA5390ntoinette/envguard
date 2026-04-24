"""rotator.py – detect variables that may be due for rotation based on age hints."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

# Keywords that suggest a variable holds a credential that should be rotated
_ROTATION_KEYWORDS = re.compile(
    r"(password|passwd|secret|token|key|api_key|apikey|credential|cert|private)",
    re.IGNORECASE,
)


@dataclass
class RotationEntry:
    key: str
    value: str
    reason: str
    suggested_action: str


@dataclass
class RotationReport:
    entries: List[RotationEntry] = field(default_factory=list)

    def add(self, entry: RotationEntry) -> None:
        self.entries.append(entry)

    @property
    def flagged_count(self) -> int:
        return len(self.entries)

    @property
    def has_candidates(self) -> bool:
        return bool(self.entries)

    @property
    def flagged_keys(self) -> List[str]:
        return [e.key for e in self.entries]


def _is_rotation_candidate(key: str, value: str) -> Optional[str]:
    """Return a reason string if the variable looks like a rotation candidate."""
    if _ROTATION_KEYWORDS.search(key):
        if not value or value.strip() == "":
            return "sensitive key has an empty value"
        if value.lower() in ("changeme", "placeholder", "todo", "fixme", "example", "test"):
            return f"value appears to be a placeholder: '{value}'"
        if len(value) < 8:
            return "sensitive key has a suspiciously short value"
        return None
    return None


def check_rotation(env: Dict[str, str]) -> RotationReport:
    """Inspect *env* and flag variables that look like rotation candidates."""
    report = RotationReport()
    for key, value in env.items():
        reason = _is_rotation_candidate(key, value)
        if reason:
            entry = RotationEntry(
                key=key,
                value=value,
                reason=reason,
                suggested_action="Replace with a freshly generated secret and redeploy.",
            )
            report.add(entry)
    return report
