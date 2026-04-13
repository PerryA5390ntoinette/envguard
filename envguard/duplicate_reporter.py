"""Format and print DuplicateReport instances."""
from __future__ import annotations
from envguard.duplicator import DuplicateReport


ANSI = {
    "red": "\033[31m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{ANSI[code]}{text}{ANSI['reset']}"


def format_duplicate_report(report: DuplicateReport, use_color: bool = True) -> str:
    lines = []
    header = _color("Duplicate Detection Report", "bold", use_color)
    lines.append(header)
    lines.append("-" * 30)

    if not report.has_key_duplicates and not report.has_value_duplicates:
        lines.append(_color("No duplicates found.", "cyan", use_color))
        return "\n".join(lines)

    if report.has_key_duplicates:
        lines.append(_color("Duplicate Keys:", "red", use_color))
        for entry in report.key_duplicates:
            vals = ", ".join(repr(v) for v in entry.values)
            lines.append(
                f"  {_color(entry.key, 'bold', use_color)} "
                f"appears {entry.occurrences}x → [{vals}]"
            )

    if report.has_value_duplicates:
        lines.append(_color("Shared Values:", "yellow", use_color))
        for value, keys in report.value_duplicates.items():
            key_list = ", ".join(keys)
            lines.append(
                f"  {_color(repr(value), 'bold', use_color)} shared by: {key_list}"
            )

    lines.append("-" * 30)
    lines.append(f"Total issues: {report.total_issues}")
    return "\n".join(lines)


def print_duplicate_report(report: DuplicateReport, use_color: bool = True) -> None:
    print(format_duplicate_report(report, use_color=use_color))
