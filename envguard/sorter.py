"""Sort .env file variables alphabetically or by group prefix."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortReport:
    original_order: List[str] = field(default_factory=list)
    sorted_order: List[str] = field(default_factory=list)
    sorted_env: Dict[str, str] = field(default_factory=dict)
    mode: str = "alpha"

    @property
    def is_already_sorted(self) -> bool:
        return self.original_order == self.sorted_order

    @property
    def moved_count(self) -> int:
        return sum(
            1 for i, key in enumerate(self.sorted_order)
            if i >= len(self.original_order) or self.original_order[i] != key
        )


def _extract_prefix(key: str) -> str:
    """Return the prefix of a key (part before the first underscore)."""
    if "_" in key:
        return key.split("_")[0]
    return key


def sort_env(
    env: Dict[str, str],
    mode: str = "alpha",
) -> SortReport:
    """Sort environment variables.

    Args:
        env: Mapping of variable names to values.
        mode: Sorting strategy — 'alpha' for alphabetical, 'group' for
              prefix-grouped then alphabetical within each group.

    Returns:
        A SortReport with the sorted result and metadata.
    """
    original_keys = list(env.keys())

    if mode == "group":
        sorted_keys = sorted(
            original_keys,
            key=lambda k: (_extract_prefix(k).lower(), k.lower()),
        )
    else:
        sorted_keys = sorted(original_keys, key=str.lower)

    sorted_env = {k: env[k] for k in sorted_keys}

    return SortReport(
        original_order=original_keys,
        sorted_order=sorted_keys,
        sorted_env=sorted_env,
        mode=mode,
    )
