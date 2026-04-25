"""Reporter for SplitReport — formats bucket split results for terminal output."""
from __future__ import annotations

from typing import Optional

from envguard.splitter import SplitReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_split_report(report: SplitReport, use_color: bool = True) -> str:
    lines: list[str] = []

    header = _color("EnvGuard — Env Split Report", "1;36", use_color)
    lines.append(header)
    lines.append("-" * 40)

    if report.total == 0:
        lines.append(_color("No variables to split.", "33", use_color))
        return "\n".join(lines)

    summary = (
        f"Total variables : {report.total}  |  "
        f"Buckets : {report.bucket_count}"
    )
    lines.append(summary)
    lines.append("")

    for bucket in sorted(report.bucket_names):
        bucket_label = _color(f"[{bucket}]", "1;34", use_color)
        lines.append(bucket_label)
        env = report.env_for(bucket)
        for key in sorted(env):
            key_str = _color(key, "32", use_color)
            lines.append(f"  {key_str} = {env[key]}")
        lines.append("")

    return "\n".join(lines).rstrip()


def print_split_report(
    report: SplitReport,
    use_color: bool = True,
    file: Optional[object] = None,
) -> None:
    import sys

    out = file or sys.stdout
    print(format_split_report(report, use_color=use_color), file=out)  # type: ignore[arg-type]
