"""Flattener: collapses nested key structures (e.g. APP__DB__HOST) into dot or underscore notation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenEntry:
    original_key: str
    flattened_key: str
    depth: int
    changed: bool


@dataclass
class FlattenReport:
    entries: List[FlattenEntry] = field(default_factory=list)

    def add(self, entry: FlattenEntry) -> None:
        self.entries.append(entry)

    @property
    def changed_count(self) -> int:
        return sum(1 for e in self.entries if e.changed)

    @property
    def unchanged_count(self) -> int:
        return sum(1 for e in self.entries if not e.changed)

    @property
    def max_depth(self) -> int:
        if not self.entries:
            return 0
        return max(e.depth for e in self.entries)

    @property
    def result_env(self) -> Dict[str, str]:
        return {}


def _flatten_key(key: str, separator: str = "__", output_sep: str = ".") -> str:
    """Replace internal separator with output separator and lowercase segments."""
    if separator not in key:
        return key
    parts = key.split(separator)
    return output_sep.join(p.lower() for p in parts)


def _depth(key: str, separator: str = "__") -> int:
    return key.count(separator)


def flatten_env(
    env: Dict[str, str],
    separator: str = "__",
    output_sep: str = ".",
) -> tuple[Dict[str, str], FlattenReport]:
    """Flatten env keys that use *separator* as a nesting delimiter."""
    report = FlattenReport()
    result: Dict[str, str] = {}

    for key, value in env.items():
        flat_key = _flatten_key(key, separator=separator, output_sep=output_sep)
        depth = _depth(key, separator=separator)
        changed = flat_key != key
        entry = FlattenEntry(
            original_key=key,
            flattened_key=flat_key,
            depth=depth,
            changed=changed,
        )
        report.add(entry)
        result[flat_key] = value

    return result, report
