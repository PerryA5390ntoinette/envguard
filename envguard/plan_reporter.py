"""plan_reporter.py — Formats and prints PlanReport output."""
from __future__ import annotations
from envguard.planner import PlanReport, PlanAction


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def _action_label(action: str, use_color: bool) -> str:
    labels = {
        "add":    ("[ADD]   ", "32"),
        "remove": ("[REMOVE]", "31"),
        "update": ("[UPDATE]", "33"),
        "keep":   ("[KEEP]  ", "90"),
    }
    text, code = labels.get(action, (f"[{action.upper()}]", "0"))
    return _color(text, code, use_color)


def format_plan_action(entry: PlanAction, use_color: bool = True) -> str:
    label = _action_label(entry.action, use_color)
    parts = [f"{label} {entry.key}"]
    if entry.action == "add":
        parts.append(f"  -> {entry.new_value!r}")
    elif entry.action == "remove":
        parts.append(f"  <- {entry.old_value!r}")
    elif entry.action == "update":
        parts.append(f"  {entry.old_value!r} -> {entry.new_value!r}")
    if entry.reason:
        parts.append(f"  # {entry.reason}")
    return "".join(parts)


def format_plan_report(report: PlanReport, use_color: bool = True) -> str:
    lines: list[str] = []
    header = _color("Migration Plan", "1", use_color)
    lines.append(f"=== {header} ===")

    if not report.actions:
        lines.append("  (no variables)")  
        return "\n".join(lines)

    for entry in report.actions:
        lines.append("  " + format_plan_action(entry, use_color))

    summary = (
        f"  Summary: {report.add_count} add, "
        f"{report.update_count} update, "
        f"{report.remove_count} remove, "
        f"{report.keep_count} keep"
    )
    lines.append("")
    lines.append(summary)
    return "\n".join(lines)


def print_plan_report(report: PlanReport, use_color: bool = True) -> None:
    print(format_plan_report(report, use_color))
