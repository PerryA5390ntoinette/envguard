"""Traces the origin of each variable across multiple .env sources."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TraceEntry:
    key: str
    value: str
    source: str
    overridden_by: Optional[str] = None
    previous_value: Optional[str] = None

    @property
    def was_overridden(self) -> bool:
        return self.overridden_by is not None


@dataclass
class TraceReport:
    entries: List[TraceEntry] = field(default_factory=list)

    def add(self, entry: TraceEntry) -> None:
        self.entries.append(entry)

    def for_key(self, key: str) -> List[TraceEntry]:
        return [e for e in self.entries if e.key == key]

    @property
    def overridden_count(self) -> int:
        return sum(1 for e in self.entries if e.was_overridden)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def all_keys(self) -> List[str]:
        seen: List[str] = []
        for e in self.entries:
            if e.key not in seen:
                seen.append(e.key)
        return seen


def trace_envs(sources: List[Dict[str, str]], source_names: List[str]) -> TraceReport:
    """Trace variable origins across ordered env sources (later sources override earlier)."""
    report = TraceReport()
    accumulated: Dict[str, TraceEntry] = {}

    for env, name in zip(sources, source_names):
        for key, value in env.items():
            if key in accumulated:
                prev = accumulated[key]
                prev.overridden_by = name
                report.add(prev)
                entry = TraceEntry(
                    key=key,
                    value=value,
                    source=name,
                    previous_value=prev.value,
                )
            else:
                entry = TraceEntry(key=key, value=value, source=name)
            accumulated[key] = entry

    for entry in accumulated.values():
        report.add(entry)

    return report
