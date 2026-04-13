"""Detect duplicate keys and duplicate values in .env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List


@dataclass
class DuplicateEntry:
    key: str
    occurrences: int
    values: List[str]


@dataclass
class DuplicateReport:
    key_duplicates: List[DuplicateEntry] = field(default_factory=list)
    value_duplicates: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def has_key_duplicates(self) -> bool:
        return len(self.key_duplicates) > 0

    @property
    def has_value_duplicates(self) -> bool:
        return len(self.value_duplicates) > 0

    @property
    def total_issues(self) -> int:
        return len(self.key_duplicates) + len(self.value_duplicates)


def _find_key_duplicates(lines: List[str]) -> List[DuplicateEntry]:
    """Scan raw lines to find keys that appear more than once."""
    counts: Dict[str, List[str]] = defaultdict(list)
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        counts[key.strip()].append(value.strip())

    entries = []
    for key, values in counts.items():
        if len(values) > 1:
            entries.append(DuplicateEntry(key=key, occurrences=len(values), values=values))
    return entries


def _find_value_duplicates(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Find non-empty values shared by multiple keys."""
    value_map: Dict[str, List[str]] = defaultdict(list)
    for key, value in env.items():
        if value:
            value_map[value].append(key)
    return {v: keys for v, keys in value_map.items() if len(keys) > 1}


def find_duplicates(env: Dict[str, str], raw_lines: List[str] | None = None) -> DuplicateReport:
    """Return a DuplicateReport for the given env dict and optional raw lines."""
    key_dups = _find_key_duplicates(raw_lines) if raw_lines is not None else []
    value_dups = _find_value_duplicates(env)
    return DuplicateReport(key_duplicates=key_dups, value_duplicates=value_dups)
