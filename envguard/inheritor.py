"""Inheritor: merge a base .env with an override .env, tracking which keys were inherited vs overridden."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class InheritEntry:
    key: str
    value: str
    source: str  # 'base' | 'override' | 'merged'
    overridden: bool = False


@dataclass
class InheritReport:
    entries: List[InheritEntry] = field(default_factory=list)

    @property
    def inherited_count(self) -> int:
        """Number of keys taken from base without override."""
        return sum(1 for e in self.entries if e.source == "base" and not e.overridden)

    @property
    def overridden_count(self) -> int:
        """Number of keys that were present in base but replaced by override."""
        return sum(1 for e in self.entries if e.overridden)

    @property
    def added_count(self) -> int:
        """Number of keys that exist only in override (not in base)."""
        return sum(1 for e in self.entries if e.source == "override" and not e.overridden)

    @property
    def result_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}


def inherit_env(
    base: Dict[str, str],
    override: Dict[str, str],
) -> Tuple[Dict[str, str], InheritReport]:
    """Merge *override* on top of *base*, returning the combined env and a report.

    Keys present only in *base* are marked as 'base'.
    Keys present in both are marked as 'merged' with overridden=True.
    Keys present only in *override* are marked as 'override'.
    """
    report = InheritReport()

    for key, base_value in base.items():
        if key in override:
            entry = InheritEntry(
                key=key,
                value=override[key],
                source="merged",
                overridden=True,
            )
        else:
            entry = InheritEntry(key=key, value=base_value, source="base", overridden=False)
        report.entries.append(entry)

    for key, ov_value in override.items():
        if key not in base:
            report.entries.append(
                InheritEntry(key=key, value=ov_value, source="override", overridden=False)
            )

    return report.result_env, report
