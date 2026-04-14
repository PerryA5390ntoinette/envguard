"""Format and print deprecation reports."""
from __future__ import annotations

from typing import Optional

from envguard.deprecator import DeprecationReport


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_deprecation_report(
    report: DeprecationReport,
    use_color: bool = True,
) -> str:
    if not report.has_deprecations:
        msg = "No deprecated variables found."
        return _color(msg, "32", use_color)

    lines = []
    header = _color("Deprecated Variables", "1;33", use_color)
    lines.append(header)
    lines.append(_color("-" * 40, "33", use_color))

    for entry in report.entries:
        key_str = _color(entry.key, "1;31", use_color)
        lines.append(f"  {key_str}")
        reason_str = _color(f"    Reason     : {entry.reason}", "33", use_color)
        lines.append(reason_str)
        if entry.has_replacement:
            rep_str = _color(
                f"    Replacement: {entry.replacement}", "36", use_color
            )
            lines.append(rep_str)
        else:
            lines.append(
                _color("    Replacement: (none)", "90", use_color)
            )

    summary = _color(
        f"\nTotal deprecated: {report.total} "
        f"({len(report.with_replacement)} with replacement, "
        f"{len(report.without_replacement)} without)",
        "33",
        use_color,
    )
    lines.append(summary)
    return "\n".join(lines)


def print_deprecation_report(
    report: DeprecationReport,
    use_color: bool = True,
) -> None:
    print(format_deprecation_report(report, use_color=use_color))
