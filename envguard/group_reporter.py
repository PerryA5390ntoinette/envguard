"""Formats and prints GroupReport output."""

from typing import Optional
from envguard.grouper import GroupReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_group_report(report: GroupReport, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("=== Variable Groups ===", "1;34", use_color)
    lines.append(header)

    if not report.groups and not report.ungrouped:
        lines.append("  No variables found.")
        return "\n".join(lines)

    for group in report.all_groups():
        entries = report.entries_for(group)
        group_label = _color(f"[{group}]", "1;36", use_color)
        lines.append(f"  {group_label}  ({len(entries)} variable(s))")
        for entry in entries:
            key_str = _color(entry.key, "33", use_color)
            lines.append(f"    {key_str}")

    if report.ungrouped:
        ug_label = _color("[ungrouped]", "1;90", use_color)
        lines.append(f"  {ug_label}  ({len(report.ungrouped)} variable(s))")
        for entry in report.ungrouped:
            key_str = _color(entry.key, "90", use_color)
            lines.append(f"    {key_str}")

    total_str = _color(f"Total: {report.total()} variable(s) in {len(report.groups)} group(s)", "1", use_color)
    lines.append(total_str)
    return "\n".join(lines)


def print_group_report(report: GroupReport, use_color: bool = True) -> None:
    print(format_group_report(report, use_color=use_color))
