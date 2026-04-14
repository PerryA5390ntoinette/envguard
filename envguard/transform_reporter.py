"""Format and print TransformReport instances."""

from typing import Optional
from envguard.transformer import TransformReport, TransformEntry


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def _format_entry(entry: TransformEntry, use_color: bool) -> str:
    if entry.skipped:
        label = _color("SKIP", "33", use_color)
        reason = entry.skip_reason or "unknown reason"
        return f"  [{label}] {entry.key} — {reason}"
    arrow = _color("->", "36", use_color)
    key_str = _color(entry.key, "1", use_color)
    rule_str = _color(f"({entry.rule})", "35", use_color)
    return (
        f"  {key_str}: \"{entry.original}\" {arrow} \"{entry.transformed}\" {rule_str}"
    )


def format_transform_report(
    report: TransformReport,
    use_color: bool = False,
) -> str:
    lines = []
    header = "Transform Report"
    lines.append(header)
    lines.append("-" * len(header))

    if not report.entries:
        lines.append("  No transformations applied.")
    else:
        for entry in report.entries:
            lines.append(_format_entry(entry, use_color))

    lines.append("")
    transformed = _color(str(report.transformed_count()), "32", use_color)
    skipped = _color(str(report.skipped_count()), "33", use_color)
    lines.append(f"  Transformed: {transformed}  Skipped: {skipped}")
    return "\n".join(lines)


def print_transform_report(
    report: TransformReport,
    use_color: bool = True,
) -> None:
    print(format_transform_report(report, use_color=use_color))
