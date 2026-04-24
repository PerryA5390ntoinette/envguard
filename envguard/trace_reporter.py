"""Formats and prints TraceReport output."""
from __future__ import annotations
from envguard.tracer import TraceReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_trace_report(report: TraceReport, use_color: bool = True) -> str:
    lines = []
    header = _color("=== Variable Trace Report ===", "1;36", use_color)
    lines.append(header)

    if report.total == 0:
        lines.append(_color("  No variables traced.", "2", use_color))
        return "\n".join(lines)

    lines.append(
        f"  Traced {report.total} entr{'y' if report.total == 1 else 'ies'}, "
        f"{report.overridden_count} override(s) detected."
    )
    lines.append("")

    for key in report.all_keys:
        key_entries = report.for_key(key)
        final = key_entries[-1]
        key_label = _color(key, "1", use_color)
        src_label = _color(final.source, "0;33", use_color)
        val_display = _color(repr(final.value), "0;32", use_color)
        lines.append(f"  {key_label}  ({src_label})  =  {val_display}")

        for entry in key_entries[:-1]:
            if entry.was_overridden:
                old_val = _color(repr(entry.value), "0;31", use_color)
                old_src = _color(entry.source, "2", use_color)
                overrider = _color(entry.overridden_by or "", "0;33", use_color)
                lines.append(
                    f"    {_color('overrode', '2', use_color)} {old_val} "
                    f"from {old_src} -> {overrider}"
                )

    return "\n".join(lines)


def print_trace_report(report: TraceReport, use_color: bool = True) -> None:
    print(format_trace_report(report, use_color=use_color))
