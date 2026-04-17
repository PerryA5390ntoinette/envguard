"""Detects stale variables — keys present in .env but absent from schema for a long time."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envguard.schema import EnvSchema


@dataclass
class StaleEntry:
    key: str
    value: str
    reason: str


@dataclass
class StaleReport:
    entries: List[StaleEntry] = field(default_factory=list)

    def add(self, entry: StaleEntry) -> None:
        self.entries.append(entry)

    @property
    def stale_count(self) -> int:
        return len(self.entries)

    @property
    def has_stale(self) -> bool:
        return bool(self.entries)

    @property
    def stale_keys(self) -> List[str]:
        return [e.key for e in self.entries]


def detect_stale(
    env: Dict[str, str],
    schema: EnvSchema,
    allowlist: Optional[List[str]] = None,
) -> StaleReport:
    """Return a StaleReport listing env keys not defined in schema."""
    allowlist = allowlist or []
    known_keys = set(schema.variables.keys())
    report = StaleReport()
    for key, value in env.items():
        if key in known_keys or key in allowlist:
            continue
        report.add(StaleEntry(
            key=key,
            value=value,
            reason="Key is not defined in the schema",
        ))
    return report
