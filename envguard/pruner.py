"""Prune .env variables that match a set of patterns or explicit keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class PruneEntry:
    key: str
    value: str
    reason: str  # 'pattern', 'explicit', or 'kept'
    pruned: bool


@dataclass
class PruneReport:
    entries: List[PruneEntry] = field(default_factory=list)

    def pruned_count(self) -> int:
        return sum(1 for e in self.entries if e.pruned)

    def kept_count(self) -> int:
        return sum(1 for e in self.entries if not e.pruned)

    def pruned_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.pruned]

    def result_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries if not e.pruned}


def prune_env(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> tuple[Dict[str, str], PruneReport]:
    """Remove variables from *env* that match *keys* or *patterns*.

    Args:
        env: The source environment mapping.
        keys: Explicit variable names to remove.
        patterns: Regular-expression patterns; any key that fully matches
                  one of these patterns will be pruned.

    Returns:
        A tuple of (cleaned_env, PruneReport).
    """
    explicit: set[str] = set(keys or [])
    compiled = [re.compile(p) for p in (patterns or [])]

    report = PruneReport()
    for key, value in env.items():
        if key in explicit:
            report.entries.append(PruneEntry(key=key, value=value, reason="explicit", pruned=True))
            continue

        matched_pattern = next((p.pattern for p in compiled if p.fullmatch(key)), None)
        if matched_pattern is not None:
            report.entries.append(PruneEntry(key=key, value=value, reason="pattern", pruned=True))
            continue

        report.entries.append(PruneEntry(key=key, value=value, reason="kept", pruned=False))

    return report.result_env(), report
