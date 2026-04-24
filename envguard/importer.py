"""Import env variables from external sources (shell environment, JSON, TOML)."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ImportEntry:
    key: str
    value: str
    source: str  # 'shell', 'json', 'toml'


@dataclass
class ImportReport:
    entries: List[ImportEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def imported_count(self) -> int:
        return len(self.entries)

    def skipped_count(self) -> int:
        return len(self.skipped)

    def result_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}


def import_from_shell(
    keys: Optional[List[str]] = None,
    prefix: Optional[str] = None,
) -> Tuple[Dict[str, str], ImportReport]:
    """Import variables from the current shell environment.

    Args:
        keys: If provided, only import variables whose names are in this list.
        prefix: If provided, only import variables whose names start with this prefix.

    Returns:
        A tuple of (env dict, ImportReport).
    """
    report = ImportReport()
    env: Dict[str, str] = {}

    for k, v in os.environ.items():
        if keys is not None and k not in keys:
            report.skipped.append(k)
            continue
        if prefix is not None and not k.startswith(prefix):
            report.skipped.append(k)
            continue
        entry = ImportEntry(key=k, value=v, source="shell")
        report.entries.append(entry)
        env[k] = v

    return env, report


def import_from_json(
    path: str,
    prefix: Optional[str] = None,
) -> Tuple[Dict[str, str], ImportReport]:
    """Import variables from a JSON file (flat key-value object).

    Args:
        path: Path to the JSON file to read.
        prefix: If provided, only import keys that start with this prefix.

    Raises:
        ValueError: If the JSON file does not contain a top-level object, or if
            a key is not a string.

    Returns:
        A tuple of (env dict, ImportReport).
    """
    report = ImportReport()
    env: Dict[str, str] = {}

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path!r}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object at the top level in {path!r}")

    for k, v in data.items():
        if not isinstance(k, str):
            raise ValueError(
                f"All keys in {path!r} must be strings; got {type(k).__name__!r}"
            )
        if not isinstance(v, (str, int, float, bool)):
            report.skipped.append(k)
            continue
        if prefix is not None and not k.startswith(prefix):
            report.skipped.append(k)
            continue
        str_val = str(v)
        entry = ImportEntry(key=k, value=str_val, source="json")
        report.entries.append(entry)
        env[k] = str_val

    return env, report


def merge_into(
    base: Dict[str, str],
    incoming: Dict[str, str],
    overwrite: bool = False,
) -> Dict[str, str]:
    """Merge *incoming* into *base*, optionally overwriting existing keys."""
    result = dict(base)
    for k, v in incoming.items():
        if k not in result or overwrite:
            result[k] = v
    return result
