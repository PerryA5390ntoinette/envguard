"""Reporter for TemplateReport: formats and prints template generation results."""
from __future__ import annotations

from envguard.templater import TemplateReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_template_report(report: TemplateReport, use_color: bool = True) -> str:
    lines = []
    header = _color("envguard • Template Report", "1;36", use_color)
    lines.append(header)
    lines.append("-" * 40)

    if report.total == 0:
        lines.append(_color("No variables found in schema.", "33", use_color))
        return "\n".join(lines)

    for entry in report.entries:
        req_label = (
            _color("required", "1;31", use_color)
            if entry.required
            else _color("optional", "2;32", use_color)
        )
        key_str = _color(entry.key, "1", use_color)
        placeholder_str = _color(entry.placeholder, "33", use_color)
        line = f"  {key_str}={placeholder_str}  [{req_label}]"
        if entry.description:
            line += f"  # {entry.description}"
        lines.append(line)

    lines.append("-" * 40)
    summary = (
        f"Total: {report.total}  "
        f"Required: {report.required_count}  "
        f"Optional: {report.optional_count}"
    )
    lines.append(_color(summary, "2", use_color))
    return "\n".join(lines)


def print_template_report(report: TemplateReport, use_color: bool = True) -> None:
    print(format_template_report(report, use_color=use_color))
