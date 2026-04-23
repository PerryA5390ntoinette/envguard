"""aliaser.py – map deprecated or alternate variable names to canonical names."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class AliasEntry:
    alias: str
    canonical: str
    value: str
    resolved: bool  # True if alias was found and remapped


@dataclass
class AliasReport:
    entries: List[AliasEntry] = field(default_factory=list)
    result_env: Dict[str, str] = field(default_factory=dict)

    def resolved_count(self) -> int:
        return sum(1 for e in self.entries if e.resolved)

    def unresolved_count(self) -> int:
        return sum(1 for e in self.entries if not e.resolved)

    def resolved_keys(self) -> List[str]:
        return [e.alias for e in self.entries if e.resolved]


def apply_aliases(
    env: Dict[str, str],
    alias_map: Dict[str, str],  # {alias: canonical}
    *,
    overwrite: bool = False,
) -> Tuple[Dict[str, str], AliasReport]:
    """Return a new env dict with aliases remapped to canonical names.

    Args:
        env: The source environment dictionary.
        alias_map: Mapping of alias name -> canonical name.
        overwrite: If True, canonical key is overwritten when both exist.

    Returns:
        A tuple of (new_env, AliasReport).
    """
    report = AliasReport()
    new_env: Dict[str, str] = dict(env)

    for alias, canonical in alias_map.items():
        if alias not in env:
            continue
        value = env[alias]
        should_write = overwrite or canonical not in new_env
        if should_write:
            new_env[canonical] = value
        del new_env[alias]
        report.entries.append(
            AliasEntry(
                alias=alias,
                canonical=canonical,
                value=value,
                resolved=should_write,
            )
        )

    report.result_env = new_env
    return new_env, report
