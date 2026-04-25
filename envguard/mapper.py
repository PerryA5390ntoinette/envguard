"""mapper.py — remap environment variable keys according to a mapping table."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MapEntry:
    original_key: str
    new_key: str
    value: str
    remapped: bool  # False when key was not found in mapping table


@dataclass
class MapReport:
    entries: List[MapEntry] = field(default_factory=list)

    def remapped_count(self) -> int:
        return sum(1 for e in self.entries if e.remapped)

    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if not e.remapped)

    def remapped_keys(self) -> List[str]:
        return [e.original_key for e in self.entries if e.remapped]

    def result_env(self) -> Dict[str, str]:
        """Return the final env dict with keys renamed per the mapping."""
        return {e.new_key: e.value for e in self.entries}


def map_env(
    env: Dict[str, str],
    mapping: Dict[str, str],
    *,
    keep_unmapped: bool = True,
) -> tuple[Dict[str, str], MapReport]:
    """Remap *env* keys according to *mapping* (old_key -> new_key).

    Parameters
    ----------
    env:
        Source environment dictionary.
    mapping:
        Dict mapping original key names to desired new key names.
    keep_unmapped:
        When *True* (default) keys not present in *mapping* are passed
        through unchanged.  When *False* they are dropped.

    Returns
    -------
    A tuple of ``(result_env, MapReport)``.
    """
    report = MapReport()

    for key, value in env.items():
        if key in mapping:
            new_key = mapping[key]
            report.entries.append(
                MapEntry(original_key=key, new_key=new_key, value=value, remapped=True)
            )
        elif keep_unmapped:
            report.entries.append(
                MapEntry(original_key=key, new_key=key, value=value, remapped=False)
            )
        # else: silently drop the key

    return report.result_env(), report
