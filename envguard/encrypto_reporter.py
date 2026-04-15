"""Reporter for encryption check results."""
from __future__ import annotations

from typing import List

from .encrypto import EncryptionReport, EncryptionEntry


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def _status_label(entry: EncryptionEntry, use_color: bool) -> str:
    if entry.looks_encrypted:
        return _color("ENCRYPTED", "32", use_color)
    if entry.is_sensitive:
        return _color("PLAINTEXT!", "31", use_color)
    return _color("plaintext", "37", use_color)


def format_encryption_report(report: EncryptionReport, use_color: bool = True) -> str:
    lines: List[str] = []
    header = _color("Encryption Check Report", "1", use_color)
    lines.append(header)
    lines.append("-" * 40)

    if not report.entries:
        lines.append("No variables found.")
        return "\n".join(lines)

    for entry in report.entries:
        label = _status_label(entry, use_color)
        sensitive_flag = " [sensitive]" if entry.is_sensitive else ""
        lines.append(f"  {entry.key:<30} {label}  ({entry.reason}){sensitive_flag}")

    lines.append("")
    total = report.total()
    enc = report.encrypted_count()
    plain_sensitive = report.plaintext_sensitive_count()
    lines.append(f"Total: {total}  Encrypted: {enc}  Plaintext-sensitive: {plain_sensitive}")

    if plain_sensitive > 0:
        warn = _color(
            f"WARNING: {plain_sensitive} sensitive variable(s) appear to be stored in plaintext.",
            "33",
            use_color,
        )
        lines.append(warn)

    return "\n".join(lines)


def print_encryption_report(report: EncryptionReport, use_color: bool = True) -> None:
    print(format_encryption_report(report, use_color=use_color))
