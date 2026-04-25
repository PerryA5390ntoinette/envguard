"""map_reporter.py — human-readable output for MapReport."""
from __future__ import annotations

from envguard.mapper import MapReport


def _color(text: str, code: str, *, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_map_report(report: MapReport, *, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Key Mapping Report", "1;34", use_color=use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries:
        lines.append(_color("  No variables processed.", "2", use_color=use_color))
        return "\n".join(lines)

    for entry in report.entries:
        if entry.remapped:
            arrow = _color("→", "1;32", use_color=use_color)
            label = _color("REMAPPED", "32", use_color=use_color)
            lines.append(
                f"  {label}  {entry.original_key} {arrow} {entry.new_key}"
            )
        else:
            label = _color("KEPT    ", "2", use_color=use_color)
            lines.append(f"  {label}  {entry.original_key}")

    lines.append("-" * 40)
    total = len(report.entries)
    remapped = report.remapped_count()
    skipped = report.skipped_count()
    lines.append(
        f"  Total: {total}  "
        + _color(f"Remapped: {remapped}", "32", use_color=use_color)
        + f"  Kept: {skipped}"
    )
    return "\n".join(lines)


def print_map_report(report: MapReport, *, use_color: bool = True) -> None:
    print(format_map_report(report, use_color=use_color))
