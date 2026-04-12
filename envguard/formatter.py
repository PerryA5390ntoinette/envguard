"""Formats .env files by sorting, deduplicating, and normalizing entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from envguard.loader import parse_env_line


@dataclass
class FormatResult:
    """Result of formatting an .env file."""

    original_lines: List[str] = field(default_factory=list)
    formatted_lines: List[str] = field(default_factory=list)
    duplicates_removed: List[str] = field(default_factory=list)
    changed: bool = False

    def diff_summary(self) -> str:
        lines = []
        if self.duplicates_removed:
            lines.append(
                f"Removed {len(self.duplicates_removed)} duplicate(s): "
                + ", ".join(self.duplicates_removed)
            )
        if self.changed:
            lines.append("File has formatting changes.")
        else:
            lines.append("File is already well-formatted.")
        return "\n".join(lines)


def _normalize_line(line: str) -> str:
    """Strip trailing whitespace and normalize spacing around '='."""
    stripped = line.rstrip()
    if "=" in stripped and not stripped.startswith("#"):
        key, _, value = stripped.partition("=")
        return f"{key.strip()}={value.strip()}"
    return stripped


def format_env_content(
    content: str,
    sort_keys: bool = False,
    remove_duplicates: bool = True,
) -> FormatResult:
    """Format raw .env file content.

    Args:
        content: Raw text content of the .env file.
        sort_keys: Whether to sort variable declarations alphabetically.
        remove_duplicates: Whether to remove duplicate keys (keeps last occurrence).

    Returns:
        A FormatResult describing the changes made.
    """
    original_lines = content.splitlines()
    result = FormatResult(original_lines=original_lines)

    normalized: List[str] = [_normalize_line(ln) for ln in original_lines]

    if remove_duplicates:
        seen: dict = {}
        for idx, line in enumerate(normalized):
            parsed = parse_env_line(line)
            if parsed is not None:
                key, _ = parsed
                if key in seen:
                    result.duplicates_removed.append(key)
                seen[key] = idx

        deduped: List[str] = []
        skip_keys: set = set()
        # Walk in reverse to keep last occurrence
        key_last_index: dict = {}
        for idx, line in enumerate(normalized):
            parsed = parse_env_line(line)
            if parsed is not None:
                key_last_index[parsed[0]] = idx

        for idx, line in enumerate(normalized):
            parsed = parse_env_line(line)
            if parsed is not None and key_last_index.get(parsed[0]) != idx:
                continue
            deduped.append(line)
        normalized = deduped

    if sort_keys:
        comment_blocks: List[Tuple[Optional[str], str]] = []
        for line in normalized:
            parsed = parse_env_line(line)
            key = parsed[0] if parsed else None
            comment_blocks.append((key, line))
        comment_blocks.sort(key=lambda t: (t[0] is None, t[0] or ""))
        normalized = [ln for _, ln in comment_blocks]

    result.formatted_lines = normalized
    result.changed = normalized != [_normalize_line(ln) for ln in original_lines]
    return result
