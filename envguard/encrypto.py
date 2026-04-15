"""Encryption status checker for .env variable values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# Patterns that suggest a value might be base64 or encrypted
import re

_BASE64_RE = re.compile(r'^[A-Za-z0-9+/]{16,}={0,2}$')
_HEX_RE = re.compile(r'^[0-9a-fA-F]{32,}$')
_ENC_PREFIX_RE = re.compile(r'^(enc:|ENC:|\{cipher\}|vault:)', re.IGNORECASE)


@dataclass
class EncryptionEntry:
    key: str
    value: str
    is_sensitive: bool
    looks_encrypted: bool
    reason: str


@dataclass
class EncryptionReport:
    entries: List[EncryptionEntry] = field(default_factory=list)

    def encrypted_count(self) -> int:
        return sum(1 for e in self.entries if e.looks_encrypted)

    def plaintext_sensitive_count(self) -> int:
        return sum(1 for e in self.entries if e.is_sensitive and not e.looks_encrypted)

    def total(self) -> int:
        return len(self.entries)


_SENSITIVE_KEYWORDS = ("password", "secret", "token", "key", "api", "auth", "private")


def _is_sensitive(name: str) -> bool:
    lower = name.lower()
    return any(kw in lower for kw in _SENSITIVE_KEYWORDS)


def _looks_encrypted(value: str) -> tuple[bool, str]:
    if not value:
        return False, "empty value"
    if _ENC_PREFIX_RE.match(value):
        return True, "encrypted prefix detected"
    if _HEX_RE.match(value):
        return True, "hex-encoded value"
    if _BASE64_RE.match(value) and len(value) >= 24:
        return True, "base64-encoded value"
    return False, "plaintext"


def check_encryption(env: Dict[str, str]) -> EncryptionReport:
    """Analyse each variable and report whether sensitive values appear encrypted."""
    report = EncryptionReport()
    for key, value in env.items():
        sensitive = _is_sensitive(key)
        encrypted, reason = _looks_encrypted(value)
        report.entries.append(
            EncryptionEntry(
                key=key,
                value=value,
                is_sensitive=sensitive,
                looks_encrypted=encrypted,
                reason=reason,
            )
        )
    return report
