"""Format and print CloneReport output."""
from envguard.cloner import CloneReport


def _color(text: str, code: str, use_color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if use_color else text


def format_clone_report(report: CloneReport, use_color: bool = True) -> str:
    lines = []
    header = _color("Clone Report", "1;36", use_color)
    lines.append(header)
    lines.append("-" * 40)

    if report.total == 0:
        lines.append(_color("No variables cloned.", "33", use_color))
        return "\n".join(lines)

    for entry in report.entries:
        if entry.was_remapped:
            key_label = _color(
                f"{entry.original_key} -> {entry.key}", "35", use_color
            )
        else:
            key_label = _color(entry.key, "32", use_color)

        value_display = entry.value if entry.value else _color("(empty)", "90", use_color)

        badges = []
        if entry.was_remapped:
            badges.append(_color("[remapped]", "35", use_color))
        if entry.was_overridden:
            badges.append(_color("[overridden]", "33", use_color))

        badge_str = " ".join(badges)
        line = f"  {key_label} = {value_display}"
        if badge_str:
            line += f"  {badge_str}"
        lines.append(line)

    lines.append("-" * 40)
    lines.append(
        f"Total: {report.total}  "
        f"Remapped: {report.remapped_count}  "
        f"Overridden: {report.overridden_count}"
    )
    return "\n".join(lines)


def print_clone_report(report: CloneReport, use_color: bool = True) -> None:
    print(format_clone_report(report, use_color=use_color))
