"""Render ScopeReport to terminal output."""
from __future__ import annotations
import sys
from envguard.scoper import ScopeReport

_COLORS = {
    "dev": "\033[34m",
    "staging": "\033[33m",
    "prod": "\033[31m",
    "test": "\033[36m",
    "global": "\033[37m",
}
_RESET = "\033[0m"


def _color(text: str, scope: str, use_color: bool) -> str:
    if not use_color:
        return text
    code = _COLORS.get(scope, "\033[37m")
    return f"{code}{text}{_RESET}"


def format_scope_report(report: ScopeReport, use_color: bool = True) -> str:
    if report.total() == 0:
        return "No variables found."
    lines = ["Scope Report", "============"]
    for scope in sorted(report.scopes()):
        entries = report.entries_for(scope)
        label = _color(f"[{scope.upper()}]", scope, use_color)
        lines.append(f"\n{label} ({len(entries)} variable(s))")
        for e in entries:
            lines.append(f"  {e.key}")
    lines.append(f"\nTotal: {report.total()} | Global: {report.global_count()}")
    return "\n".join(lines)


def print_scope_report(report: ScopeReport, use_color: bool = True) -> None:
    print(format_scope_report(report, use_color=use_color))
