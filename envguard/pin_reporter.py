"""Formatting and printing helpers for pin / drift reports."""
from __future__ import annotations

from typing import List

from envguard.pinner import PinReport, PinDrift


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_pin_report(report: PinReport, use_color: bool = False) -> str:
    lines: List[str] = []
    header = _color("Pinned Variables", "1;34", use_color)
    lines.append(f"{header} ({report.pinned_count()} total)")
    if not report.entries:
        lines.append("  No variables pinned.")
        return "\n".join(lines)
    for entry in report.entries:
        key_str = _color(entry.key, "36", use_color)
        cs_str = _color(entry.checksum, "2", use_color)
        lines.append(f"  {key_str} = {entry.value!r}  [{cs_str}]")
    return "\n".join(lines)


def format_drift_report(drifts: List[PinDrift], use_color: bool = False) -> str:
    lines: List[str] = []
    header = _color("Drift Detection", "1;33", use_color)
    lines.append(f"{header} ({len(drifts)} drift(s) found)")
    if not drifts:
        lines.append("  " + _color("No drift detected. Environment matches pinfile.", "32", use_color))
        return "\n".join(lines)
    for drift in drifts:
        key_str = _color(drift.key, "33", use_color)
        lines.append(f"  {key_str}")
        lines.append(f"    pinned : {drift.pinned_value!r}  [{drift.pinned_checksum}]")
        lines.append(f"    current: {drift.current_value!r}  [{drift.current_checksum}]")
    return "\n".join(lines)


def print_pin_report(report: PinReport, use_color: bool = False) -> None:
    print(format_pin_report(report, use_color))


def print_drift_report(drifts: List[PinDrift], use_color: bool = False) -> None:
    print(format_drift_report(drifts, use_color))
