"""Suggests fixes for common .env validation errors."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from envguard.validator import ValidationReport, ValidationResult


@dataclass
class Suggestion:
    variable: str
    message: str
    fix: Optional[str] = None


@dataclass
class SuggestionReport:
    suggestions: List[Suggestion] = field(default_factory=list)

    def add(self, suggestion: Suggestion) -> None:
        self.suggestions.append(suggestion)

    @property
    def has_suggestions(self) -> bool:
        return len(self.suggestions) > 0


def _suggest_for_result(result: ValidationResult) -> Optional[Suggestion]:
    """Derive a suggestion from a single ValidationResult error message."""
    msg = result.message.lower()
    var = result.variable

    if "missing" in msg and "required" in msg:
        return Suggestion(
            variable=var,
            message=f"'{var}' is required but not set.",
            fix=f"{var}=<value>",
        )

    if "pattern" in msg or "does not match" in msg:
        pattern_match = re.search(r"pattern[:\s]+([^\s]+)", result.message, re.IGNORECASE)
        pattern_hint = pattern_match.group(1) if pattern_match else "<expected pattern>"
        return Suggestion(
            variable=var,
            message=f"'{var}' value does not match the required pattern.",
            fix=f"Ensure {var} matches: {pattern_hint}",
        )

    if "allowed" in msg or "not one of" in msg:
        allowed_match = re.search(r"allowed values[:\s]+([^.]+)", result.message, re.IGNORECASE)
        allowed_hint = allowed_match.group(1).strip() if allowed_match else "<allowed values>"
        return Suggestion(
            variable=var,
            message=f"'{var}' has an invalid value.",
            fix=f"Set {var} to one of: {allowed_hint}",
        )

    if "unknown" in msg:
        return Suggestion(
            variable=var,
            message=f"'{var}' is not defined in the schema.",
            fix=f"Remove {var} or add it to the schema.",
        )

    return None


def suggest(report: ValidationReport) -> SuggestionReport:
    """Generate suggestions for all errors in a ValidationReport."""
    suggestion_report = SuggestionReport()
    for result in report.results:
        if result.status == "error":
            suggestion = _suggest_for_result(result)
            if suggestion:
                suggestion_report.add(suggestion)
    return suggestion_report
