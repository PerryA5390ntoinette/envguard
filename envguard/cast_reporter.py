"""cast_reporter.py — format and print CastReport results."""
from __future__ import annotations
from typing import List
from envguard.caster import CastReport, CastEntry

_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"
_BOLD = "\033[1m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def _format_entry(entry: CastEntry, use_color: bool) -> str:
    if entry.success:
        status = _color("OK", _GREEN, use_color)
        detail = f"{entry.raw!r} → ({entry.cast_type}) {entry.cast_value!r}"
    else:
        status = _color("FAIL", _RED, use_color)
        detail = f"{entry.raw!r} — {entry.error}"
    key_str = _color(entry.key, _BOLD, use_color)
    return f"  [{status}] {key_str}: {detail}"


def format_cast_report(report: CastReport, use_color: bool = True) -> str:
    lines: List[str] = []
    header = _color("Cast Report", _BOLD, use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries:
        lines.append("  No variables to cast.")
    else:
        for entry in report.entries:
            lines.append(_format_entry(entry, use_color))

    lines.append("-" * 40)
    ok = _color(str(report.success_count()), _GREEN, use_color)
    fail = _color(str(report.failure_count()), _RED, use_color)
    lines.append(f"  Passed: {ok}  Failed: {fail}")
    return "\n".join(lines)


def print_cast_report(report: CastReport, use_color: bool = True) -> None:
    print(format_cast_report(report, use_color=use_color))
