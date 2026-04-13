"""Redact sensitive variable values in env output."""
from dataclasses import dataclass, field
from typing import Dict, List

_SECRET_KEYWORDS = ("secret", "password", "passwd", "token", "key", "api_key", "private", "credential", "auth")
_REDACTED = "***REDACTED***"


@dataclass
class RedactionReport:
    original: Dict[str, str] = field(default_factory=dict)
    redacted: Dict[str, str] = field(default_factory=dict)
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redaction_count(self) -> int:
        return len(self.redacted_keys)


def _is_sensitive(name: str) -> bool:
    """Return True if the variable name looks like it holds sensitive data."""
    lower = name.lower()
    return any(keyword in lower for keyword in _SECRET_KEYWORDS)


def redact_env(env: Dict[str, str], extra_keys: List[str] = None) -> RedactionReport:
    """Return a RedactionReport with sensitive values replaced.

    Args:
        env: Mapping of variable names to values.
        extra_keys: Additional keys to redact regardless of name.
    """
    extra = set(k.upper() for k in (extra_keys or []))
    report = RedactionReport(original=dict(env))

    for key, value in env.items():
        if _is_sensitive(key) or key.upper() in extra:
            report.redacted[key] = _REDACTED
            report.redacted_keys.append(key)
        else:
            report.redacted[key] = value

    return report
