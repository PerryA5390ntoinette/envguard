"""Reporter for InheritReport — formats inheritance results for CLI output."""
from __future__ import annotations
from envguard.inheritor import InheritReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_inherit_report(report: InheritReport, use_color: bool = True) -> str:
    lines: list[str] = []

    header = _color("Inheritance Report", "1;34", use_color)
    lines.append(f"\n{header}")
    lines.append("-" * 40)

    if not report.entries:
        lines.append(_color("  No variables found.", "33", use_color))
        return "\n".join(lines)

    for entry in sorted(report.entries, key=lambda e: e.key):
        if entry.overridden:
            label = _color("OVERRIDDEN", "1;33", use_color)
        elif entry.source == "override":
            label = _color("ADDED", "1;32", use_color)
        else:
            label = _color("INHERITED", "36", use_color)
        lines.append(f"  {label:<20}  {entry.key} = {entry.value}")

    lines.append("-" * 40)
    lines.append(
        f"  Inherited: {report.inherited_count}  "
        f"Overridden: {report.overridden_count}  "
        f"Added: {report.added_count}"
    )
    return "\n".join(lines)


def print_inherit_report(report: InheritReport, use_color: bool = True) -> None:
    print(format_inherit_report(report, use_color=use_color))
