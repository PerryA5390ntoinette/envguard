"""masker.py — Mask sensitive variable values for safe display."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_KEYWORDS = ("password", "secret", "token", "key", "auth", "credential", "passwd", "private")

_MASK = "***"
_PARTIAL_VISIBLE = 4  # characters to reveal at the end for partial masking


@dataclass
class MaskEntry:
    name: str
    original: str
    masked: str
    was_masked: bool


@dataclass
class MaskReport:
    entries: List[MaskEntry] = field(default_factory=list)

    @property
    def masked_count(self) -> int:
        return sum(1 for e in self.entries if e.was_masked)

    @property
    def plain_count(self) -> int:
        return sum(1 for e in self.entries if not e.was_masked)

    def masked_env(self) -> Dict[str, str]:
        """Return a dict with masked values substituted in."""
        return {e.name: e.masked for e in self.entries}


def _is_sensitive(name: str) -> bool:
    lower = name.lower()
    return any(kw in lower for kw in _SENSITIVE_KEYWORDS)


def _mask_value(value: str, partial: bool = False) -> str:
    if not value:
        return _MASK
    if partial and len(value) > _PARTIAL_VISIBLE:
        return _MASK + value[-_PARTIAL_VISIBLE:]
    return _MASK


def mask_env(env: Dict[str, str], partial: bool = False) -> MaskReport:
    """Mask sensitive values in *env*.

    Args:
        env: Mapping of variable names to values.
        partial: If True, reveal the last few characters of sensitive values.

    Returns:
        A :class:`MaskReport` describing which variables were masked.
    """
    report = MaskReport()
    for name, value in env.items():
        sensitive = _is_sensitive(name)
        masked_value = _mask_value(value, partial=partial) if sensitive else value
        report.entries.append(
            MaskEntry(
                name=name,
                original=value,
                masked=masked_value,
                was_masked=sensitive,
            )
        )
    return report
