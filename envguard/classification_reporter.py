"""Format and print ClassificationReport output."""
from __future__ import annotations

import sys
from typing import IO

from envguard.classifier import ClassificationReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_classification_report(report: ClassificationReport, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("=== Variable Classification ===", "1", use_color)
    lines.append(header)

    if report.total == 0:
        lines.append("  No variables to classify.")
        return "\n".join(lines)

    by_type = report.by_type()
    sensitive_keys = set(report.sensitive_keys())

    for entry in report.entries:
        type_label = _color(f"[{entry.inferred_type}]", "36", use_color)
        if entry.sensitive:
            sens_label = _color("[sensitive]", "31", use_color)
            lines.append(f"  {entry.key:<30} {type_label} {sens_label}")
        else:
            lines.append(f"  {entry.key:<30} {type_label}")

    lines.append("")
    summary_parts = [
        f"Total: {report.total}",
        f"Sensitive: {_color(str(report.sensitive_count), '31', use_color)}",
    ]
    for type_name, keys in sorted(by_type.items()):
        summary_parts.append(f"{type_name}: {len(keys)}")
    lines.append("  " + "  |  ".join(summary_parts))

    return "\n".join(lines)


def print_classification_report(
    report: ClassificationReport,
    use_color: bool = True,
    file: IO[str] = sys.stdout,
) -> None:
    print(format_classification_report(report, use_color=use_color), file=file)
