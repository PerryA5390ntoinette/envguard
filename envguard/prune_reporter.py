"""Format and print PruneReport results."""
from __future__ import annotations

from envguard.pruner import PruneReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_prune_report(report: PruneReport, *, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Prune Report", "1;36", use_color)
    lines.append(f"{header}")
    lines.append("-" * 40)

    if not report.entries:
        lines.append(_color("No variables processed.", "2", use_color))
        return "\n".join(lines)

    for entry in report.entries:
        if entry.pruned:
            label = _color("PRUNED", "1;31", use_color)
            reason = _color(f"[{entry.reason}]", "33", use_color)
            lines.append(f"  {label}  {entry.key}  {reason}")
        else:
            label = _color("kept  ", "2", use_color)
            lines.append(f"  {label}  {entry.key}")

    lines.append("-" * 40)
    pruned_str = _color(str(report.pruned_count()), "1;31", use_color)
    kept_str = _color(str(report.kept_count()), "1;32", use_color)
    lines.append(f"Pruned: {pruned_str}  Kept: {kept_str}")
    return "\n".join(lines)


def print_prune_report(report: PruneReport, *, use_color: bool = True) -> None:
    print(format_prune_report(report, use_color=use_color))
