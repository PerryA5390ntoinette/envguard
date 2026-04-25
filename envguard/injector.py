"""Inject variables into an env dict from external sources (OS env, defaults map)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InjectionEntry:
    key: str
    value: str
    source: str          # 'os', 'defaults', or 'override'
    replaced: bool = False  # True when an existing value was overwritten


@dataclass
class InjectionReport:
    entries: List[InjectionEntry] = field(default_factory=list)

    def add(self, entry: InjectionEntry) -> None:
        self.entries.append(entry)

    @property
    def injected_count(self) -> int:
        return len(self.entries)

    @property
    def replaced_count(self) -> int:
        return sum(1 for e in self.entries if e.replaced)

    @property
    def sources_used(self) -> List[str]:
        seen: List[str] = []
        for e in self.entries:
            if e.source not in seen:
                seen.append(e.source)
        return seen


def inject_env(
    env: Dict[str, str],
    *,
    from_os: Optional[List[str]] = None,
    defaults: Optional[Dict[str, str]] = None,
    overrides: Optional[Dict[str, str]] = None,
    overwrite: bool = False,
) -> tuple[Dict[str, str], InjectionReport]:
    """Return a new env dict with injected values and a report of changes.

    Injection order (lowest to highest priority):
      1. ``defaults``  – applied only when the key is absent.
      2. ``from_os``   – pull named keys from ``os.environ``; respects *overwrite*.
      3. ``overrides`` – always applied, replacing existing values.
    """
    result = dict(env)
    report = InjectionReport()

    # 1. defaults
    for key, value in (defaults or {}).items():
        if key not in result:
            result[key] = value
            report.add(InjectionEntry(key=key, value=value, source="defaults", replaced=False))

    # 2. os environment
    for key in (from_os or []):
        if key in os.environ:
            replaced = key in result
            if overwrite or not replaced:
                result[key] = os.environ[key]
                report.add(InjectionEntry(key=key, value=os.environ[key], source="os", replaced=replaced and overwrite))

    # 3. explicit overrides
    for key, value in (overrides or {}).items():
        replaced = key in result
        result[key] = value
        report.add(InjectionEntry(key=key, value=value, source="override", replaced=replaced))

    return result, report
