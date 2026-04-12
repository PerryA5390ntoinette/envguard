"""Variable interpolation for .env files.

Supports ${VAR} and $VAR style references within values.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationWarning:
    variable: str
    reference: str
    message: str


@dataclass
class InterpolationReport:
    resolved: Dict[str, str] = field(default_factory=dict)
    warnings: List[InterpolationWarning] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


def _resolve_value(
    key: str,
    value: str,
    env: Dict[str, str],
    warnings: List[InterpolationWarning],
    visited: Optional[set] = None,
) -> str:
    if visited is None:
        visited = set()
    if key in visited:
        warnings.append(
            InterpolationWarning(
                variable=key,
                reference=key,
                message=f"Circular reference detected for '{key}'",
            )
        )
        return value
    visited = visited | {key}

    def replacer(match: re.Match) -> str:
        ref = match.group(1) or match.group(2)
        if ref not in env:
            warnings.append(
                InterpolationWarning(
                    variable=key,
                    reference=ref,
                    message=f"'{key}' references undefined variable '{ref}'",
                )
            )
            return match.group(0)
        return _resolve_value(ref, env[ref], env, warnings, visited)

    return _REF_PATTERN.sub(replacer, value)


def interpolate(env: Dict[str, str]) -> InterpolationReport:
    """Resolve all variable references in *env* and return an InterpolationReport."""
    report = InterpolationReport()
    for key, raw_value in env.items():
        resolved = _resolve_value(key, raw_value, env, report.warnings)
        report.resolved[key] = resolved
    return report
