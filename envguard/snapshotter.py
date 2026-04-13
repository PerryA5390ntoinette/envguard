"""Snapshot module: capture and compare .env state over time."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class Snapshot:
    timestamp: str
    source: str
    env: Dict[str, str]

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "env": self.env,
        }

    @staticmethod
    def from_dict(data: dict) -> "Snapshot":
        return Snapshot(
            timestamp=data["timestamp"],
            source=data["source"],
            env=data["env"],
        )


@dataclass
class SnapshotDiff:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def take_snapshot(env: Dict[str, str], source: str) -> Snapshot:
    """Create a new snapshot from the current env dict."""
    ts = datetime.now(timezone.utc).isoformat()
    return Snapshot(timestamp=ts, source=source, env=dict(env))


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot.from_dict(data)


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """Compute the difference between two snapshots."""
    result = SnapshotDiff()
    old_keys = set(old.env)
    new_keys = set(new.env)

    for key in new_keys - old_keys:
        result.added[key] = new.env[key]

    for key in old_keys - new_keys:
        result.removed[key] = old.env[key]

    for key in old_keys & new_keys:
        if old.env[key] != new.env[key]:
            result.changed[key] = (old.env[key], new.env[key])
        else:
            result.unchanged[key] = new.env[key]

    return result
