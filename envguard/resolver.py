"""Resolve final effective values for env variables across multiple layers.

Layers are applied in order: earlier layers are base, later layers override.
Each entry records the key, final value, which layer it came from, and whether
it was overridden by a higher-priority layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ResolveEntry:
    key: str
    value: str
    source: str          # label of the winning layer
    overridden_by: Optional[str] = None   # label of layer that overrode a previous value
    original_value: Optional[str] = None  # value before override


@dataclass
class ResolveReport:
    entries: List[ResolveEntry] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    # --- convenience accessors ---

    def resolved_count(self) -> int:
        return len(self.entries)

    def overridden_count(self) -> int:
        return sum(1 for e in self.entries if e.overridden_by is not None)

    def result_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def for_key(self, key: str) -> Optional[ResolveEntry]:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None


def resolve_layers(
    layers: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
) -> ResolveReport:
    """Merge *layers* left-to-right; later layers win.

    Parameters
    ----------
    layers:
        Ordered list of env dicts.  Index 0 is the lowest-priority base.
    labels:
        Human-readable name for each layer (e.g. ``[".env.defaults", ".env"]``).
        If omitted, layers are labelled ``layer_0``, ``layer_1``, …
    """
    if labels is None:
        labels = [f"layer_{i}" for i in range(len(layers))]

    if len(labels) != len(layers):
        raise ValueError("labels length must match layers length")

    report = ResolveReport(sources=list(labels))

    # key -> (value, source_label)
    resolved: Dict[str, tuple[str, str]] = {}
    # key -> (original_value, overriding_label)
    override_info: Dict[str, tuple[str, str]] = {}

    for label, layer in zip(labels, layers):
        for key, value in layer.items():
            if key in resolved:
                prev_value, _prev_label = resolved[key]
                if value != prev_value:
                    override_info[key] = (prev_value, label)
            resolved[key] = (value, label)

    for key, (value, source) in sorted(resolved.items()):
        if key in override_info:
            orig_val, overriding_label = override_info[key]
            entry = ResolveEntry(
                key=key,
                value=value,
                source=source,
                overridden_by=overriding_label,
                original_value=orig_val,
            )
        else:
            entry = ResolveEntry(key=key, value=value, source=source)
        report.entries.append(entry)

    return report
