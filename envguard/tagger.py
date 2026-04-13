"""Tag environment variables by category based on name patterns."""

from dataclasses import dataclass, field
from typing import Dict, List, Set

_TAG_PATTERNS: Dict[str, List[str]] = {
    "secret": ["password", "passwd", "secret", "token", "key", "api_key", "private"],
    "database": ["db", "database", "postgres", "mysql", "mongo", "redis", "dsn"],
    "network": ["host", "port", "url", "uri", "endpoint", "address", "ip"],
    "feature_flag": ["enable", "disable", "flag", "feature", "toggle"],
    "logging": ["log", "logger", "logging", "loglevel", "log_level"],
    "auth": ["auth", "jwt", "oauth", "session", "cookie"],
}


@dataclass
class TagEntry:
    name: str
    value: str
    tags: Set[str] = field(default_factory=set)


@dataclass
class TagReport:
    entries: List[TagEntry] = field(default_factory=list)
    tag_index: Dict[str, List[str]] = field(default_factory=dict)

    def by_tag(self, tag: str) -> List[TagEntry]:
        """Return all entries that have the given tag."""
        return [e for e in self.entries if tag in e.tags]

    def all_tags(self) -> Set[str]:
        """Return the set of all tags present in this report."""
        result: Set[str] = set()
        for entry in self.entries:
            result.update(entry.tags)
        return result


def _tags_for_name(name: str) -> Set[str]:
    """Determine which tags apply to a variable name."""
    lower = name.lower()
    tags: Set[str] = set()
    for tag, patterns in _TAG_PATTERNS.items():
        if any(pat in lower for pat in patterns):
            tags.add(tag)
    return tags


def tag_env(env: Dict[str, str]) -> TagReport:
    """Tag all variables in *env* and return a TagReport."""
    report = TagReport()
    for name, value in env.items():
        tags = _tags_for_name(name)
        entry = TagEntry(name=name, value=value, tags=tags)
        report.entries.append(entry)
        for tag in tags:
            report.tag_index.setdefault(tag, []).append(name)
    return report
