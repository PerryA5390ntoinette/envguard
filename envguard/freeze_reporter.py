"""Human-readable reporter for :class:`FreezeReport`."""
from __future__ import annotations

import sys
from typing import TextIO

from envguard.freezer import FreezeReport


def _color(text: str, code: str, *, use_color: bool) -> str:
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_freeze_report(report: FreezeReport, *, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Freeze Drift Report", "1;36", use_color=use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries:
        lines.append(_color("No variables in freeze manifest.", "2", use_color=use_color))
        return "\n".join(lines)

    for entry in report.entries:
        if entry.drifted:
            status = _color("DRIFTED", "1;31", use_color=use_color)
            detail = (
                f"  frozen={entry.frozen_hash}  current={entry.current_hash}"
            )
            lines.append(f"  {status}  {entry.key}{detail}")
        else:
            status = _color("OK", "1;32", use_color=use_color)
            lines.append(f"  {status}      {entry.key}")

    lines.append("-" * 40)
    summary = (
        f"Stable: {report.stable_count}  "
        f"Drifted: {_color(str(report.drifted_count), '1;31' if report.has_drift else '2', use_color=use_color)}"
    )
    lines.append(summary)
    return "\n".join(lines)


def print_freeze_report(
    report: FreezeReport,
    *,
    use_color: bool = True,
    file: TextIO = sys.stdout,
) -> None:
    print(format_freeze_report(report, use_color=use_color), file=file)
