"""Reporter for SummaryReport — formats and prints a human-readable summary."""

from __future__ import annotations

from envguard.summarizer import SummaryReport


def _color(text: str, code: str, *, use_color: bool) -> str:
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_summary_report(report: SummaryReport, *, use_color: bool = True) -> str:
    """Return a formatted string representation of a SummaryReport."""
    lines: list[str] = []

    header = _color("EnvGuard Summary", "1;36", use_color=use_color)
    lines.append(header)
    lines.append("-" * 40)

    source_label = _color("Source:", "1", use_color=use_color)
    lines.append(f"{source_label} {report.source}")

    vars_label = _color("Variables loaded:", "1", use_color=use_color)
    lines.append(f"{vars_label} {report.variables_loaded}")

    errors = report.audit_errors
    warnings = report.audit_warnings
    passed = report.audit_passed

    err_text = _color(str(errors), "1;31" if errors else "0", use_color=use_color)
    warn_text = _color(str(warnings), "1;33" if warnings else "0", use_color=use_color)
    pass_text = _color(str(passed), "1;32", use_color=use_color)

    lines.append(f"Audit errors:    {err_text}")
    lines.append(f"Audit warnings:  {warn_text}")
    lines.append(f"Audit passed:    {pass_text}")

    lint_issues = report.lint_issues
    lint_text = _color(str(lint_issues), "1;31" if lint_issues else "0", use_color=use_color)
    lines.append(f"Lint issues:     {lint_text}")

    if report.interpolation_warnings:
        iw_text = _color(
            str(report.interpolation_warnings), "1;33", use_color=use_color
        )
        lines.append(f"Interp warnings: {iw_text}")

    overall = "PASS" if (errors == 0 and lint_issues == 0) else "FAIL"
    color_code = "1;32" if overall == "PASS" else "1;31"
    overall_text = _color(overall, color_code, use_color=use_color)
    lines.append("-" * 40)
    lines.append(f"Overall: {overall_text}")

    return "\n".join(lines)


def print_summary_report(report: SummaryReport, *, use_color: bool = True) -> None:
    """Print a formatted SummaryReport to stdout."""
    print(format_summary_report(report, use_color=use_color))
