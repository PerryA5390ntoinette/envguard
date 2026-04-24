"""Freeze an env dict into a locked snapshot that detects any drift."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FreezeEntry:
    key: str
    value: str
    frozen_hash: str
    current_hash: str
    drifted: bool


@dataclass
class FreezeReport:
    entries: List[FreezeEntry] = field(default_factory=list)

    @property
    def drifted_count(self) -> int:
        return sum(1 for e in self.entries if e.drifted)

    @property
    def stable_count(self) -> int:
        return sum(1 for e in self.entries if not e.drifted)

    @property
    def has_drift(self) -> bool:
        return self.drifted_count > 0

    @property
    def drifted_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.drifted]


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def freeze_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a dict mapping each key to its value hash (the freeze manifest)."""
    return {key: _hash_value(value) for key, value in env.items()}


def check_freeze(
    env: Dict[str, str],
    manifest: Dict[str, str],
    *,
    ignore_new: bool = False,
) -> FreezeReport:
    """Compare *env* against a previously frozen *manifest*.

    Args:
        env: Current environment variables.
        manifest: Mapping of key -> frozen hash produced by :func:`freeze_env`.
        ignore_new: When True, keys present in *env* but absent from the
            manifest are not reported as drifted.
    """
    report = FreezeReport()
    all_keys = set(manifest) | (set(env) if not ignore_new else set(manifest))

    for key in sorted(all_keys):
        current_value = env.get(key, "")
        current_hash = _hash_value(current_value)
        frozen_hash = manifest.get(key, "")

        if key not in manifest and ignore_new:
            continue

        drifted = current_hash != frozen_hash
        report.entries.append(
            FreezeEntry(
                key=key,
                value=current_value,
                frozen_hash=frozen_hash,
                current_hash=current_hash,
                drifted=drifted,
            )
        )
    return report
