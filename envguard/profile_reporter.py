"""Format and print ProfileReport summaries for CLI output."""

from typing import Optional
from envguard.profiler import ProfileReport


def _bar(count: int, total: int, width: int = 20) -> str:
    """Render a simple ASCII progress bar."""
    if total == 0:
        filled = 0
    else:
        filled = int(round(count / total * width))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def format_profile_report(report: ProfileReport, use_color: bool = True) -> str:
    """Return a formatted string summary of a ProfileReport."""
    lines = []

    def _color(text: str, code: str) -> str:
        if use_color:
            return f"\033[{code}m{text}\033[0m"
        return text

    lines.append(_color("=== Env Profile Summary ===", "1;36"))
    lines.append(f"  Total variables : {report.total}")
    lines.append(
        f"  Empty values    : {report.empty_count} "
        + _bar(report.empty_count, report.total)
    )
    lines.append(
        f"  Secret-like     : {report.secret_like_count} "
        + _bar(report.secret_like_count, report.total)
    )
    lines.append(
        f"  URL-like        : {report.url_like_count} "
        + _bar(report.url_like_count, report.total)
    )

    if report.category_counts:
        lines.append("")
        lines.append(_color("  Categories:", "1"))
        for category, count in sorted(report.category_counts.items()):
            lines.append(f"    {category:<12}: {count}")

    return "\n".join(lines)


def print_profile_report(report: ProfileReport, use_color: bool = True) -> None:
    """Print a ProfileReport to stdout."""
    print(format_profile_report(report, use_color=use_color))
