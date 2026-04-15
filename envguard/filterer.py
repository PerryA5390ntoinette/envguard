"""Filter env variables by pattern, tag, or prefix."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class FilterEntry:
    key: str
    value: str
    matched_by: str  # 'pattern', 'prefix', 'tag', 'key'


@dataclass
class FilterReport:
    entries: List[FilterEntry] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)

    def matched_count(self) -> int:
        return len(self.entries)

    def excluded_count(self) -> int:
        return len(self.excluded)

    def result_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}


def _matches_pattern(key: str, pattern: str) -> bool:
    try:
        return bool(re.search(pattern, key))
    except re.error:
        return False


def filter_env(
    env: Dict[str, str],
    *,
    pattern: Optional[str] = None,
    prefix: Optional[str] = None,
    keys: Optional[List[str]] = None,
    exclude_pattern: Optional[str] = None,
) -> FilterReport:
    """Return a FilterReport containing only the variables that match the criteria."""
    report = FilterReport()

    for key, value in env.items():
        # Exclusion check first
        if exclude_pattern and _matches_pattern(key, exclude_pattern):
            report.excluded.append(key)
            continue

        matched_by: Optional[str] = None

        if keys and key in keys:
            matched_by = "key"
        elif prefix and key.startswith(prefix):
            matched_by = "prefix"
        elif pattern and _matches_pattern(key, pattern):
            matched_by = "pattern"
        elif not keys and not prefix and not pattern:
            matched_by = "all"

        if matched_by:
            report.entries.append(FilterEntry(key=key, value=value, matched_by=matched_by))
        else:
            report.excluded.append(key)

    return report
