"""Format and print RenameReport output."""
from __future__ import annotations

from envguard.renamer import RenameReport


def _color(text: str, code: str, *, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_rename_report(report: RenameReport, *, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Rename Report", "1;34", use_color=use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries:
        lines.append("  No renames requested.")
        return "\n".join(lines)

    for entry in report.entries:
        if entry.skipped:
            label = _color("SKIP", "33", use_color=use_color)
            reason = f" ({entry.skip_reason})"
            lines.append(f"  {label}  {entry.old_name} -> {entry.new_name}{reason}")
        else:
            label = _color("OK", "32", use_color=use_color)
            lines.append(f"  {label}    {entry.old_name} -> {entry.new_name}")

    lines.append("-" * 40)
    renamed = _color(str(report.renamed_count()), "32", use_color=use_color)
    skipped = _color(str(report.skipped_count()), "33", use_color=use_color)
    lines.append(f"  Renamed: {renamed}  Skipped: {skipped}")
    return "\n".join(lines)


def print_rename_report(report: RenameReport, *, use_color: bool = True) -> None:
    print(format_rename_report(report, use_color=use_color))
