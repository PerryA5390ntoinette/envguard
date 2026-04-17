"""Formats and prints StaleReport output."""
from __future__ import annotations
from envguard.staler import StaleReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_stale_report(report: StaleReport, use_color: bool = True) -> str:
    lines = []
    header = _color("Stale Variable Report", "1;36", use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.has_stale:
        lines.append(_color("No stale variables detected.", "32", use_color))
        return "\n".join(lines)

    for entry in report.entries:
        key_label = _color(entry.key, "33", use_color)
        reason_label = _color(entry.reason, "90", use_color)
        lines.append(f"  {key_label}  —  {reason_label}")

    lines.append("")
    summary = _color(f"Total stale: {report.stale_count}", "1", use_color)
    lines.append(summary)
    return "\n".join(lines)


def print_stale_report(report: StaleReport, use_color: bool = True) -> None:
    print(format_stale_report(report, use_color=use_color))
