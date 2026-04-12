"""Formats and outputs ValidationReport results to the terminal."""

from dataclasses import dataclass
from typing import TextIO
import sys

from envguard.validator import ValidationReport, ValidationResult


ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN = "\033[92m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_result(result: ValidationResult, use_color: bool = True) -> str:
    """Format a single ValidationResult as a human-readable string."""
    level = result.level.upper()
    if result.level == "error":
        level_str = _colorize(f"[{level}]", ANSI_RED, use_color)
    elif result.level == "warning":
        level_str = _colorize(f"[{level}]", ANSI_YELLOW, use_color)
    else:
        level_str = _colorize(f"[{level}]", ANSI_GREEN, use_color)

    var_str = _colorize(result.variable, ANSI_BOLD, use_color)
    return f"  {level_str} {var_str}: {result.message}"


def print_report(
    report: ValidationReport,
    out: TextIO = sys.stdout,
    use_color: bool = True,
) -> None:
    """Print a full ValidationReport to the given output stream."""
    header = _colorize("envguard audit report", ANSI_BOLD, use_color)
    print(f"\n{header}", file=out)
    print("-" * 40, file=out)

    all_results = report.errors + report.warnings
    if not all_results:
        print(_colorize("  ✔ All variables passed validation.", ANSI_GREEN, use_color), file=out)
    else:
        for result in report.errors:
            print(format_result(result, use_color), file=out)
        for result in report.warnings:
            print(format_result(result, use_color), file=out)

    print("-" * 40, file=out)
    summary = (
        f"  {len(report.errors)} error(s), "
        f"{len(report.warnings)} warning(s), "
        f"{len(report.passed)} passed"
    )
    print(summary, file=out)

    status = "FAIL" if report.errors else "PASS"
    color = ANSI_RED if report.errors else ANSI_GREEN
    print(_colorize(f"  Status: {status}", color, use_color), file=out)
    print(file=out)
