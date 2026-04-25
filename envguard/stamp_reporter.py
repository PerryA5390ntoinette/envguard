"""Reporter for StampReport."""
from __future__ import annotations

from envguard.stamper import StampReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_stamp_report(report: StampReport, *, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Stamp Report", "1;36", use_color)
    lines.append(f"=== {header} ===")

    if not report.entries:
        lines.append(_color("  No stamp keys configured.", "2", use_color))
        return "\n".join(lines)

    for entry in report.entries:
        if entry.injected:
            label = _color("INJECTED", "1;32", use_color)
        else:
            label = _color("SKIPPED ", "1;33", use_color)
        lines.append(f"  [{label}] {entry.key} = {entry.value}")

    summary = (
        f"\n  Injected: {report.injected_count}  "
        f"Skipped: {report.skipped_count}"
    )
    lines.append(_color(summary, "2", use_color))
    return "\n".join(lines)


def print_stamp_report(report: StampReport, *, use_color: bool = True) -> None:
    print(format_stamp_report(report, use_color=use_color))
