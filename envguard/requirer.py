"""requirer.py – checks which variables are required but missing a value (empty string)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.schema import EnvSchema


@dataclass
class RequireEntry:
    key: str
    required: bool
    value: str | None  # None = absent, "" = present but empty
    flagged: bool


@dataclass
class RequireReport:
    entries: List[RequireEntry] = field(default_factory=list)

    def flagged_count(self) -> int:
        return sum(1 for e in self.entries if e.flagged)

    def ok_count(self) -> int:
        return sum(1 for e in self.entries if not e.flagged)

    def has_issues(self) -> bool:
        return self.flagged_count() > 0

    def flagged_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.flagged]


def check_required(env: Dict[str, str], schema: EnvSchema) -> RequireReport:
    """Flag every required variable that is absent or has an empty value."""
    report = RequireReport()

    for name, var in schema.variables.items():
        if not var.required:
            continue
        value = env.get(name)  # None if absent
        flagged = value is None or value.strip() == ""
        report.entries.append(
            RequireEntry(
                key=name,
                required=True,
                value=value,
                flagged=flagged,
            )
        )

    # Also include optional keys present in env so callers get a full picture
    for key, value in env.items():
        if key in schema.variables and not schema.variables[key].required:
            report.entries.append(
                RequireEntry(
                    key=key,
                    required=False,
                    value=value,
                    flagged=False,
                )
            )

    return report
