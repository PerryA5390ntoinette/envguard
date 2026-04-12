"""Merge multiple .env files with conflict detection and precedence rules."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MergeConflict:
    key: str
    values: List[Tuple[str, str]]  # list of (source_file, value)


@dataclass
class MergeReport:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: List[MergeConflict] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


def _collect_conflicts(
    key: str,
    existing_value: str,
    existing_source: str,
    new_value: str,
    new_source: str,
    conflicts: List[MergeConflict],
) -> None:
    """Record a conflict between two sources for the same key."""
    for conflict in conflicts:
        if conflict.key == key:
            conflict.values.append((new_source, new_value))
            return
    conflicts.append(
        MergeConflict(
            key=key,
            values=[(existing_source, existing_value), (new_source, new_value)],
        )
    )


def merge_envs(
    env_maps: List[Tuple[str, Dict[str, str]]],
    strategy: str = "last-wins",
    detect_conflicts: bool = True,
) -> MergeReport:
    """Merge a list of (source_name, env_dict) pairs into a single MergeReport.

    Args:
        env_maps: Ordered list of (source_name, key-value dict) pairs.
        strategy: 'last-wins' keeps the last value; 'first-wins' keeps the first.
        detect_conflicts: When True, populate report.conflicts for differing values.

    Returns:
        MergeReport with merged values, conflicts, and source list.
    """
    report = MergeReport()
    key_source: Dict[str, str] = {}

    for source, env in env_maps:
        report.sources.append(source)
        for key, value in env.items():
            if key in report.merged:
                existing_value = report.merged[key]
                if existing_value != value and detect_conflicts:
                    _collect_conflicts(
                        key,
                        existing_value,
                        key_source[key],
                        value,
                        source,
                        report.conflicts,
                    )
                if strategy == "last-wins":
                    report.merged[key] = value
                    key_source[key] = source
            else:
                report.merged[key] = value
                key_source[key] = source

    return report
