"""Format and print redaction reports for CLI output."""
from envguard.redactor import RedactionReport

_RESET = "\033[0m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_redaction_report(report: RedactionReport, use_color: bool = True) -> str:
    """Return a human-readable string summarising the redaction report."""
    lines = []
    header = _color("Redaction Summary", _CYAN, use_color)
    lines.append(header)
    lines.append("-" * 40)

    for key, value in report.redacted.items():
        if key in report.redacted_keys:
            label = _color("REDACTED", _YELLOW, use_color)
            lines.append(f"  {key} = {label}")
        else:
            lines.append(f"  {key} = {value}")

    lines.append("-" * 40)
    count_str = _color(str(report.redaction_count), _YELLOW, use_color)
    total_str = _color(str(len(report.redacted)), _GREEN, use_color)
    lines.append(f"  {count_str} of {total_str} variable(s) redacted.")
    return "\n".join(lines)


def print_redaction_report(report: RedactionReport, use_color: bool = True) -> None:
    """Print the formatted redaction report to stdout."""
    print(format_redaction_report(report, use_color=use_color))
