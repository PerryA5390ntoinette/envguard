"""Reporter for ImportReport — formats import results for terminal output."""
from __future__ import annotations

from envguard.importer import ImportReport


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_import_report(report: ImportReport, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Import Report", "1;36", use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries and not report.skipped:
        lines.append(_color("No variables imported.", "2", use_color))
        return "\n".join(lines)

    if report.entries:
        imported_label = _color(
            f"Imported ({report.imported_count()})", "1;32", use_color
        )
        lines.append(imported_label)
        for entry in report.entries:
            source_tag = _color(f"[{entry.source}]", "0;34", use_color)
            lines.append(f"  {source_tag} {entry.key}")

    if report.skipped:
        skipped_label = _color(
            f"Skipped ({report.skipped_count()})", "1;33", use_color
        )
        lines.append(skipped_label)
        for key in report.skipped:
            lines.append(f"  - {key}")

    summary = _color(
        f"Total: {report.imported_count()} imported, "
        f"{report.skipped_count()} skipped.",
        "2",
        use_color,
    )
    lines.append(summary)
    return "\n".join(lines)


def print_import_report(report: ImportReport, use_color: bool = True) -> None:
    print(format_import_report(report, use_color=use_color))
