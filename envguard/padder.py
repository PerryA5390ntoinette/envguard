"""Pad missing env variables with placeholder values for safe template rendering."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_PLACEHOLDER = "PLACEHOLDER"


@dataclass
class PadEntry:
    key: str
    placeholder: str
    was_present: bool


@dataclass
class PadReport:
    entries: List[PadEntry] = field(default_factory=list)
    _padded: int = field(default=0, init=False, repr=False)
    _kept: int = field(default=0, init=False, repr=False)

    def padded_count(self) -> int:
        return self._padded

    def kept_count(self) -> int:
        return self._kept

    def padded_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.was_present]


def pad_env(
    env: Dict[str, str],
    keys: List[str],
    placeholder: Optional[str] = None,
) -> tuple:
    """Return a new env dict with missing keys filled in and a PadReport.

    Args:
        env: The current environment variables.
        keys: The complete list of expected keys.
        placeholder: Value to use for missing keys. Defaults to DEFAULT_PLACEHOLDER.

    Returns:
        A tuple of (padded_env, PadReport).
    """
    fill = placeholder if placeholder is not None else DEFAULT_PLACEHOLDER
    report = PadReport()
    result: Dict[str, str] = dict(env)

    for key in keys:
        if key in env:
            entry = PadEntry(key=key, placeholder=fill, was_present=True)
            report._kept += 1
        else:
            result[key] = fill
            entry = PadEntry(key=key, placeholder=fill, was_present=False)
            report._padded += 1
        report.entries.append(entry)

    return result, report
