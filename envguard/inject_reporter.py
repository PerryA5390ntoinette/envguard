"""Formatting and printing helpers for InjectionReport."""
from __future__ import annotations

from envguard.injector import InjectionReport

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"


def _color(text: str, code: str, *, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_inject_report(report: InjectionReport, *, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Injection Report", _BOLD, use_color=use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries:
        lines.append("  No variables were injected.")
        return "\n".join(lines)

    for entry in report.entries:
        source_label = _color(f"[{entry.source}]", _CYAN, use_color=use_color)
        replaced_label = (
            _color(" (replaced)", _YELLOW, use_color=use_color)
            if entry.replaced
            else ""
        )
        key_label = _color(entry.key, _GREEN, use_color=use_color)
        lines.append(f"  {source_label} {key_label} = {entry.value}{replaced_label}")

    lines.append("-" * 40)
    lines.append(
        f"  Injected: {report.injected_count}  "
        f"Replaced: {report.replaced_count}  "
        f"Sources: {', '.join(report.sources_used) or 'none'}"
    )
    return "\n".join(lines)


def print_inject_report(report: InjectionReport, *, use_color: bool = True) -> None:
    print(format_inject_report(report, use_color=use_color))
