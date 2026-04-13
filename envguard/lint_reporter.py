"""Formats and prints LintReport output for the CLI."""
from typing import Optional
from envguard.linter import LintReport, LintIssue

_RESET = "\033[0m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_BOLD = "\033[1m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def _severity_label(severity: str, use_color: bool) -> str:
    if severity == "error":
        return _color("ERROR  ", _RED, use_color)
    return _color("WARNING", _YELLOW, use_color)


def format_lint_issue(issue: LintIssue, use_color: bool = False) -> str:
    label = _severity_label(issue.severity, use_color)
    key_part = f" [{issue.key}]" if issue.key else ""
    return f"  line {issue.line_number:>3} | {label} |{key_part} {issue.message}"


def format_lint_report(report: LintReport, use_color: bool = False) -> str:
    lines = []
    header = _color("Lint Results", _BOLD, use_color)
    lines.append(header)

    if not report.has_issues:
        lines.append(_color("  No issues found.", _GREEN, use_color))
    else:
        for issue in report.issues:
            lines.append(format_lint_issue(issue, use_color))

    summary = (
        f"  {report.error_count} error(s), {report.warning_count} warning(s)"
    )
    lines.append(summary)
    return "\n".join(lines)


def print_lint_report(report: LintReport, use_color: bool = True) -> None:
    print(format_lint_report(report, use_color=use_color))
