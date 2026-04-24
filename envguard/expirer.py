"""expirer.py — Detects env variables that may have expired based on age hints in comments or naming conventions."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import re

_DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")
_EXPIRY_KEYS = re.compile(r"(expir|ttl|until|expires|timeout|deadline)", re.IGNORECASE)


@dataclass
class ExpiryEntry:
    key: str
    value: str
    detected_date: Optional[str]
    is_expired: bool
    reason: str


@dataclass
class ExpiryReport:
    entries: List[ExpiryEntry] = field(default_factory=list)

    def add(self, entry: ExpiryEntry) -> None:
        self.entries.append(entry)

    @property
    def expired_count(self) -> int:
        return sum(1 for e in self.entries if e.is_expired)

    @property
    def ok_count(self) -> int:
        return sum(1 for e in self.entries if not e.is_expired)

    @property
    def has_expired(self) -> bool:
        return self.expired_count > 0


def _extract_date(value: str) -> Optional[str]:
    """Return the first ISO date string found in value, or None."""
    m = _DATE_PATTERN.search(value)
    return m.group(1) if m else None


def _is_past(date_str: str) -> bool:
    """Return True if the parsed date is before today (UTC)."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt < datetime.now(timezone.utc)
    except ValueError:
        return False


def check_expiry(env: Dict[str, str]) -> ExpiryReport:
    """Inspect each variable for expiry hints and return an ExpiryReport."""
    report = ExpiryReport()

    for key, value in env.items():
        detected = _extract_date(value)
        key_looks_temporal = bool(_EXPIRY_KEYS.search(key))

        if detected:
            expired = _is_past(detected)
            reason = (
                f"Value contains date {detected} which is in the past."
                if expired
                else f"Value contains date {detected} which is still valid."
            )
            report.add(ExpiryEntry(key=key, value=value, detected_date=detected,
                                   is_expired=expired, reason=reason))
        elif key_looks_temporal:
            report.add(ExpiryEntry(key=key, value=value, detected_date=None,
                                   is_expired=False,
                                   reason="Key name suggests a time-bound value; no date detected."))

    return report
