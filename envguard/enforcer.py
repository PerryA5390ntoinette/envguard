"""enforcer.py — Enforce naming conventions on .env variable keys."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


_CONVENTIONS = {
    "upper_snake": re.compile(r"^[A-Z][A-Z0-9_]*$"),
    "lower_snake": re.compile(r"^[a-z][a-z0-9_]*$"),
    "screaming_snake": re.compile(r"^[A-Z0-9][A-Z0-9_]*$"),
}


@dataclass
class EnforcementEntry:
    key: str
    value: str
    convention: str
    passed: bool
    reason: Optional[str] = None


@dataclass
class EnforcementReport:
    convention: str
    entries: List[EnforcementEntry] = field(default_factory=list)

    def violation_count(self) -> int:
        return sum(1 for e in self.entries if not e.passed)

    def ok_count(self) -> int:
        return sum(1 for e in self.entries if e.passed)

    def has_violations(self) -> bool:
        return self.violation_count() > 0

    def violations(self) -> List[EnforcementEntry]:
        return [e for e in self.entries if not e.passed]


def enforce_naming(
    env: Dict[str, str],
    convention: str = "upper_snake",
) -> EnforcementReport:
    """Check every key in *env* against the chosen naming *convention*.

    Supported conventions: ``upper_snake``, ``lower_snake``,
    ``screaming_snake``.
    """
    if convention not in _CONVENTIONS:
        raise ValueError(
            f"Unknown convention '{convention}'. "
            f"Choose from: {', '.join(_CONVENTIONS)}"
        )

    pattern = _CONVENTIONS[convention]
    report = EnforcementReport(convention=convention)

    for key, value in env.items():
        if pattern.fullmatch(key):
            report.entries.append(
                EnforcementEntry(
                    key=key,
                    value=value,
                    convention=convention,
                    passed=True,
                )
            )
        else:
            report.entries.append(
                EnforcementEntry(
                    key=key,
                    value=value,
                    convention=convention,
                    passed=False,
                    reason=f"'{key}' does not match {convention} convention",
                )
            )

    return report
