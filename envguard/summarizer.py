"""Summarizer — condenses a PipelineResult into a single-line SummaryReport."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SummaryLine:
    source: str
    variables_loaded: int
    audit_errors: int
    audit_warnings: int
    audit_passed: int
    lint_issues: int
    interpolation_warnings: int


class SummaryReport:
    def __init__(self) -> None:
        self._lines: List[SummaryLine] = []

    def add(self, line: SummaryLine) -> None:
        self._lines.append(line)

    # Aggregate helpers — sum across all lines for multi-source use
    @property
    def source(self) -> str:
        if not self._lines:
            return "unknown"
        return self._lines[0].source

    @property
    def variables_loaded(self) -> int:
        return sum(l.variables_loaded for l in self._lines)

    @property
    def audit_errors(self) -> int:
        return sum(l.audit_errors for l in self._lines)

    @property
    def audit_warnings(self) -> int:
        return sum(l.audit_warnings for l in self._lines)

    @property
    def audit_passed(self) -> int:
        return sum(l.audit_passed for l in self._lines)

    @property
    def lint_issues(self) -> int:
        return sum(l.lint_issues for l in self._lines)

    @property
    def interpolation_warnings(self) -> int:
        return sum(l.interpolation_warnings for l in self._lines)


def summarize(pipeline_result: object) -> SummaryReport:
    """Build a SummaryReport from a PipelineResult."""
    report = SummaryReport()

    sources = getattr(pipeline_result, "sources", [])
    source_label = sources[0] if sources else "unknown"

    raw_env = getattr(pipeline_result, "raw_env", {}) or {}
    variables_loaded = len(raw_env)

    audit_report = getattr(pipeline_result, "audit_report", None)
    audit_errors = len(audit_report.errors) if audit_report else 0
    audit_warnings = len(audit_report.warnings) if audit_report else 0
    audit_passed = len(audit_report.passed) if audit_report else 0

    lint_report = getattr(pipeline_result, "lint_report", None)
    lint_issues = lint_report.error_count() if lint_report else 0

    interp_report = getattr(pipeline_result, "interpolation_report", None)
    interp_warnings = (
        len(interp_report.warnings) if interp_report else 0
    )

    line = SummaryLine(
        source=source_label,
        variables_loaded=variables_loaded,
        audit_errors=audit_errors,
        audit_warnings=audit_warnings,
        audit_passed=audit_passed,
        lint_issues=lint_issues,
        interpolation_warnings=interp_warnings,
    )
    report.add(line)
    return report
