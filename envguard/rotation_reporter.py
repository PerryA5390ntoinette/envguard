"""rotation_reporter.py – format and print RotationReport output."""
from __future__ import annotations

from envguard.rotator import RotationReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_rotation_report(report: RotationReport, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Rotation Candidates", "1;36", use_color)
    lines.append(f"\n{header}")
    lines.append("-" * 40)

    if not report.has_candidates:
        lines.append(_color("  No rotation candidates detected.", "32", use_color))
        return "\n".join(lines)

    for entry in report.entries:
        key_label = _color(entry.key, "1;33", use_color)
        reason_label = _color(entry.reason, "33", use_color)
        action_label = _color(entry.suggested_action, "36", use_color)
        lines.append(f"  {key_label}")
        lines.append(f"    Reason : {reason_label}")
        lines.append(f"    Action : {action_label}")

    summary = _color(
        f"\n{report.flagged_count} variable(s) flagged for rotation.",
        "1;31" if report.flagged_count else "32",
        use_color,
    )
    lines.append(summary)
    return "\n".join(lines)


def print_rotation_report(report: RotationReport, use_color: bool = True) -> None:
    print(format_rotation_report(report, use_color=use_color))
