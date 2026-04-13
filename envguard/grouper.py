"""Groups environment variables by prefix or custom rules."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class GroupEntry:
    key: str
    value: str
    group: str


@dataclass
class GroupReport:
    groups: Dict[str, List[GroupEntry]] = field(default_factory=dict)
    ungrouped: List[GroupEntry] = field(default_factory=list)

    def all_groups(self) -> List[str]:
        return sorted(self.groups.keys())

    def entries_for(self, group: str) -> List[GroupEntry]:
        return self.groups.get(group, [])

    def total(self) -> int:
        count = len(self.ungrouped)
        for entries in self.groups.values():
            count += len(entries)
        return count


def _extract_prefix(key: str, separator: str = "_") -> Tuple[str, bool]:
    """Return (prefix, had_prefix). Prefix is the part before the first separator."""
    if separator in key:
        prefix, _ = key.split(separator, 1)
        return prefix.upper(), True
    return key.upper(), False


def group_env(
    env: Dict[str, str],
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupReport:
    """Group variables by their key prefix.

    Variables whose prefix appears fewer than *min_group_size* times are
    placed in the ungrouped bucket.
    """
    report = GroupReport()
    prefix_map: Dict[str, List[GroupEntry]] = {}

    for key, value in env.items():
        prefix, had_prefix = _extract_prefix(key, separator)
        entry = GroupEntry(key=key, value=value, group=prefix if had_prefix else "")
        if had_prefix:
            prefix_map.setdefault(prefix, []).append(entry)
        else:
            report.ungrouped.append(entry)

    for prefix, entries in prefix_map.items():
        if len(entries) >= min_group_size:
            report.groups[prefix] = entries
        else:
            report.ungrouped.extend(entries)

    return report
