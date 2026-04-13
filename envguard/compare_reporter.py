"""Format and print ComparisonReport results to the terminal."""

from envguard.comparator import ComparisonReport, ComparisonEntry


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def _status_label(entry: ComparisonEntry, use_color: bool) -> str:
    if entry.status == "match":
        return _color("MATCH", "32", use_color)
    if entry.status == "mismatch":
        return _color("MISMATCH", "33", use_color)
    if entry.status == "left_only":
        return _color("LEFT ONLY", "34", use_color)
    return _color("RIGHT ONLY", "35", use_color)


def format_comparison_report(report: ComparisonReport, use_color: bool = True) -> str:
    lines = []
    header = f"Comparing: {report.left_label}  vs  {report.right_label}"
    lines.append(header)
    lines.append("-" * len(header))

    for entry in report.entries:
        label = _status_label(entry, use_color)
        if entry.status == "match":
            lines.append(f"  [{label}] {entry.key}")
        elif entry.status == "mismatch":
            lines.append(f"  [{label}] {entry.key}")
            lines.append(f"      {report.left_label}: {entry.left_value!r}")
            lines.append(f"      {report.right_label}: {entry.right_value!r}")
        elif entry.status == "left_only":
            lines.append(f"  [{label}] {entry.key} = {entry.left_value!r}")
        else:
            lines.append(f"  [{label}] {entry.key} = {entry.right_value!r}")

    lines.append("")
    summary_parts = [
        f"{len(report.matches)} match(es)",
        f"{len(report.mismatches)} mismatch(es)",
        f"{len(report.left_only)} left-only",
        f"{len(report.right_only)} right-only",
    ]
    lines.append("Summary: " + ", ".join(summary_parts))
    if report.is_identical:
        lines.append(_color("Files are identical.", "32", use_color))
    return "\n".join(lines)


def print_comparison_report(report: ComparisonReport, use_color: bool = True) -> None:
    print(format_comparison_report(report, use_color=use_color))
