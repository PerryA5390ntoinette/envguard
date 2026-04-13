"""Rename variables across an env dict, tracking what changed."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameEntry:
    old_name: str
    new_name: str
    value: str
    skipped: bool = False
    skip_reason: Optional[str] = None


@dataclass
class RenameReport:
    entries: List[RenameEntry] = field(default_factory=list)

    def renamed_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped)

    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.skipped)


def rename_vars(
    env: Dict[str, str],
    renames: Dict[str, str],
    *,
    overwrite: bool = False,
) -> tuple[Dict[str, str], RenameReport]:
    """Return a new env dict with keys renamed according to *renames*.

    Args:
        env:       Original environment mapping.
        renames:   Mapping of {old_name: new_name}.
        overwrite: If True, overwrite an existing key at new_name.
                   If False (default) the rename is skipped when new_name
                   already exists in env.

    Returns:
        A tuple of (new_env, RenameReport).
    """
    result: Dict[str, str] = dict(env)
    report = RenameReport()

    for old, new in renames.items():
        if old not in result:
            report.entries.append(
                RenameEntry(
                    old_name=old,
                    new_name=new,
                    value="",
                    skipped=True,
                    skip_reason="source key not found",
                )
            )
            continue

        if new in result and not overwrite:
            report.entries.append(
                RenameEntry(
                    old_name=old,
                    new_name=new,
                    value=result[old],
                    skipped=True,
                    skip_reason=f"target key '{new}' already exists",
                )
            )
            continue

        value = result.pop(old)
        result[new] = value
        report.entries.append(RenameEntry(old_name=old, new_name=new, value=value))

    return result, report
