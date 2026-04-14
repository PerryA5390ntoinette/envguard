"""Detect and report deprecated variable names in .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecationEntry:
    key: str
    reason: str
    replacement: Optional[str] = None

    @property
    def has_replacement(self) -> bool:
        return self.replacement is not None


@dataclass
class DeprecationReport:
    entries: List[DeprecationEntry] = field(default_factory=list)

    def add(self, entry: DeprecationEntry) -> None:
        self.entries.append(entry)

    @property
    def has_deprecations(self) -> bool:
        return len(self.entries) > 0

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def with_replacement(self) -> List[DeprecationEntry]:
        return [e for e in self.entries if e.has_replacement]

    @property
    def without_replacement(self) -> List[DeprecationEntry]:
        return [e for e in self.entries if not e.has_replacement]


def check_deprecations(
    env: Dict[str, str],
    deprecated: Dict[str, Dict[str, Optional[str]]],
) -> DeprecationReport:
    """Check env keys against a deprecation map.

    Args:
        env: Parsed environment variables.
        deprecated: Mapping of deprecated key -> {"reason": str, "replacement": str|None}.

    Returns:
        A DeprecationReport listing every deprecated key found.
    """
    report = DeprecationReport()
    for key in env:
        if key in deprecated:
            meta = deprecated[key]
            entry = DeprecationEntry(
                key=key,
                reason=meta.get("reason", "This variable is deprecated."),
                replacement=meta.get("replacement"),
            )
            report.add(entry)
    return report
