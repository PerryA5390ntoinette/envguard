"""Split a flat env dict into multiple named buckets by prefix or explicit mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitEntry:
    key: str
    value: str
    bucket: str


@dataclass
class SplitReport:
    entries: List[SplitEntry] = field(default_factory=list)
    _buckets: Dict[str, Dict[str, str]] = field(default_factory=dict, repr=False)

    def add(self, entry: SplitEntry) -> None:
        self.entries.append(entry)
        self._buckets.setdefault(entry.bucket, {})[entry.key] = entry.value

    @property
    def bucket_names(self) -> List[str]:
        return list(self._buckets.keys())

    def env_for(self, bucket: str) -> Dict[str, str]:
        return dict(self._buckets.get(bucket, {}))

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def bucket_count(self) -> int:
        return len(self._buckets)


def _resolve_bucket(
    key: str,
    prefix_map: Dict[str, str],
    default_bucket: str,
) -> str:
    """Return the bucket name for *key* by longest-prefix match."""
    best: Optional[str] = None
    best_len = -1
    for prefix, bucket in prefix_map.items():
        if key.startswith(prefix) and len(prefix) > best_len:
            best = bucket
            best_len = len(prefix)
    return best if best is not None else default_bucket


def split_env(
    env: Dict[str, str],
    prefix_map: Optional[Dict[str, str]] = None,
    default_bucket: str = "default",
) -> SplitReport:
    """Split *env* into buckets according to *prefix_map*.

    Parameters
    ----------
    env:
        The flat environment dictionary to split.
    prefix_map:
        A mapping of key-prefix -> bucket name.  The longest matching prefix
        wins.  Keys that match no prefix land in *default_bucket*.
    default_bucket:
        Name used for keys that do not match any prefix.
    """
    if prefix_map is None:
        prefix_map = {}

    report = SplitReport()
    for key, value in env.items():
        bucket = _resolve_bucket(key, prefix_map, default_bucket)
        report.add(SplitEntry(key=key, value=value, bucket=bucket))
    return report
