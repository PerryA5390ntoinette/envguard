"""Reporter for FilterReport."""
from __future__ import annotations
from envguard.filterer import FilterReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_filter_report(report: FilterReport, *, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("=== Filter Report ===", "1;36", use_color)
    lines.append(header)

    if not report.entries:
        lines.append(_color("  No variables matched the filter criteria.", "33", use_color))
    else:
        lines.append(
            _color(f"  Matched : {report.matched_count()}", "32", use_color)
        )
        lines.append(
            _color(f"  Excluded: {report.excluded_count()}", "90", use_color)
        )
        lines.append("")
        lines.append(_color("  Matched variables:", "1", use_color))
        for entry in report.entries:
            key_str = _color(entry.key, "32", use_color)
            by_str = _color(f"[{entry.matched_by}]", "36", use_color)
            lines.append(f"    {key_str} = {entry.value}  {by_str}")

    if report.excluded:
        lines.append("")
        lines.append(_color("  Excluded keys:", "90", use_color))
        for key in report.excluded:
            lines.append(f"    {_color(key, '90', use_color)}")

    return "\n".join(lines)


def print_filter_report(report: FilterReport, *, use_color: bool = True) -> None:
    print(format_filter_report(report, use_color=use_color))
