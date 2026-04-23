"""alias_reporter.py – human-readable output for AliasReport."""
from __future__ import annotations

from envguard.aliaser import AliasReport


def _color(text: str, code: str, *, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_alias_report(report: AliasReport, *, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Alias Remapping Report", "1;34", use_color=use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries:
        lines.append("  No aliases processed.")
        return "\n".join(lines)

    for entry in report.entries:
        if entry.resolved:
            arrow = _color("→", "32", use_color=use_color)
            label = _color("remapped", "32", use_color=use_color)
        else:
            arrow = _color("→", "33", use_color=use_color)
            label = _color("skipped (canonical exists)", "33", use_color=use_color)
        lines.append(
            f"  {entry.alias} {arrow} {entry.canonical}  [{label}]  value={entry.value!r}"
        )

    lines.append("-" * 40)
    resolved = _color(str(report.resolved_count()), "32", use_color=use_color)
    skipped = _color(str(report.unresolved_count()), "33", use_color=use_color)
    lines.append(f"  Remapped: {resolved}  Skipped: {skipped}")
    return "\n".join(lines)


def print_alias_report(report: AliasReport, *, use_color: bool = True) -> None:
    print(format_alias_report(report, use_color=use_color))
