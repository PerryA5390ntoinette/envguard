"""Compare two .env files and report differences in keys and values."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envguard.loader import load_env_file


@dataclass
class DiffEntry:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class DiffReport:
    entries: List[DiffEntry] = field(default_factory=list)

    @property
    def added(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def changed(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == "changed"]

    @property
    def unchanged(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == "unchanged"]

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def diff_env_files(base_path: str, target_path: str) -> DiffReport:
    """Compare two .env files and return a DiffReport."""
    base: Dict[str, str] = load_env_file(base_path)
    target: Dict[str, str] = load_env_file(target_path)

    report = DiffReport()
    all_keys = set(base.keys()) | set(target.keys())

    for key in sorted(all_keys):
        in_base = key in base
        in_target = key in target

        if in_base and not in_target:
            report.entries.append(DiffEntry(key=key, status="removed", old_value=base[key]))
        elif in_target and not in_base:
            report.entries.append(DiffEntry(key=key, status="added", new_value=target[key]))
        elif base[key] != target[key]:
            report.entries.append(
                DiffEntry(key=key, status="changed", old_value=base[key], new_value=target[key])
            )
        else:
            report.entries.append(
                DiffEntry(key=key, status="unchanged", old_value=base[key], new_value=target[key])
            )

    return report
