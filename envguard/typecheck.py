"""Type-checking module: validates env variable values against declared types."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_INT_RE = re.compile(r'^-?\d+$')
_FLOAT_RE = re.compile(r'^-?\d+(\.\d+)?([eE][+-]?\d+)?$')
_BOOL_VALUES = {"true", "false", "1", "0", "yes", "no", "on", "off"}
_URL_RE = re.compile(r'^https?://.+', re.IGNORECASE)


@dataclass
class TypeIssue:
    key: str
    value: str
    expected_type: str
    message: str


@dataclass
class TypeReport:
    issues: List[TypeIssue] = field(default_factory=list)
    passed: List[str] = field(default_factory=list)

    def add_issue(self, key: str, value: str, expected_type: str, message: str) -> None:
        self.issues.append(TypeIssue(key=key, value=value, expected_type=expected_type, message=message))

    def add_passed(self, key: str) -> None:
        self.passed.append(key)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def _check_type(key: str, value: str, expected_type: str) -> Optional[str]:
    """Return an error message if value does not match expected_type, else None."""
    t = expected_type.lower().strip()
    if t == "int":
        if not _INT_RE.match(value):
            return f"Expected integer, got '{value}'"
    elif t == "float":
        if not _FLOAT_RE.match(value):
            return f"Expected float, got '{value}'"
    elif t == "bool":
        if value.lower() not in _BOOL_VALUES:
            return f"Expected boolean (true/false/1/0/yes/no), got '{value}'"
    elif t == "url":
        if not _URL_RE.match(value):
            return f"Expected URL starting with http:// or https://, got '{value}'"
    elif t == "nonempty":
        if not value.strip():
            return "Expected non-empty value, got empty string"
    # unknown or 'string' type: always passes
    return None


def typecheck_env(env: Dict[str, str], type_map: Dict[str, str]) -> TypeReport:
    """Check each key in type_map against the corresponding value in env.

    Keys present in type_map but absent from env are skipped (the auditor
    handles missing-required logic separately).
    """
    report = TypeReport()
    for key, expected_type in type_map.items():
        if key not in env:
            continue
        value = env[key]
        error_msg = _check_type(key, value, expected_type)
        if error_msg:
            report.add_issue(key, value, expected_type, error_msg)
        else:
            report.add_passed(key)
    return report
