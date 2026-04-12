"""Profile .env files to summarize variable statistics and patterns."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class VariableProfile:
    name: str
    value_length: int
    is_empty: bool
    has_special_chars: bool
    looks_like_url: bool
    looks_like_secret: bool


@dataclass
class ProfileReport:
    total: int = 0
    empty_count: int = 0
    secret_like_count: int = 0
    url_like_count: int = 0
    profiles: List[VariableProfile] = field(default_factory=list)
    category_counts: Dict[str, int] = field(default_factory=dict)


_SECRET_KEYWORDS = ("secret", "password", "passwd", "token", "key", "api_key", "auth")
_URL_PREFIXES = ("http://", "https://", "ftp://", "postgres://", "mysql://", "redis://")
_SPECIAL_CHARS = set("!@#$%^&*()[]{}|;:,.<>?/\\")


def _profile_variable(name: str, value: str) -> VariableProfile:
    lower_name = name.lower()
    looks_like_secret = any(kw in lower_name for kw in _SECRET_KEYWORDS)
    looks_like_url = any(value.startswith(pfx) for pfx in _URL_PREFIXES)
    has_special = bool(set(value) & _SPECIAL_CHARS)
    return VariableProfile(
        name=name,
        value_length=len(value),
        is_empty=value == "",
        has_special_chars=has_special,
        looks_like_url=looks_like_url,
        looks_like_secret=looks_like_secret,
    )


def _categorize(profile: VariableProfile) -> str:
    if profile.looks_like_url:
        return "url"
    if profile.looks_like_secret:
        return "secret"
    if profile.is_empty:
        return "empty"
    return "general"


def profile_env(env: Dict[str, str]) -> ProfileReport:
    """Build a ProfileReport from a parsed env dictionary."""
    report = ProfileReport()
    for name, value in env.items():
        vp = _profile_variable(name, value)
        report.profiles.append(vp)
        report.total += 1
        if vp.is_empty:
            report.empty_count += 1
        if vp.looks_like_secret:
            report.secret_like_count += 1
        if vp.looks_like_url:
            report.url_like_count += 1
        category = _categorize(vp)
        report.category_counts[category] = report.category_counts.get(category, 0) + 1
    return report
