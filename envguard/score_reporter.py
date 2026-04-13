"""Formats and prints ScoreReport output for the CLI."""
from envguard.scorer import ScoreReport

_GRADE_COLORS = {
    "A": "\033[92m",
    "B": "\033[94m",
    "C": "\033[93m",
    "D": "\033[33m",
    "F": "\033[91m",
}
_RESET = "\033[0m"


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{code}{text}{_RESET}"


def format_score_report(report: ScoreReport, use_color: bool = True) -> str:
    lines = []
    grade_color = _GRADE_COLORS.get(report.grade, "")
    grade_str = _color(report.grade, grade_color, use_color)
    score_str = _color(str(report.score), grade_color, use_color)

    lines.append(f"EnvGuard Score: {score_str}/100  Grade: {grade_str}")
    lines.append("")

    bd = report.breakdown
    lines.append("Breakdown:")
    lines.append(f"  Audit errors   : {bd.audit_errors}")
    lines.append(f"  Audit warnings : {bd.audit_warnings}")
    lines.append(f"  Lint errors    : {bd.lint_errors}")
    lines.append(f"  Lint warnings  : {bd.lint_warnings}")
    lines.append(f"  Exposed secrets: {bd.exposed_secrets}")

    if bd.deductions:
        lines.append("")
        lines.append("Deductions:")
        for d in bd.deductions:
            lines.append(f"  {d}")

    return "\n".join(lines)


def print_score_report(report: ScoreReport, use_color: bool = True) -> None:
    print(format_score_report(report, use_color=use_color))
