"""Defaulter: fills in missing env variables using schema-defined defaults."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envguard.schema import EnvSchema


@dataclass
class DefaultEntry:
    key: str
    default_value: str
    was_present: bool


@dataclass
class DefaultReport:
    entries: List[DefaultEntry] = field(default_factory=list)
    _filled: List[str] = field(default_factory=list, repr=False)
    _skipped: List[str] = field(default_factory=list, repr=False)

    def filled_count(self) -> int:
        return len(self._filled)

    def skipped_count(self) -> int:
        return len(self._skipped)

    def filled_keys(self) -> List[str]:
        return list(self._filled)

    def result_env(self) -> Dict[str, str]:
        return {e.key: e.default_value for e in self.entries if not e.was_present}


def apply_defaults(
    env: Dict[str, str],
    schema: EnvSchema,
    overwrite: bool = False,
) -> tuple[Dict[str, str], DefaultReport]:
    """Return a new env dict with schema defaults applied for missing keys.

    Args:
        env: The current environment variables.
        schema: The schema containing variable definitions with defaults.
        overwrite: If True, apply default even when key is already present.

    Returns:
        A tuple of (updated_env, DefaultReport).
    """
    report = DefaultReport()
    updated = dict(env)

    for var in schema.variables:
        if var.default is None:
            continue

        was_present = var.name in env
        entry = DefaultEntry(
            key=var.name,
            default_value=var.default,
            was_present=was_present,
        )
        report.entries.append(entry)

        if not was_present or overwrite:
            updated[var.name] = var.default
            report._filled.append(var.name)
        else:
            report._skipped.append(var.name)

    return updated, report
