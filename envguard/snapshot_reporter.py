"""Reporter for snapshot diffs."""
from __future__ import annotations

from envguard.snapshotter import Snapshot, SnapshotDiff


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_snapshot_diff(diff: SnapshotDiff, use_color: bool = True) -> str:
    lines: list[str] = []

    if not diff.has_changes:
        lines.append(_color("No changes detected between snapshots.", "32", use_color))
        return "\n".join(lines)

    if diff.added:
        lines.append(_color("Added:", "32", use_color))
        for key, val in sorted(diff.added.items()):
            lines.append(f"  + {key}={val}")

    if diff.removed:
        lines.append(_color("Removed:", "31", use_color))
        for key, val in sorted(diff.removed.items()):
            lines.append(f"  - {key}={val}")

    if diff.changed:
        lines.append(_color("Changed:", "33", use_color))
        for key, (old, new) in sorted(diff.changed.items()):
            lines.append(f"  ~ {key}: {old!r} -> {new!r}")

    summary_parts = []
    if diff.added:
        summary_parts.append(_color(f"{len(diff.added)} added", "32", use_color))
    if diff.removed:
        summary_parts.append(_color(f"{len(diff.removed)} removed", "31", use_color))
    if diff.changed:
        summary_parts.append(_color(f"{len(diff.changed)} changed", "33", use_color))

    lines.append("")
    lines.append("Summary: " + ", ".join(summary_parts))
    return "\n".join(lines)


def print_snapshot_diff(
    diff: SnapshotDiff,
    old: Snapshot,
    new: Snapshot,
    use_color: bool = True,
) -> None:
    print(f"Snapshot diff: {old.timestamp} -> {new.timestamp}")
    print(f"Sources: {old.source!r} -> {new.source!r}")
    print()
    print(format_snapshot_diff(diff, use_color=use_color))
