"""Summarizer: produces a high-level human-readable summary of a pipeline result."""

from dataclasses import dataclass, field
from typing import List

from envguard.pipeline import PipelineResult


@dataclass
class SummaryLine:
    icon: str
    label: str
    value: str


@dataclass
class SummaryReport:
    source: str
    lines: List[SummaryLine] = field(default_factory=list)

    def add(self, icon: str, label: str, value: str) -> None:
        self.lines.append(SummaryLine(icon=icon, label=label, value=value))


def summarize(result: PipelineResult) -> SummaryReport:
    """Build a SummaryReport from a PipelineResult."""
    source = ", ".join(result.sources) if result.sources else "<unknown>"
    report = SummaryReport(source=source)

    total_vars = len(result.raw_env)
    report.add("📦", "Variables loaded", str(total_vars))

    audit = result.audit_report
    if audit is not None:
        errors = len([r for r in audit.results if r.status == "error"])
        warnings = len([r for r in audit.results if r.status == "warning"])
        passed = len([r for r in audit.results if r.status == "pass"])
        report.add("❌", "Audit errors", str(errors))
        report.add("⚠️ ", "Audit warnings", str(warnings))
        report.add("✅", "Audit passed", str(passed))

    interp = result.interpolation_report
    if interp is not None:
        warn_count = len(interp.warnings)
        report.add("🔗", "Interpolation warnings", str(warn_count))

    lint = result.lint_report
    if lint is not None:
        lint_errors = lint.error_count()
        lint_warnings = lint.warning_count()
        report.add("🔍", "Lint errors", str(lint_errors))
        report.add("🔍", "Lint warnings", str(lint_warnings))

    score = result.score_report
    if score is not None:
        report.add("🏆", "Score", f"{score.score}/100 (Grade {score.grade})")

    return report
