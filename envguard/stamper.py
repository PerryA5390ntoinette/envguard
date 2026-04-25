"""Stamper: injects metadata stamps (timestamps, version, env name) into env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class StampEntry:
    key: str
    value: str
    injected: bool  # True = newly added, False = already existed / skipped


@dataclass
class StampReport:
    entries: List[StampEntry] = field(default_factory=list)

    @property
    def injected_count(self) -> int:
        return sum(1 for e in self.entries if e.injected)

    @property
    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if not e.injected)

    @property
    def injected_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.injected]


def stamp_env(
    env: Dict[str, str],
    *,
    timestamp_key: Optional[str] = "ENVGUARD_STAMPED_AT",
    version: Optional[str] = None,
    version_key: Optional[str] = "ENVGUARD_VERSION",
    env_name: Optional[str] = None,
    env_name_key: Optional[str] = "ENVGUARD_ENV",
    overwrite: bool = False,
) -> tuple[Dict[str, str], StampReport]:
    """Return a new env dict with metadata stamps injected and a report."""
    result = dict(env)
    report = StampReport()

    def _inject(key: str, value: str) -> None:
        if key is None:
            return
        already_present = key in result
        if already_present and not overwrite:
            report.entries.append(StampEntry(key=key, value=result[key], injected=False))
        else:
            result[key] = value
            report.entries.append(StampEntry(key=key, value=value, injected=True))

    if timestamp_key:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _inject(timestamp_key, ts)

    if version is not None and version_key:
        _inject(version_key, version)

    if env_name is not None and env_name_key:
        _inject(env_name_key, env_name)

    return result, report
