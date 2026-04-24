"""Formats and prints AnnotationReport instances."""
from envguard.annotator import AnnotationReport

_RESET = "\033[0m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_GREY = "\033[90m"


def _color(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color else text


def format_annotation_report(
    report: AnnotationReport, use_color: bool = True
) -> str:
    lines = []
    header = _color("Annotation Report", _CYAN, use_color)
    lines.append(f"=== {header} ===")

    if not report.entries:
        lines.append(_color("  No variables to annotate.", _GREY, use_color))
        return "\n".join(lines)

    annotated = report.annotated_count()
    unchanged = report.unchanged_count()
    lines.append(
        f"  Annotated : {_color(str(annotated), _GREEN, use_color)}"
    )
    lines.append(f"  Unchanged : {unchanged}")
    lines.append("")

    for entry in report.entries:
        if not entry.key:
            continue
        if entry.was_changed:
            label = _color("annotated", _GREEN, use_color)
            lines.append(f"  {entry.key:<30} [{label}]  # {entry.annotation}")
        else:
            label = _color("unchanged", _GREY, use_color)
            lines.append(f"  {entry.key:<30} [{label}]")

    return "\n".join(lines)


def print_annotation_report(
    report: AnnotationReport, use_color: bool = True
) -> None:
    print(format_annotation_report(report, use_color=use_color))
