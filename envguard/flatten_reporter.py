"""Reporter for FlattenReport."""
from __future__ import annotations

from envguard.flattener import FlattenReport


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_flatten_report(report: FlattenReport, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Flatten Report", "1;36", use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries:
        lines.append(_color("No variables to flatten.", "2", use_color))
        return "\n".join(lines)

    for entry in report.entries:
        if entry.changed:
            arrow = _color("→", "33", use_color)
            key_part = f"{entry.original_key} {arrow} {entry.flattened_key}"
            depth_label = _color(f"(depth={entry.depth})", "2", use_color)
            lines.append(f"  {_color('FLAT', '33', use_color)}  {key_part} {depth_label}")
        else:
            lines.append(f"  {_color('OK  ', '32', use_color)}  {entry.original_key}")

    lines.append("")
    summary = (
        f"Total: {len(report.entries)}  "
        f"Flattened: {_color(str(report.changed_count), '33', use_color)}  "
        f"Unchanged: {_color(str(report.unchanged_count), '32', use_color)}  "
        f"Max depth: {report.max_depth}"
    )
    lines.append(summary)
    return "\n".join(lines)


def print_flatten_report(report: FlattenReport, use_color: bool = True) -> None:
    print(format_flatten_report(report, use_color=use_color))
