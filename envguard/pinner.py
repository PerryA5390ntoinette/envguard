"""Pin resolved environment variable values to a lockfile for reproducible deployments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import hashlib


@dataclass
class PinEntry:
    key: str
    value: str
    checksum: str


@dataclass
class PinReport:
    entries: List[PinEntry] = field(default_factory=list)
    source: str = ""

    def pinned_count(self) -> int:
        return len(self.entries)

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def checksums(self) -> Dict[str, str]:
        return {e.key: e.checksum for e in self.entries}


def _checksum(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def pin_env(env: Dict[str, str], source: str = "") -> PinReport:
    """Create a pin report capturing current values and their checksums."""
    report = PinReport(source=source)
    for key in sorted(env.keys()):
        value = env[key]
        report.entries.append(PinEntry(key=key, value=value, checksum=_checksum(value)))
    return report


def save_pinfile(report: PinReport, path: str) -> None:
    """Persist a pin report to a JSON lockfile."""
    data = {
        "source": report.source,
        "pins": [
            {"key": e.key, "value": e.value, "checksum": e.checksum}
            for e in report.entries
        ],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_pinfile(path: str) -> PinReport:
    """Load a previously saved pin report from a JSON lockfile."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    report = PinReport(source=data.get("source", ""))
    for item in data.get("pins", []):
        report.entries.append(
            PinEntry(key=item["key"], value=item["value"], checksum=item["checksum"])
        )
    return report


@dataclass
class PinDrift:
    key: str
    pinned_value: str
    current_value: str
    pinned_checksum: str
    current_checksum: str


def detect_drift(pinned: PinReport, current: Dict[str, str]) -> List[PinDrift]:
    """Compare a pinned report against current env values and return drifted entries."""
    drifts: List[PinDrift] = []
    pin_map = {e.key: e for e in pinned.entries}
    for key, value in current.items():
        if key in pin_map:
            entry = pin_map[key]
            current_cs = _checksum(value)
            if current_cs != entry.checksum:
                drifts.append(
                    PinDrift(
                        key=key,
                        pinned_value=entry.value,
                        current_value=value,
                        pinned_checksum=entry.checksum,
                        current_checksum=current_cs,
                    )
                )
    return drifts
