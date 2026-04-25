"""Clone an env dict with optional key remapping and value overrides."""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CloneEntry:
    key: str
    original_key: str
    value: str
    was_remapped: bool
    was_overridden: bool


@dataclass
class CloneReport:
    entries: list = field(default_factory=list)

    def add(self, entry: CloneEntry) -> None:
        self.entries.append(entry)

    @property
    def remapped_count(self) -> int:
        return sum(1 for e in self.entries if e.was_remapped)

    @property
    def overridden_count(self) -> int:
        return sum(1 for e in self.entries if e.was_overridden)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def result_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}


def clone_env(
    env: Dict[str, str],
    key_map: Optional[Dict[str, str]] = None,
    overrides: Optional[Dict[str, str]] = None,
) -> tuple:
    """Return a cloned env dict plus a CloneReport.

    Args:
        env: Source environment mapping.
        key_map: Optional mapping of old_key -> new_key for renaming.
        overrides: Optional mapping of key -> value to override after cloning.

    Returns:
        Tuple of (cloned_env, CloneReport).
    """
    key_map = key_map or {}
    overrides = overrides or {}
    report = CloneReport()

    for original_key, value in env.items():
        new_key = key_map.get(original_key, original_key)
        was_remapped = new_key != original_key

        if new_key in overrides:
            final_value = overrides[new_key]
            was_overridden = True
        else:
            final_value = value
            was_overridden = False

        report.add(CloneEntry(
            key=new_key,
            original_key=original_key,
            value=final_value,
            was_remapped=was_remapped,
            was_overridden=was_overridden,
        ))

    return report.result_env, report
